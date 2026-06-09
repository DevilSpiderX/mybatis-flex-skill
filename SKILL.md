---
name: mybatis-flex-skill
description: >-
  MyBatis-Flex 开发技能。仅当后端项目明确使用 MyBatis-Flex 依赖或语法时激活，
  例如 com.mybatisflex 依赖、mybatis-flex.config、MyBatisFlexCustomizer、
  TableDef、QueryChain、UpdateChain、DbChain、UpdateEntity、Db + Row、
  MyBatis-Flex 注解、APT 代码生成、逻辑删除、乐观锁、多租户、数据权限等
  MyBatis-Flex 能力。若项目使用 MyBatis-Plus、原生 MyBatis、JPA 或其他 ORM，
  且没有 MyBatis-Flex 依赖或语法证据，不要激活本技能。
---

# MyBatis-Flex 开发技能

## 工作方式

1. 先确认项目存在 MyBatis-Flex 证据：`com.mybatisflex` 依赖、`mybatis-flex.config`、`MyBatisFlexCustomizer`、`QueryChain`、
   `UpdateChain`、`DbChain`、`UpdateEntity`、`TableDef` 或 `com.mybatisflex.*` 导入。
2. 如果只看到 `com.baomidou.mybatisplus`、MyBatis-Plus 的 `LambdaQueryWrapper` / `ServiceImpl`，或原生 MyBatis 的
   `SqlSession` / XML Mapper，不使用本技能。
3. 确认是 MyBatis-Flex 后，再识别任务主题，只读取对应 reference；不要一次性加载全部文档。
4. 优先复用项目既有 Mapper、Service、DTO、异常、事务和权限模式。
5. 默认优先链式操作：查询用 `QueryChain` / `QueryWrapper`，更新用 `UpdateChain`，无实体或通用 SQL 再考虑 `Db + Row`。
6. 涉及 API、DTO、SQL、数据库字段、权限、租户、事务、数据源、动态表名、审计、加密时，先梳理完整调用链和影响范围。
7. 保持最小、安全、可回滚修改；未明确要求不新增依赖、不迁移数据、不改变公共契约。

## 快速路由

按"遇到什么场景 → 看到什么代码信号 → 读哪个文件"匹配。如果任务涉及多个场景，按优先级依次读取对应文件。

### 一、项目初始化 & 代码生成

| 场景                                                | 代码信号 / 关键词                                                  | 读取                                   |
|---------------------------------------------------|-------------------------------------------------------------|--------------------------------------|
| 新建实体后缺少 TableDef 或 Mapper                         | 编译报错找不到 `AccountTableDef`，或 `mybatis-flex-processor` 相关配置   | `references/01-apt-configuration.md` |
| 不确定某个功能用哪个 reference 文件                           | 需要功能地图或官方文档入口                                               | `references/00-index.md`             |
| 项目还没有公共基类，需要统一 `id`/`createTime`/`updateTime` 等字段 | 无 `BaseEntity`，或需要 UUIDv7 主键、自动填充 `createUser`/`updateUser` | `references/08-base-entities.md`     |

### 二、实体定义 & 字段映射

| 场景                                               | 代码信号 / 关键词                                                                                                      | 读取                               |
|--------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|----------------------------------|
| 配置实体类注解：表名、主键策略、列映射、字段忽略、大字段                     | `@Table`、`@Id`、`@Column`、`@ColumnAlias`、`KeyType`、`isLarge`                                                     | `references/02-annotations.md`   |
| 定义实体间关联关系（一对一、一对多、多对多）                           | `@RelationOneToOne`、`@RelationOneToMany`、`@RelationManyToOne`、`@RelationManyToMany`                             | `references/02-annotations.md`   |
| 字段类型映射问题：枚举存库、JSON 列、日期格式、脱敏、大字段、自定义 TypeHandler | `@Column(typeHandler=...)`、`@EnumValue`、`JacksonTypeHandler`、`Fastjson2TypeHandler`、`MaskTypeHandler`、`isLarge` | `references/10-type-handling.md` |

### 三、查询

