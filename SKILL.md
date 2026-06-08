---
name: mybatis-flex-skill
description: >-
  MyBatis-Flex 开发技能。当用户请求涉及 MyBatis-Flex 框架、MyBatis-Flex
  代码生成、Mapper/Service 持久层、QueryWrapper、QueryChain、UpdateChain、
  DbChain、UpdateEntity、部分字段更新、动态条件更新、字段判空后更新、
  CRUD、基础查询、自动映射、关联查询、批量操作、Db + Row、Active Record、
  IService、SpringBoot 配置、MyBatisFlexCustomizer、逻辑删除、乐观锁、
  数据填充、数据脱敏、数据缓存、SQL 审计、SQL 打印、多数据源、读写分离、
  数据源加密、动态表名、事务、数据权限、字段权限、字段加密、字典回写、
  枚举属性、多租户、注解映射、APT 配置、版本迁移、最佳实践咨询、
  代码检查、优化、重构、问题排查或代码解释时激活。
---

# MyBatis-Flex 开发技能

## 工作方式

1. 先识别任务主题，再只读取对应 reference；不要一次性加载全部文档。
2. 优先复用项目既有 Mapper、Service、DTO、异常、事务和权限模式。
3. 默认优先链式操作：查询用 `QueryChain` / `QueryWrapper`，更新用 `UpdateChain`，无实体或通用 SQL 再考虑 `Db + Row`。
4. 涉及 API、DTO、SQL、数据库字段、权限、租户、事务、数据源、动态表名、审计、加密时，先梳理完整调用链和影响范围。
5. 保持最小、安全、可回滚修改；未明确要求不新增依赖、不迁移数据、不改变公共契约。

## 快速路由

| 任务主题 | 优先读取 |
|----------|----------|
| 官网功能地图、选 reference | `references/00-index.md` |
| APT、TableDef、Mapper 生成 | `references/01-apt-configuration.md` |
| `@Table`、`@Id`、`@Column`、Relations 注解 | `references/02-annotations.md` |
| CRUD、基础查询、自动映射、关联、批量、Db + Row、Active Record、IService、配置 | `references/03-basic-features.md` |
| QueryWrapper、多表、子查询、SQL 函数、动态条件 | `references/04-querywrapper-advanced.md` |
| QueryChain 查询、分页、VO/DTO 映射查询 | `references/05-querychain.md` |
| UpdateChain、条件 `set`、`setRaw`、部分更新 | `references/06-updatechain.md` |
| 逻辑删除、乐观锁、填充、权限、多租户、动态表名、多数据源、审计 | `references/07-core-features.md` |
| BaseEntity、UUIDv7、自动填充基础配置 | `references/08-base-entities.md` |
| Service 与 Mapper 分层、常用 CRUD 封装 | `references/09-service-mapper.md` |
| 枚举、JSON、日期等类型处理 | `references/10-type-handling.md` |
| 源码级 API、完整方法列表 | `references/11-source-api.md` |
| PATCH/部分更新三态值 | `references/12-optional-field.md` |
| OptionalField 源码实现 | `references/12a-optional-field-source.md` |
| 编程式事务工具 | `references/13-transaction-util.md` |

## 高优先级规则

- APT 生成的 `TableDef` 是类型安全查询首选；列引用优先 `ACCOUNT.AGE`，条件判断可用 `If::hasText` 等方法引用。
- `ServiceImpl` 默认不要继承 `IService`；除非既有项目已经统一使用 IService 风格，否则 Service 直接注入 Mapper。
- `UpdateChain.set` / `setRaw` 的第三个条件参数支持 `boolean`、`BooleanSupplier`、`Predicate<V>`。
- “有值才更新”优先：

```java
UpdateChain.of(Account.class)
    .set(ACCOUNT.USER_NAME, dto.getUserName(), If::hasText)
    .set(ACCOUNT.AGE, dto.getAge(), If::notNull)
    .where(ACCOUNT.ID.eq(id))
    .update();
```

- `If::hasText` 表示字符串有非空白文本才生效；`If::notNull` 适合对象、数字、日期，以及空字符串是合法值的字段；`If::notEmpty` 适合集合、数组、Map；`If::noText` 是“为空时才生效”，不是“有值才更新”。
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
