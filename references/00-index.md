# 官网功能地图

本文件用于对齐 MyBatis-Flex 官网侧边栏功能，避免技能只覆盖少量常用 API。处理相关任务时，先按主题读取对应 references 文件，不要一次性加载全部文档。

## 基础功能

| 官网主题 | 本技能参考文件 | 处理提示 |
|----------|----------------|----------|
| 增、删、改 | `03-basic-features.md`、`09-service-mapper.md`、`06-updatechain.md` | 区分 `insertSelective`、`update` 忽略 null、`UpdateEntity` 显式更新 null |
| 基础查询 | `03-basic-features.md`、`09-service-mapper.md` | 简单查询优先 `BaseMapper` 或 `QueryChain` |
| 自动映射 | `03-basic-features.md` | 多表同名列注意 `as` 映射和 VO/DTO 字段 |
| 关联查询 | `03-basic-features.md`、`02-annotations.md` | Relations 注解需要调用 `select***WithRelations` 或链式 withRelations 方法 |
| 批量操作 | `03-basic-features.md` | 大批量优先评估 `Db.executeBatch`，普通批量可用 Mapper/Service |
| 链式操作 | `05-querychain.md`、`06-updatechain.md` | 查询用 `QueryChain`，更新用 `UpdateChain` |
| QueryWrapper | `04-querywrapper-advanced.md`、`11-source-api.md` | 复杂 SQL、子查询、函数、动态条件 |
| Db + Row | `03-basic-features.md`、`09-service-mapper.md` | 无实体表、原生 SQL、通用 Row 场景 |
| Active Record | `03-basic-features.md` | Entity 继承 `Model`，仍需注入对应 `BaseMapper` |
| IService | `03-basic-features.md`、`09-service-mapper.md` | 本项目默认 Service 直接注入 Mapper，除非既有代码已采用 IService |
| SpringBoot 配置文件 | `03-basic-features.md` | 数据源、MyBatis-Flex 配置、SQL 打印等 |
| MyBatisFlexCustomizer | `03-basic-features.md`、`07-core-features.md` | 全局配置、主键生成、多租户、动态表名、审计、打印 |

## 核心功能

| 官网主题 | 本技能参考文件 | 处理提示 |
|----------|----------------|----------|
| @Table 注解 | `02-annotations.md`、`07-core-features.md` | 表名、schema、onInsert/onUpdate/onSet |
| @Id 注解 | `02-annotations.md` | 主键策略、复合主键、生成器 |
| @Column 注解 | `02-annotations.md`、`07-core-features.md` | 忽略字段、逻辑删除、乐观锁、租户、填充值 |
| 逻辑删除 | `07-core-features.md` | `@Column(isLogicDelete = true)` 或全局逻辑删除配置 |
| 乐观锁 | `07-core-features.md` | `@Column(version = true)`，更新时校验版本并递增 |
| 数据填充 | `07-core-features.md`、`08-base-entities.md` | Java 层 onInsert/onUpdate 与数据库层 onInsertValue/onUpdateValue 分开 |
| 数据脱敏 | `07-core-features.md` | 查询结果脱敏，不替代权限控制 |
| 数据缓存 | `07-core-features.md` | 关注缓存失效和更新一致性 |
| SQL 审计 | `07-core-features.md` | 用于拦截高风险 SQL 或记录审计 |
| SQL 打印 | `07-core-features.md` | 开发调试开启，生产环境谨慎 |
| 多数据源 | `07-core-features.md` | 配置 datasource key，必要时使用 `DataSourceKey` |
| 读写分离 | `07-core-features.md` | 基于多数据源和分片策略 |
| 数据源加密 | `07-core-features.md` | 配置解密器，不把密钥硬编码到业务代码 |
| 动态表名 | `07-core-features.md` | `TableManager.setDynamicTableProcessor` |
| 事务管理 | `13-transaction-util.md`、`07-core-features.md` | Spring 优先 `@Transactional` |
| 数据权限 | `07-core-features.md` | 优先统一方言或权限策略，不在 Controller 拼条件 |
| 字段权限 | `07-core-features.md` | `onSet` 可控制查询结果字段返回 |
| 字段加密 | `07-core-features.md` | `onSet` 示例是结果加密；入库加密需另行确认链路 |
| 字典回写 | `07-core-features.md` | `onSet` 回填展示字段，非数据库字段需 `@Column(ignore = true)` |
| 枚举属性 | `07-core-features.md`、`10-type-handling.md` | 使用 `@EnumValue` 保存枚举属性值 |
| 多租户 | `07-core-features.md` | `@Column(tenantId = true)` + `TenantManager` |

## 官方入口

- 快速开始：https://mybatis-flex.com/zh/intro/getting-started.html
- 增删改：https://mybatis-flex.com/zh/base/add-delete-update.html
- 链式操作：https://mybatis-flex.com/zh/base/chain.html
- QueryWrapper：https://mybatis-flex.com/zh/base/query-wrapper.html
- 自动映射：https://mybatis-flex.com/zh/base/auto-mapping.html
- 关联查询：https://mybatis-flex.com/zh/base/relations-query.html
- 批量操作：https://mybatis-flex.com/zh/base/batch.html
- Db + Row：https://mybatis-flex.com/zh/base/db-row.html
- Active Record：https://mybatis-flex.com/zh/base/active-record.html
- MyBatisFlexCustomizer：https://mybatis-flex.com/zh/base/mybatis-flex-customizer.html