| 场景                                                                                  | 代码信号 / 关键词                                                                                                                                                                                  | 读取                                                                                          |
|-------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| 需要链式查询：按 ID 查、列表、分页、查单个字段、DTO/VO 转换                                                 | `QueryChain`、`.one()`、`.list()`、`.page()`、`.oneAs()`、`.listAs()`、`.pageAs()`、`.obj()`、`.count()`、`.exists()`                                                                                | `references/05-querychain.md`                                                               |
| 需要构建复杂 SQL：多表 JOIN、子查询、SQL 函数、CASE WHEN、GROUP BY/HAVING、UNION、CTE、EXISTS、FOR UPDATE | `QueryWrapper.create()`、`leftJoin`、`rightJoin`、`innerJoin`、`QueryMethods`（`count`/`max`/`sum`/`concat`/`year` 等）、`and(or)`、`with...asSelect`、`forUpdate()`、`distinct()`、`.when()`、`toSQL()` | `references/04-querywrapper-advanced.md`                                                    |
| 需要关联查询（带 Relations 的查询）                                                             | `selectOneWithRelationsById`、`withRelations`、`oneWithRelations()`、`listWithRelationsAs()`                                                                                                   | `references/05-querychain.md`（关联查询章节），如需 `@Relation` 注解写法则补读 `references/02-annotations.md` |
| 不需要实体类，直接用 SQL 或 Row 操作                                                             | `Db.selectOneById`、`Db.selectAllBySql`、`Db.selectListBySql`、`Row`                                                                                                                           | `references/09-service-mapper.md`（Db 工具类章节）                                                 |
| 需要查看源码解析总览、类继承关系图、或不确定看哪个 11x 子文件                                                   | 类继承关系、11a~11d 子文件索引                                                                                                                                                                         | `references/11-source-api.md`                                                               |
| 需要查看 `QueryMethods` 提供的 SQL 函数（数学/字符串/日期/聚合/CASE WHEN 等）                            | `QueryMethods.abs`、`QueryMethods.concat`、`QueryMethods.year`、`case_()`、`distinct()`                                                                                                         | `references/11a-source-api.md`                                                              |
| 不确定 `QueryWrapper` 或 `QueryChain` 有哪些可用方法                                           | 需要方法列表、参数签名                                                                                                                                                                                 | `references/11b-source-api.md`                                                              |
| 需要查看 `If` 工具类的条件判断方法                                                                | `If::notNull`、`If::hasText`、`If::notEmpty`、`If::isEmpty`                                                                                                                                    | `references/11d-source-api.md`                                                              |

### 四、新增 & 批量

| 场景                                        | 代码信号 / 关键词                                                                      | 读取                                                                                 |
|-------------------------------------------|---------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| 基础新增：`insert` vs `insertSelective` 的区别与选择 | `insert`、`insertSelective`、null 字段是否入库                                          | `references/03-basic-features.md`                                                  |
| 批量新增                                      | `insertBatch`、`insertBatchSelective`、`Db.executeBatch`、`Db.updateEntitiesBatch` | `references/03-basic-features.md`（批量章节），`references/09-service-mapper.md`（Db 批量章节） |
| 新增或更新（存在则更新）                              | `insertOrUpdate`                                                                | `references/09-service-mapper.md`                                                  |

### 五、更新 & 部分更新

| 场景                                                               | 代码信号 / 关键词                                                                                                 | 读取                                                                                                                                 |
|------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| 链式条件更新：有值才更新、动态 set、原子增减                                         | `UpdateChain`、`.set(field, value, If::hasText)`、`.set(field, value, If::notNull)`、`.setRaw()`（如 `age + 1`） | `references/06-updatechain.md`                                                                                                     |
| PATCH 语义：需要区分"字段未传"和"字段传了 null"三态                                | `OptionalField<T>`、`State.MISSING`/`NULL`/`VALUE`、DTO 中用 `OptionalField` 包装字段                              | 读 `references/12-optional-field.md`；需要理解源码实现或 `OptionalDtoUtil.toUpdateEntity()` 内部逻辑时补读 `references/12a-optional-field-source.md` |
| 按 ID 更新实体部分字段（不用 UpdateChain）                                    | `UpdateEntity.of(Account.class, id)`，然后 `mapper.updateByEntity()`                                          | `references/09-service-mapper.md`（UpdateEntity 章节）                                                                                 |
| 需要查看 `UpdateChain` / `PropertySetter` / `UpdateWrapper` 的完整方法和用法 | `set`、`setRaw`、`isEffective`、`Predicate<V>`、`BooleanSupplier`                                              | `references/11c-source-api.md`                                                                                                     |
| 需要查看 `If` 工具类的条件判断方法                                             | `If::notNull`、`If::hasText`、`If::notEmpty`、`If::isEmpty`                                                   | `references/11d-source-api.md`                                                                                                     |

### 六、删除

| 场景              | 代码信号 / 关键词                                             | 读取                                |
|-----------------|--------------------------------------------------------|-----------------------------------|
| 基础删除：按 ID、按条件   | `deleteById`、`deleteByQuery`                           | `references/03-basic-features.md` |
| 逻辑删除（软删除，不物理删除） | `@Column(isLogicDelete = true)`、`LogicDeleteProcessor` | `references/07-core-features.md`  |

### 七、Service & Mapper 分层

