# 实体差异比较工具 EntityDiffUtil（项目侧能力）

> 🚫 **非框架 API（项目侧能力）**：`EntityDiffUtil` 是项目侧自研工具
> （`com.sanyuan.business.platform.mybatisflex.util`），MyBatis-Flex 1.11.8 框架中不存在该类
> （全仓检索零命中）。它基于以下框架 API 实现：
> `TableInfo.getPropertyColumnMapping`（`mybatis-flex-core/.../table/TableInfo.java:161`）、
> `getValue`（`:907`）、`getVersionColumn`（`:244`）、`getQueryColumnByProperty`（`:1624`）、
> `UpdateChain.of(mapper)` 与 `set(QueryColumn, Object)`（`mybatis-flex-core/.../update/UpdateChain.java:51,100`）。
> 消费方项目若要用必须自带该类。

## 能力概览

两个静态方法：

- `diff(oldEntity, newEntity)`：字段级比较，返回 `List<DiffResult>`（数据库列、属性名、新值、旧值），
  无变化返回空列表。
- `diffUpdate(mapper, oldEntity, newEntity)`：基于 diff 生成**只含变化字段**的 `UpdateChain`，
  已附加主键 WHERE 条件和乐观锁版本条件，调用方直接 `.update()` 即可；无变化返回 `null`。

典型场景是编辑回显后的"整体覆盖式保存"：先查出旧实体，用新值构造新实体，自动算差集，
只 UPDATE 变化的列；`updateTime`/`updateUser` 等审计字段交给 08 的监听器，不参与 diff。

## 自动排除规则（不参与 diff 与更新）

- 主键（`@Id`）
- 乐观锁（`@Column(version = true)`）
- 逻辑删除（`@Column(isLogicDelete = true)`）
- 不可更新列（`@Column(updatable = false)`）
- 约定审计字段：`updateTime`、`updateUser`（由 `BaseEntityListener` 自动填充）
- 大字段（`isLarge`）**参与**比较，不排除

排除集合按实体类缓存（`ConcurrentHashMap`），不每次反射计算。`@Column(ignore = true)`
的非数据库字段本身不在 `propertyColumnMapping` 里，天然不参与。

## 完整源码（项目侧）

```java
package com.sanyuan.business.platform.mybatisflex.util;

import com.mybatisflex.annotation.Column;
import com.mybatisflex.annotation.Id;
import com.mybatisflex.core.BaseMapper;
import com.mybatisflex.core.query.QueryColumn;
import com.mybatisflex.core.query.QueryCondition;
import com.mybatisflex.core.table.TableInfo;
import com.mybatisflex.core.table.TableInfoFactory;
import com.mybatisflex.core.update.UpdateChain;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

import java.lang.reflect.Field;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 实体差异比较工具，支持两个同类实体的字段级 diff 和基于 diff 的增量更新。
 * <p>
 * 自动排除主键、乐观锁、逻辑删除、不可更新字段（{@code @Column(updatable = false)}）和监听器自动填充的审计字段（{@code updateTime}、{@code updateUser}）。
 * 大字段（{@code isLarge}）参与比较。
 *
 * @author DevilSpiderX
 */
@NullMarked
public final class EntityDiffUtil {

    private static final Set<String> CONVENTION_EXCLUDED_PROPERTIES = Set.of("updateTime", "updateUser");
    private static final ConcurrentHashMap<Class<?>, Set<String>> EXCLUDED_PROPERTIES_CACHE = new ConcurrentHashMap<>();

    private EntityDiffUtil() {
    }

    /**
     * 差异结果记录。
     *
     * @param column   数据库列
     * @param property 实体属性
     * @param newValue 新值
     * @param oldValue 旧值
     */
    public record DiffResult(
            QueryColumn column,
            String property,
            @Nullable Object newValue,
            @Nullable Object oldValue
    ) {
        @Override
        public QueryColumn column() {
            return column.clone();
        }
    }

    /**
     * 比较两个同类实体，返回发生变化的列及新值。
     *
     * @param oldEntity 旧实体，不允许为 null
     * @param newEntity 新实体，不允许为 null
     * @return 变化的列及新值（LinkedHashMap 保持遍历顺序），无变化时返回空 Map
     * @throws IllegalArgumentException 当两个实体不是同一类型时
     */
    public static <T> List<DiffResult> diff(final T oldEntity, final T newEntity) {
        Objects.requireNonNull(oldEntity, "oldEntity 不能为 null");
        Objects.requireNonNull(newEntity, "newEntity 不能为 null");

        final var entityClass = oldEntity.getClass();
        if (!entityClass.equals(newEntity.getClass())) {
            throw new IllegalArgumentException("两个实体必须是同一类型: %s vs %s".formatted(
                    entityClass.getSimpleName(), newEntity.getClass().getSimpleName()));
        }

        final var tableInfo = TableInfoFactory.ofEntityClass(entityClass);
        final var excluded = getExcludedProperties(entityClass);
        final var propertyColumnMapping = tableInfo.getPropertyColumnMapping();

        final List<DiffResult> changes = new ArrayList<>();
        for (final var entry : propertyColumnMapping.entrySet()) {
            final var property = entry.getKey();
            if (excluded.contains(property)) {
                continue;
            }
            final var oldVal = tableInfo.getValue(oldEntity, property);
            final var newVal = tableInfo.getValue(newEntity, property);
            if (!Objects.equals(oldVal, newVal)) {
                final var column = tableInfo.getQueryColumnByProperty(property);
                changes.add(new DiffResult(
                        column,
                        property,
                        newVal,
                        oldVal
                ));
            }
        }
        return changes;
    }

    /**
     * 比较两个同类实体，返回仅包含变化字段的 UpdateChain。
     * <p>
     * UpdateChain 已附加主键 WHERE 条件和乐观锁版本条件，调用方直接调用 {@code .update()} 即可。
     * 无变化时返回 null。
     *
     * @param mapper    BaseMapper 实例，不允许为 null
     * @param oldEntity 旧实体，不允许为 null
     * @param newEntity 新实体，不允许为 null
     * @return 仅含变化字段的 UpdateChain，无变化时返回 null
     */
    public static <T> @Nullable UpdateChain<T> diffUpdate(
            final BaseMapper<T> mapper,
            final T oldEntity,
            final T newEntity
    ) {
        Objects.requireNonNull(mapper, "mapper 不能为 null");

        final var changes = diff(oldEntity, newEntity);
        if (changes.isEmpty()) {
            return null;
        }

        final var tableInfo = TableInfoFactory.ofEntityClass(oldEntity.getClass());
        var chain = UpdateChain.of(mapper);
        for (final var one : changes) {
            chain = chain.set(one.column(), one.newValue());
        }

        final var whereCondition = buildWhereCondition(tableInfo, oldEntity);
        return chain.where(whereCondition);
    }

    private static QueryCondition buildWhereCondition(final TableInfo tableInfo, final Object entity) {
        final var columnToProperty = buildColumnToPropertyMap(tableInfo);

        QueryCondition condition = null;

        // 主键条件
        for (final var field : getAllFields(entity.getClass())) {
            if (field.getAnnotation(Id.class) == null) {
                continue;
            }
            final var property = field.getName();
            final var column = tableInfo.getQueryColumnByProperty(property);
            final var pkVal = tableInfo.getValue(entity, property);
            final var pkCondition = column.eq(pkVal);
            condition = (condition == null) ? pkCondition : condition.and(pkCondition);
        }

        // 乐观锁版本条件
        final var versionColumnName = tableInfo.getVersionColumn();
        if (versionColumnName != null) {
            final var versionProperty = columnToProperty.get(versionColumnName);
            if (versionProperty != null) {
                final var versionVal = tableInfo.getValue(entity, versionProperty);
                final var versionColumn = tableInfo.getQueryColumnByProperty(versionProperty);
                final var versionCondition = versionColumn.eq(versionVal);
                condition = (condition == null) ? versionCondition : condition.and(versionCondition);
            }
        }

        if (condition == null) {
            throw new IllegalArgumentException("实体 %s 没有主键，无法构建 WHERE 条件".formatted(
                    tableInfo.getEntityClass().getSimpleName()));
        }
        return condition;
    }

    private static Set<String> getExcludedProperties(final Class<?> entityClass) {
        return EXCLUDED_PROPERTIES_CACHE.computeIfAbsent(
                entityClass, cls -> {
                    final Set<String> excluded = new HashSet<>();

                    for (final var field : getAllFields(cls)) {
                        // 主键属性
                        if (field.getAnnotation(Id.class) != null) {
                            excluded.add(field.getName());
                        }
                        // @Column 注解：version、isLogicDelete、updatable = false
                        final var column = field.getAnnotation(Column.class);
                        if (column != null && (column.version() || column.isLogicDelete() || !column.updatable())) {
                            excluded.add(field.getName());
                        }
                    }

                    // 约定：监听器自动填充的审计字段
                    excluded.addAll(CONVENTION_EXCLUDED_PROPERTIES);

                    return excluded;
                }
        );
    }

    private static Map<String, String> buildColumnToPropertyMap(final TableInfo tableInfo) {
        final var reverse = new HashMap<String, String>();
        tableInfo.getPropertyColumnMapping().forEach((prop, col) -> reverse.put(col, prop));
        return reverse;
    }

    private static List<Field> getAllFields(final Class<?> clazz) {
        final var fields = new ArrayList<Field>();
        var current = clazz;
        while (current != null && current != Object.class) {
            fields.addAll(Arrays.asList(current.getDeclaredFields()));
            current = current.getSuperclass();
        }
        return fields;
    }
}
```