| 场景                                             | 代码信号 / 关键词                                                                                              | 读取                                |
|------------------------------------------------|---------------------------------------------------------------------------------------------------------|-----------------------------------|
| 不确定 Service 层怎么写：是否继承 IService、怎么注入 Mapper     | `Service` 类、`BaseMapper`、`mapper.queryChain()`                                                          | `references/09-service-mapper.md` |
| 需要查看 `BaseMapper` 的完整方法列表                      | `selectOneById`、`selectAll`、`selectListByQuery`、`selectListByQueryAs`、`paginate`、`selectCount`、`exists` | `references/09-service-mapper.md` |
| 需要分页查询：Page 对象、`paginate` 用法、`PageWithDetails` | `paginate`、`Page`、`PageWithDetails`                                                                     | `references/09-service-mapper.md` |
| 只查询部分字段、字段排除、字段重命名                             | `ALL_COLUMNS.except(...)`、`.as()`、`selectListByQueryAs`                                                 | `references/09-service-mapper.md` |

### 八、框架核心功能

| 场景                                           | 代码信号 / 关键词                                                                                 | 读取                                                                                   |
|----------------------------------------------|--------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| 乐观锁（版本号控制）                                   | `@Column(version = true)`、`@Version`                                                       | `references/07-core-features.md`                                                     |
| 多租户隔离                                        | `@Column(tenantId = true)`、`TenantManager`、`tenant_id` 字段                                  | `references/07-core-features.md`                                                     |
| 数据权限（行级权限过滤）                                 | `DataPermission`、行级过滤                                                                      | `references/07-core-features.md`                                                     |
| 字段加密/脱敏                                      | `SetListener`、`@Table(onSet)`、字段加解密                                                        | `references/07-core-features.md`                                                     |
| 数据填充：自动写入 createTime/updateTime/createUser 等 | `@OnInsert`、`@OnUpdate`、`@Table(onInsert/onUpdate)`、`@Column(onInsertValue/onUpdateValue)` | `references/07-core-features.md`（填充章节），如需项目级统一配置则补读 `references/08-base-entities.md` |
| 多数据源、读写分离、动态切换数据源                            | `DataSourceKey`、`@DS`、数据源 YAML 配置                                                          | `references/07-core-features.md`                                                     |
| 动态表名（运行时切换表名，如按月分表）                          | `TableManager.setDynamicTableProcessor`                                                    | `references/07-core-features.md`                                                     |
| SQL 审计、SQL 打印                                | SQL 日志、审计拦截器                                                                               | `references/07-core-features.md`                                                     |
| 编程式事务（不用 `@Transactional` 注解）                | `TransactionUtil.execute()`、`TransactionUtil.getTemplate()`、`Propagation.REQUIRES_NEW`     | `references/13-transaction-util.md`                                                  |

### 九、Spring Boot 配置

| 场景                                                       | 代码信号 / 关键词                                             | 读取                                      |
|----------------------------------------------------------|--------------------------------------------------------|-----------------------------------------|
| `application.yml` 中 MyBatis-Flex 数据源、mapper-locations 配置 | YAML 配置、`MybatisFlexCustomizer`                        | `references/03-basic-features.md`（配置章节） |
| APT 编译配置：Maven/Gradle 的 `annotationProcessorPaths`       | `mybatis-flex-processor`、`pom.xml` / `build.gradle` 配置 | `references/01-apt-configuration.md`    |

## 高优先级规则

- APT 生成的 `TableDef` 是类型安全查询首选；列引用优先 `ACCOUNT.AGE`，条件判断可用 `If::hasText` 等方法引用。
- `ServiceImpl` 默认不要继承 `IService`；除非既有项目已经统一使用 IService 风格，否则 Service 直接注入 Mapper。
- `UpdateChain.set` / `setRaw` 的第三个条件参数支持 `boolean`、`BooleanSupplier`、`Predicate<V>`。
- “有值才更新”优先：

```java
UpdateChain.of(Account.class)
        .set(ACCOUNT.USER_NAME, dto.getUserName(),If::hasText)
        .set(ACCOUNT.AGE, dto.getAge(),If::notNull)
        .where(ACCOUNT.ID.eq(id))
        .update();
```

- `If::hasText` 表示字符串有非空白文本才生效；`If::notNull` 适合对象、数字、日期，以及空字符串是合法值的字段；`If::notEmpty`
  适合集合、数组、Map；`If::noText` 是“为空时才生效”，不是“有值才更新”。
- 需要显式更新为 `null` 时，不要用普通 null 判空跳过；使用 `UpdateEntity` 或 `OptionalField` 区分“未传字段”和“传了 null”。
- `setRaw` 只用于数据库表达式、原子增减、函数或受控子查询；禁止拼接未校验用户输入。

## 常用导入

```java
import com.mybatisflex.core.query.If;
import com.mybatisflex.core.query.QueryWrapper;
import com.mybatisflex.core.query.QueryChain;
import com.mybatisflex.core.update.UpdateChain;
import com.mybatisflex.core.update.UpdateEntity;
import com.mybatisflex.core.row.Db;
import com.mybatisflex.core.row.DbChain;

import static com.example.entity.table.AccountTableDef.ACCOUNT;
```