## 使用示例

```java
// 1. 只比较，拿变化清单（操作日志、变更记录）
Account oldEntity = accountMapper.selectOneById(id);
Account newEntity = buildFromDto(dto);   // 用前端提交值构造
List<EntityDiffUtil.DiffResult> changes = EntityDiffUtil.diff(oldEntity, newEntity);
changes.forEach(r -> log.info("{}: {} -> {}", r.property(), r.oldValue(), r.newValue()));

// 2. 增量更新：只写变化的列，自动带主键 WHERE + 乐观锁 WHERE
var chain = EntityDiffUtil.diffUpdate(accountMapper, oldEntity, newEntity);
if (chain == null) {
    return; // 无变化
}
if (!chain.update()) {
    // 影响行数为 0：version 不匹配（并发修改），按项目错误响应处理
    throw new BizException("数据已被他人修改");
}
```

## 与 UpdateEntity / OptionalField 的取舍

| 方案 | 适用场景 | 特点 |
|------|----------|------|
| `EntityDiffUtil.diffUpdate` | 编辑回显后整体保存（持有新旧两个实体） | 自动算差集，调用方不列举字段 |
| `UpdateEntity.of` + 手写 set | 明确知道改了哪些字段 | 直接声明，无反射比较开销 |
| `OptionalField`（见 [12-optional-field.md](12-optional-field.md)） | PATCH 三态（区分未传/null） | DTO 字段包装，前端契约驱动 |

三者都只生成变化字段的 UPDATE；`updateTime`/`updateUser` 统一由 08 的监听器填充，不要手工 set。

## 坑点

- **约定排除字段名硬编码**：`CONVENTION_EXCLUDED_PROPERTIES = Set.of("updateTime", "updateUser")`
  与 08 的 `BaseAllEntity` 字段名绑定；项目若改字段名必须同步改这个常量，否则审计字段会被
  diff 出来并参与更新。
- **`diffUpdate` 无变化返回 null**：不能直接链式 `.update()`，先判空。
- **乐观锁版本取 `oldEntity` 的值**：`newEntity` 的 version 必须是从库里查出来的原值；
  若前端回传篡改或丢失，WHERE 的 version 条件错误，会导致更新不到（表现为 `update()` 返回 false）。
- **无主键实体直接抛 `IllegalArgumentException`**（构建 WHERE 失败）。
- **`isLarge` 大字段参与比较**：旧实体若没查大字段（`DEFAULT_COLUMNS` 不含），旧值为 null，
  会把"未加载"误判为"被清空"并 UPDATE 覆盖。编辑回显场景要么查全字段，要么注意该字段的来源。
- **`Objects.equals` 语义**：`BigDecimal("1.0")` 与 `BigDecimal("1.00")` equals 为 false，
  会被判为变化；`Date`/`LocalDateTime`/枚举按 equals 比较没问题。涉及金额字段时留意。
- **set 不过滤 null**：diff 出来的 `newValue` 为 null 会把列显式更新为 NULL（与
  `UpdateEntity` 的"忽略 null"语义不同），这是设计行为——字段被改成 null 就应该落库。
- **两个实体必须同一类型**，否则抛 `IllegalArgumentException`；父子类混用会踩到。
- `DiffResult.column()` 返回 `column.clone()`，避免调用方改动内部 `QueryColumn` 状态。
- `diff` 每次调用都走 `TableInfo.getValue` 反射取值（排除集合有缓存、取值没有），
  大批量循环 diff 时注意性能。
