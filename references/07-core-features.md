# 官网核心功能用例补齐（源码级）

> 以下内容基于 MyBatis-Flex **1.11.8** 源码（`C:\Code\mybatis-flex`）逐文件求证，源码位置为仓库相对路径，如
> `mybatis-flex-core/src/main/java/com/mybatisflex/core/tenant/TenantManager.java:33`。
> 涉及权限、租户、数据源、SQL 审计、加密、动态表名时属于高风险变更，修改前先梳理调用链和影响范围。

## 全局配置速查

以下键位于 `mybatis-flex.global-config.*`（配置类 `MybatisFlexProperties`，`mybatis-flex-spring-boot-starter/src/main/java/com/mybatisflex/spring/boot/MybatisFlexProperties.java:54`）：

```yaml
mybatis-flex:
  global-config:
    normal-value-of-logic-delete: 0     # 逻辑删除正常值，默认 0
    deleted-value-of-logic-delete: 1    # 逻辑删除删除值，默认 1
    logic-delete-column: del_flag       # 全局逻辑删除列名（免注解）
    version-column: version             # 全局乐观锁列名（免注解）
    tenant-column: tenant_id            # 全局租户列名（免注解）
```

## 逻辑删除

**注解**：`@Column(isLogicDelete = true)`（`mybatis-flex-annotation/src/main/java/com/mybatisflex/annotation/Column.java:64`）。一张表只能有一个逻辑删除列，超过 1 个在实体解析期抛 `The logic delete column of entity[%s] must be less then 2.`（`mybatis-flex-core/src/main/java/com/mybatisflex/core/table/TableInfoFactory.java:394-401`）。

**处理器体系**：接口 `LogicDeleteProcessor`（`mybatis-flex-core/src/main/java/com/mybatisflex/core/logicdelete/LogicDeleteProcessor.java:25`）有 5 个方法：`buildLogicNormalCondition`、`buildLogicDeletedSet`、`buildQueryCondition`、`getLogicNormalValue`、`getLogicDeletedValue`。默认注册 `DefaultLogicDeleteProcessor`（`LogicDeleteManager.java:30`），取值来自 `FlexGlobalConfig` 的 `normalValueOfLogicDelete/deletedValueOfLogicDelete`（默认 0/1，`FlexConsts.java:59-63`）。

内置类型处理器**不会按字段类型自动匹配，必须显式注册**：

| 处理器 | 正常值 | 删除值 |
|---|---|---|
| `DefaultLogicDeleteProcessor` | 0（可配置） | 1（可配置） |
| `BooleanLogicDeleteProcessor` | false | true |
| `IntegerLogicDeleteProcessor` | 0 | 1 |
| `DateTimeLogicDeleteProcessor` | null（条件为 `IS NULL`） | 字符串 `"NOW()"` 直拼 SQL |
| `TimeStampLogicDeleteProcessor` | 0 | `System.currentTimeMillis()` |
| `PrimaryKeyLogicDeleteProcessor` | null | 主键列的值（`SET is_delete = id`） |

```java
// 全局注册（Spring Boot 下暴露 @Bean LogicDeleteProcessor 亦可，自动配置会调用 setProcessor）
LogicDeleteManager.setProcessor(new BooleanLogicDeleteProcessor());

// 跳过逻辑删除，直接物理 DELETE
LogicDeleteManager.execWithoutLogicDelete(() -> accountMapper.deleteById(1));
```

**SQL 改写与查询过滤**：`deleteById/deleteBatchByIds/deleteByQuery` 统一改写为 UPDATE（`mybatis-flex-core/src/main/java/com/mybatisflex/core/dialect/impl/CommonsDialectImpl.java:709-740` by id、`744-803` batch、`806+` by query）：

```sql
UPDATE `tb_account` SET `is_delete` = 1 WHERE `id` = ? AND `is_delete` = 0
```

查询时 `TableInfo.appendConditions` 自动附加 `is_delete = 0`（`mybatis-flex-core/src/main/java/com/mybatisflex/core/table/TableInfo.java:1033-1045`），`selectOneBy**/selectListBy**/selectCountBy**/paginate` 及 left join 的子表均会附加。insert 时逻辑删除字段为 null 会自动初始化为正常值（`TableInfo.java:1561-1577`）。

坑点：

- 处理器是 JVM 级静态单例，多张表无法分别配置不同类型。
- `DateTimeLogicDeleteProcessor` 删除值是字符串 `"NOW()"` 直拼，换 Oracle 等无 `now()` 的库必须自定义处理器。
- 自定义字符串值（如 `"Y"/"N"`）走字符串拼接进 SQL，注意注入风险。
- 已逻辑删除的数据更新不到（update 的 WHERE 同样带 `is_delete = 0`，`CommonsDialectImpl.java:885-889`）。

## 乐观锁

**注解**：`@Column(version = true)`（`Column.java:72`），仅支持数值字段。同表多个 version 字段启动即抛 `The version column of entity[%s] must be less then 2.`（`TableInfoFactory.java:404-411`）。也可不写注解，用全局列名 `FlexGlobalConfig.getDefaultConfig().setVersionColumn("version")`（`FlexGlobalConfig.java:323`）。

**SQL 行为**（`CommonsDialectImpl.java:869-903`，updateByQuery 同理见 `944-947`）：

```sql
UPDATE tb_account SET nickname = ?, version = version + 1
WHERE id = ? AND is_delete = 0 AND version = ?
```

```java
Account a = mapper.selectOneById(1);
a.setNickname("x");
mapper.update(a); // 必须携带查出来的 version
```

- 插入时 version 为 null 自动置 0（`TableInfo.initVersionValueIfNecessary`，`TableInfo.java:1509-1521`；调用点 `EntitySqlProvider.java:62`）。
- 更新时实体 version 为 null 抛 `FlexExceptions(ENTITY_VERSION_NULL)`：`The version value of entity "{0}" must not be null.`（`mybatis-flex-core/src/main/java/com/mybatisflex/core/exception/locale/LocalizedFormats.java:52`）。
- **version 不匹配时源码中未提供异常机制**：影响行数为 0，`update` 返回 false，需业务自行判断。
- 跳过：`OptimisticLockManager.execWithoutOptimisticLock(() -> ...)`（`mybatis-flex-core/src/main/java/com/mybatisflex/core/optimisticlock/OptimisticLockManager.java:33-52`）。

坑点：

- `UpdateEntity.of(Account.class, id)` 局部更新忘 set version 会直接抛 ENTITY_VERSION_NULL。
- 并发失败只返回 false，不抛异常、不自动重试。
- 乐观锁条件附加在逻辑删除条件之后，已删除数据同样更新不到。

## 数据填充

两种机制：

- **应用层（Java 监听器）**：`@Table(onInsert = XxxListener.class)` / `onUpdate` / `onSet`（`mybatis-flex-annotation/src/main/java/com/mybatisflex/annotation/Table.java:58-68`）。接口 `InsertListener.onInsert(Object)`（`mybatis-flex-annotation/src/main/java/com/mybatisflex/annotation/InsertListener.java:31`）、`UpdateListener`、`SetListener`；可按泛型继承 `AbstractInsertListener<T>`（`AbstractInsertListener.java:29-59`）。
- **数据库层（SQL 片段）**：`@Column(onInsertValue = "now()")` / `onUpdateValue`（`Column.java:47-52`）。

**执行链路**：`EntitySqlProvider.insert` 构建 SQL 时调用 `tableInfo.invokeOnInsertListener(entity)`（`mybatis-flex-core/src/main/java/com/mybatisflex/core/provider/EntitySqlProvider.java:71`；update 在 `236`，`RowSqlProvider.java:256` 同理）。`TableInfo.invokeOnInsertListener` 合并 @Table 注解监听器与全局监听器后逐个执行（`TableInfo.java:1582-1595`）。`onInsertValue/onUpdateValue` 由 `TableInfoFactory` 收集为 column→SQL 字符串（`TableInfoFactory.java:424-431`），insert 时值位**直拼**该字符串（`CommonsDialectImpl.java:627-628`），update 时**无条件**追加 `SET col = 值`（`CommonsDialectImpl.java:864-867`）。

```java
@Table(value = "tb_article", onInsert = ArticleInsertListener.class)
public class Article {
    @Id private Long id;
    private String title;
    @Column(onInsertValue = "now()") private Date created;
    @Column(onUpdateValue = "now()") private Date updated;
}

// 全局注册（无 yml 入口，只能代码或 @Bean）
FlexGlobalConfig.getDefaultConfig()
    .registerInsertListener(new ArticleInsertListener(), Article.class);
```

`UpdateEntity.of(Class)` 返回"仅记录被修改属性"的代理对象（`mybatis-flex-core/src/main/java/com/mybatisflex/core/util/UpdateEntity.java:34-37`），本身不含监听逻辑；经 `mapper.update(entity)` 时仍会触发 onUpdate 监听器和 onUpdateValue 拼接，与普通实体走同一 provider 链路。

坑点：

- `onInsertValue/onUpdateValue` 是字符串直拼 SQL（非占位符），切勿拼接用户输入。
- update 时 `onUpdateValue` 列无条件进 SET，实体没 set 也会拼。
- insert 用 `ignoreNulls=true` 且字段为 null 时该列不进 insertColumns，`onInsertValue` 不生效。
- @Table 注解监听器与全局监听器都会执行（merge），重复注册会执行多次；监听器在 SQL 构建期同步执行，抛异常会中断整个 SQL 构建。

## 数据脱敏

**注意：`@Column` 没有 `mask` 属性**。启用脱敏用独立注解 `@ColumnMask`（`mybatis-flex-annotation/src/main/java/com/mybatisflex/annotation/ColumnMask.java:26`，只有一个 `value()` 填规则名）：

```java
@Table("tb_account")
public class Account {
    @ColumnMask(Masks.CHINESE_NAME)   // 张三丰 -> 张**
    private String userName;
}
```

- `Masks`（`mybatis-flex-core/src/main/java/com/mybatisflex/core/mask/Masks.java`）内置 9 个规则常量：`MOBILE`(:29)、`FIXED_PHONE`(:34)、`ID_CARD_NUMBER`(:39)、`CHINESE_NAME`(:44)、`ADDRESS`(:49)、`EMAIL`(:54)、`PASSWORD`(:59)、`CAR_LICENSE`(:64)、`BANK_CARD_NUMBER`(:69)。
- `MaskTypeHandler(String maskType)`（`MaskTypeHandler.java:30`）：**构造参数是规则名（MaskManager 注册的 key），不是"前后保留位数/掩码字符"**；保留位数和掩码字符（固定 `*`）写死在 `Masks` 的私有 `mask(s, keepFirst, keepLast, maskCount)` 里（`Masks.java:81`）。
- `CompositeMaskTypeHandler(String maskType, TypeHandler<Object> typeHandler)`（`CompositeMaskTypeHandler.java:31`）：字段同时配了 `typeHandler` 时先转类型再脱敏（`ColumnInfo.java:157-163`）。
- `MaskManager`：`registerMaskProcessor(type, processor)`(:58)、`execWithoutMask(Supplier/Runnable)`(:69/:81)、`skipMask()`(:93)、`restoreMask()`(:101)，自定义规则实现 `MaskProcessor.mask(Object)`（`MaskProcessor.java:23`）。

```java
// 自定义规则
MaskManager.registerMaskProcessor("mobile_tail4",
    data -> data instanceof String s && s.length() == 11
        ? s.substring(0, 7) + "****" : data);

// 编辑回显：必须取原始值，否则会把脱敏值保存回库
Account raw = MaskManager.execWithoutMask(() -> mapper.selectOneById(1L));
```

坑点：

- **只读脱敏、写不脱敏**：`MaskTypeHandler.setNonNullParameter` 原样 `ps.setString`（`MaskTypeHandler.java:35`），三个 `getNullableResult` 才调 `MaskManager.mask`（:41/:47/:53）。把查询到的脱敏值回填表单再保存，就会把 `张**` 写进数据库。
- `@ColumnMask` **只支持 String 字段**，非 String 启动期直接抛 `IllegalStateException`（`TableInfoFactory.java:517-518`）。
- 规则名未注册时 `MaskManager.mask` 抛 `IllegalStateException`（`MaskManager.java:113-114`），启动即炸，不是静默跳过。
- `skipMask/restoreMask` 基于 ThreadLocal，`skip()` 后必须 `restore()`，建议统一放拦截器成对调用；漏恢复会让后续请求全部拿到明文。
- 与 `SetListener` 方案的区别：脱敏是框架在结果映射层无条件执行、与调用方权限无关；`SetListener` 业务可控（可按当前用户决定是否返回原文）。

## 数据缓存

**官方源码未提供缓存能力**（core 中无 `CacheManager`/`@Cache` 之类组件，cache 相关类均为 MyBatis 内部机制，如 `CacheKeyBuilder`、结果集 handler 的 localCache）。需要缓存时用 MyBatis 二级缓存（`@Options(useCache = true)`，注意与逻辑删除/租户条件组合时的缓存键）或应用层 Caffeine/Redis，写操作频繁的表不要仅为减少查询代码而启用。

## SQL 审计

**application.yml 里没有审计开关**（`MybatisFlexProperties` 无 audit 字段），只能代码开启：

```java
AuditManager.setAuditEnable(true);
AuditManager.setMessageCollector(new ConsoleMessageCollector()); // 实时打印，可选
// 或自定义上报：AuditManager.setMessageReporter(new MyMessageReporter());
```

- 默认关闭 `auditEnable=false`；默认收集器是 `ScheduledMessageCollector`（每 10s 经 `ConsoleMessageReporter` 上报）（`mybatis-flex-core/src/main/java/com/mybatisflex/core/audit/AuditManager.java:48,50`、`ScheduledMessageCollector.java:30,41`）。
- 注册自定义收集器：`setMessageCollector(MessageCollector)`（接口仅 `void collect(AuditMessage)`）；自定义上报：`setMessageReporter(MessageReporter)`（内部包一层 10s 的 ScheduledMessageCollector）（`AuditManager.java:81,86`）。
- 内置实现——收集器：`ConsoleMessageCollector`（实时）、`ScheduledMessageCollector`、`CountableMessageCollector`（满 count 触发）；Reporter：`ConsoleMessageReporter`、`HttpMessageReporter`。
- `AuditMessage` 可拿到：`query`(SQL)、`queryParams`、`elapsedTime`(耗时ms)、`queryTime`、`queryCount`、`stmtId`、`dsName`、`hostIp` 及 metas；`getFullSql()` 会把参数回填成可执行 SQL（`AuditMessage.java:76,221`）。采集点在 `FlexStatementHandler.query/update/batch`（`mybatis-flex-core/src/main/java/com/mybatisflex/core/mybatis/FlexStatementHandler.java:96`）。

坑点：

- `FlexStatementHandler` 在构造时缓存 `auditEnable`，**必须在执行 SQL 前（建议启动时）设置**，运行中改不生效（`FlexStatementHandler.java:47`）。
- 默认 10s 批量、非实时，排查即时问题用 `ConsoleMessageCollector`。
- `MessageFactory.create()` 返回 null 时该条 SQL 直接跳过审计（`AuditManager.java:102`）。

## SQL 打印

两种官方方式：

A. MyBatis-Flex 自带（走审计，输出完整可执行 SQL + 耗时）：

```java
AuditManager.setAuditEnable(true);
AuditManager.setMessageCollector(new ConsoleMessageCollector());
```

B. MyBatis 原生日志（打印带 `?` 占位符的 SQL + 参数列表）：

```yaml
mybatis-flex:
  configuration:
    log-impl: org.apache.ibatis.logging.StdOutImpl   # 或 Slf4jImpl 等
```

`log-impl` 类型为 `Class<? extends org.apache.ibatis.logging.Log>`（`MybatisFlexProperties.java:453,759`），可选值为 MyBatis 的 `Log` 实现全类名：`StdOutImpl`、`Slf4jImpl`、`Log4j2Impl`、`CommonsLoggingImpl`、`Jdk14LoggingImpl`、`NoLoggingImpl`。坑点：只写实现名（如 `StdOutImpl`）会因类找不到报错；要"一条完整 SQL + 耗时"须用方式 A。

## 多数据源

注解是 **`@UseDataSource`**（不是 `@DS`），只有一个属性 `value()`，即数据源 key（`mybatis-flex-annotation/src/main/java/com/mybatisflex/annotation/UseDataSource.java:31`）：

```yaml
mybatis-flex:
  default-datasource-key: master        # 默认数据源 key，必填且必须存在于下面
  datasource:
    master:
      type: druid                        # 别名 druid/hikari/dbcp2... 或写全类名
      url: jdbc:mysql://127.0.0.1:3306/master
      username: root
      password: 123456
    slave1:
      url: jdbc:mysql://127.0.0.1:3306/slave1
      username: root
      password: 123456
```

- 配置类 `MybatisFlexProperties`（`@ConfigurationProperties(prefix = "mybatis-flex")`）：`default-datasource-key`(:59)、`datasource`(:68，`Map<String,Map<String,String>>`)。
- `FlexDataSource` 用 `dataSourceMap` 管理多数据源，`getDataSource()` 按 `DataSourceKey.get()`（ThreadLocal）取目标源（`mybatis-flex-core/src/main/java/com/mybatisflex/core/datasource/FlexDataSource.java:251`）。
- 切换：Spring 下由 `DataSourceInterceptor` 切面在方法前后 `DataSourceKey.use/clear`（`mybatis-flex-spring/src/main/java/com/mybatisflex/spring/datasource/DataSourceInterceptor.java:52`），注解查找顺序为 方法→类→接口（同文件:73）；非 Spring 下由 `FlexMapperProxy` 处理，还额外支持实体 `@Table(dataSource=...)` 取值（`mybatis-flex-core/src/main/java/com/mybatisflex/core/binding/FlexMapperProxy.java:126`）。

坑点：

- **只有 1 个数据源时 `@UseDataSource` 完全失效**——`getDataSource()` 仅在 `dataSourceMap.size()>1` 时才解析 key（`FlexDataSource.java:255`）。
- key 不存在抛 `IllegalStateException: Cannot get target dataSource by key`（除非注册 `DataSourceMissingHandler`）（`FlexDataSource.java:305`）。
- `default-datasource-key` 配了但 map 里没有，启动即报错"没有找到默认数据源"（`mybatis-flex-spring-boot-starter/src/main/java/com/mybatisflex/spring/boot/config/MultiDataSourceAutoConfiguration.java:106`）。

## 读写分离

**源码中没有内置读写分离**（datasource 包无 slave/readOnly 概念）。官方实现是**基于多数据源 + `DataSourceShardingStrategy` 手动分片**：

```java
public class MyStrategy implements DataSourceShardingStrategy {
    public String doSharding(String curKey, Object mapper, Method method, Object[] args) {
        if (StringUtil.startWithAny(method.getName(), "insert","delete","update")) return "master";
        return "slave*";   // 结尾 * 表示按前缀随机负载均衡
    }
}
DataSourceManager.setDataSourceShardingStrategy(new MyStrategy()); // 启动时注册
```

- 接口签名 `String doSharding(String currentDataSourceKey, Object mapper, Method mapperMethod, Object[] methodArgs)`（`mybatis-flex-core/src/main/java/com/mybatisflex/core/datasource/DataSourceShardingStrategy.java:21`）。
- `slave*` 的 `*` 后缀命中 `LOAD_BALANCE_KEY_SUFFIX`，在匹配前缀的 key 中随机取一个（`FlexDataSource.java:47,260`）。
- 生效点在 Mapper 方法调用：`DataSourceKey.getShardingDsKey(...)`，且在 `@UseDataSource` **之后**执行，可覆盖注解结果（`FlexMapperProxy.java:70`）。

坑点：只做"路由"，不做主从数据同步；仅在走 Mapper 代理时生效；随机是 `ThreadLocalRandom`，无权重、无健康检查，从库下线仍可能被选中。

## 数据源加密

官方机制：实现 `DataSourceDecipher` 并注册到 `DataSourceManager`。

```java
public class MyDecipher implements DataSourceDecipher {
    public String decrypt(DataSourceProperty property, String value) { /* 解密 */ }
}
// Spring: 直接暴露为 DataSourceDecipher Bean 即可；非 Spring:
DataSourceManager.setDecipher(new MyDecipher());
```

- 接口 `String decrypt(DataSourceProperty property, String value)`（`mybatis-flex-core/src/main/java/com/mybatisflex/core/datasource/DataSourceDecipher.java:20`）。
- 仅解密三个属性：`URL/USERNAME/PASSWORD`，通过反射 getter/setter 回写（`DataSourceProperty.java:22`、`DataSourceManager.java:64-88`）。
- Spring 下 `MultiDataSourceAutoConfiguration` 读到 `DataSourceDecipher` Bean 后 `setDecipher`，再对每个数据源 `decryptDataSource`（`MultiDataSourceAutoConfiguration.java:96,120`）。

坑点：`decipher==null` 时静默跳过，不会报错（`DataSourceManager.java:65`）；只覆盖 url/username/password，连接池参数不解密；解密是全局静态，多环境无法用不同密钥；`restartDataSource` 外层 `catch(Exception ignored)` 会吞掉解密相关异常（`DataSourceManager.java:71`）。

## 动态表名

```java
TableManager.setDynamicTableProcessor((tableName, operateType) -> {
    return "tb_account_2024";   // 返回 null/空则用原名
});
```

- 接口 `DynamicTableProcessor`：`String process(String tableName)`（已废弃）与 default `String process(String tableName, OperateType operateType)`，**新实现应重写带 OperateType 的方法**（`mybatis-flex-core/src/main/java/com/mybatisflex/core/table/DynamicTableProcessor.java:27,29`）。
- 入口 `TableManager.getRealTable(tableName, operateType)`：优先取 ThreadLocal hint，再走 processor，结果为空回落原名（`TableManager.java:82-98`）。在 dialect 的 select/insert/update/delete 构建、`QueryTable`、`TableInfo`、`QueryColumn` 等处被调用，覆盖 APISQL 与实体 CRUD。
- 支持单次 hint：`TableManager.setHintTableMapping(原表,目标表)`（ThreadLocal，优先级高于 processor）（`TableManager.java:55`）。

坑点：

- `dynamicTableProcessor` 是全局静态、多线程并发调用，`process()` 必须自行保证线程安全。
- **只作用于 MyBatis-Flex 生成的 SQL**；自定义 XML 里写死的表名不经过 `getRealTable`，不会替换。
- ThreadLocal hint 不会自动清理，跨请求残留需手动 `TableManager.clear()`（否则串数据）（`TableManager.java:119`）。

## 事务管理

Spring 项目优先使用 `@Transactional`。复杂编程式事务再参考 `references/13-transaction-util.md`。

## 数据权限（行级）

**core 中未提供独立的 `DataPermission` 组件**。官方提供的是方言钩子 `IDialect.prepareAuth(...)` 三个 default 空方法（`mybatis-flex-core/src/main/java/com/mybatisflex/core/dialect/IDialect.java:106/117/127`）：

```java
default void prepareAuth(QueryWrapper queryWrapper, OperateType operateType) {}
default void prepareAuth(String schema, String tableName, StringBuilder sql, OperateType operateType) {}
default void prepareAuth(TableInfo tableInfo, StringBuilder sql, OperateType operateType) {}
```

调用点：`CommonsDialectImpl.java:387`(selectById)、`:393`(forSelectByQuery)、`:738`/`:816`(delete)、`:905`/`:911`(update)、`:1003`(selectOneById)；update/deleteByQuery 走 `prepareAuth(queryWrapper, ...)`。

```java
public class AuthDialectImpl extends CommonsDialectImpl {
    @Override
    public void prepareAuth(QueryWrapper qw, OperateType type) {
        for (QueryTable t : CPI.getQueryTables(qw)) {
            if ("tb_project".equals(t.getName())) {
                qw.and(PROJECT.INSERT_USER_ID.eq(currentUserId()));
            }
        }
        super.prepareAuth(qw, type);
    }
}
DialectFactory.registerDialect(DbType.MYSQL, new AuthDialectImpl());
```

（官方完整示例：`mybatis-flex-core/src/test/java/com/mybatisflex/coretest/auth/AuthDialectImpl.java:38`，注册方式见 `docs/zh/core/data-permission.md:120`。）

坑点：

- `prepareAuth` 注册后对**该方言所有 core 生成的 SQL**生效，必须自己用 `CPI.getQueryTables` 按表过滤，否则会给字典表、权限表也加上条件。
- `prepareAuth(schema, tableName, sql, ...)` 是直接往 `StringBuilder` 追加裸常量，不能参数化，无法用于动态用户 ID。
- 手写 `@Select`/XML 不走 `IDialect`，覆盖不到；insert 不调用 `prepareAuth`，新增数据的行级归属要在 `InsertListener` 或实体默认值里保证。
- 替代写法（不引入自定义方言）：在自建 `BaseServiceImpl` 里重写 `list/selectListByQuery` 统一给 `QueryWrapper` 追加 `and(...)`，或写 MyBatis `Interceptor` 改写 `BoundSql`；不要在 Controller 里散拼。

## 字段权限 / 字典回写（onSet 监听）

```java
// mybatis-flex-annotation/src/main/java/com/mybatisflex/annotation/SetListener.java:21
public interface SetListener extends Listener {
    Object onSet(Object entity, String property, Object value);
}
```

`Listener` 提供 `default int order()`，值越小越先执行（`mybatis-flex-annotation/src/main/java/com/mybatisflex/annotation/Listener.java:34`）。配置方式：`@Table(onSet = Xxx.class)`（`Table.java:68`，可配多个），或全局 `FlexGlobalConfig.getDefaultConfig().registerSetListener(listener, Entity.class)`（`FlexGlobalConfig.java:197`）。

**触发时机**（两处，都是"结果被写回实体属性"时）：`FlexWrapperFactory.FlexBeanWrapper.set(prop, value)` 里 `tableInfo.invokeOnSetListener(entity, prop.getName(), value)`（`mybatis-flex-core/src/main/java/com/mybatisflex/core/mybatis/FlexWrapperFactory.java:76`）；Row/Map 转实体时 `TableInfo.java:1493`。`TableInfo.invokeOnSetListener:1610-1621` 会把注解监听器与全局监听器 merge、按 order 排序后**链式传递**（后一个收到前一个的返回值）。

**字典回写完整示例**（展示字段必须 `@Column(ignore = true)`，`Column.java:42`；`ColumnInfo.setIgnore` 见 `TableInfoFactory.java:468`）：

```java
public class AccountOnSetListener implements SetListener {
    @Override
    public Object onSet(Object entity, String property, Object value) {
        if (!"sex".equals(property) || value == null) return value;
        Account a = (Account) entity;
        a.setSexString(switch ((Integer) value) {   // 或 Map<Integer,String> dict
            case 0 -> "女"; case 1 -> "男"; default -> "未知";
        });
        return value;
    }
}

@Table(value = "tb_account", onSet = AccountOnSetListener.class)
public class Account {
    @Id(keyType = KeyType.Auto) private Long id;
    private Integer sex;

    @Column(ignore = true)   // 非数据库字段
    private String sexString;
}
```

坑点：

- **业务代码主动调用 setter 不触发**（`@Table.java:66` 注释明确："用户主动 set 不会触发"），只覆盖"查询结果映射"这一条路径。
- 若属性配了 `typeHandler`，`typeHandler` 先执行、`SetListener` 后执行，`onSet` 收到的是转换后的值。
- `FlexBeanWrapper` 只对 `TableInfoFactory.ofEntityClass(cls) != null` 的实体生效（`FlexWrapperFactory.java:45`）；查询到 `Map`/`Row` 不触发 onSet。
- 返回 `null` 只把实体属性置空，数据库里的值仍在；当"字段权限"用时，导出、日志、序列化链路要一并确认。

## 字段加密

**官方源码未提供内置加密 TypeHandler**。官方文档 `docs/zh/core/columns-encrypt.md` 的做法是用 `SetListener` 对**查询返回值**加密（只读侧）。若需求是入库加密、查询解密，需自定义 TypeHandler，继承 MyBatis 的 `BaseTypeHandler<T>`（可参考内置 `JacksonTypeHandler` 的写法，`mybatis-flex-core/src/main/java/com/mybatisflex/core/handler/JacksonTypeHandler.java:29`），再通过 `@Column(typeHandler = XxxTypeHandler.class)` 启用：

```java
public class AesTypeHandler extends BaseTypeHandler<String> {
    @Override
    public void setNonNullParameter(PreparedStatement ps, int i, String parameter, JdbcType jdbc) {
        ps.setString(i, EncryptUtil.encrypt(parameter));   // 入库加密
    }
    @Override
    public String getNullableResult(ResultSet rs, String columnName) {
        return EncryptUtil.decrypt(rs.getString(columnName)); // 查询解密
    }
    // getNullableResult(ResultSet, int) / (CallableStatement, int) 同理
}
```

坑点：加密列无法参与 `where` 等值查询（库里是密文），需要按密文查或维护哈希列；密钥来源必须来自安全配置；与脱敏（`@ColumnMask`）叠加时执行顺序为 `typeHandler` → `MaskTypeHandler` → `SetListener`。

## 枚举属性

`@EnumValue` 可标注在**字段或方法**上（`mybatis-flex-annotation/src/main/java/com/mybatisflex/annotation/EnumValue.java:25`）。枚举字段由内置 `FlexEnumTypeHandler` 处理（`mybatis-flex-core/src/main/java/com/mybatisflex/core/handler/FlexEnumTypeHandler.java:27`，注册点 `TableInfo.java:836`），取值逻辑在 `EnumWrapper`（`mybatis-flex-core/src/main/java/com/mybatisflex/core/util/EnumWrapper.java`）：

1. 优先 `@EnumValue` 标注的 get 方法（先找 `getXxx()`，再找 fluent 风格 `xxx()`）；
2. 其次 `@EnumValue` 标注的字段；
3. 都没有则取枚举 `name()`。

（顺序注释见 `EnumWrapper.java:117-126`。）

```java
public enum TypeEnum {
    TYPE1(1, "类型1"),
    TYPE2(2, "类型2");

    @EnumValue
    private final int code;
    private final String desc;
    // getter
}
```

坑点：

- 标注字段时必须有对应 public getter（`getXxx()` 或 `xxx()`），否则抛 `IllegalStateException: Can not find method "getXxx()" in enum`（`EnumWrapper.java:70`）。
- 方法上标注 `@EnumValue` 时，方法返回类型不能是泛型（`EnumWrapper.java:100-104`）。
- 没有 `@EnumValue` 时存的是枚举名 `name()`，与 MyBatis 默认 `EnumTypeHandler` 行为一致；`getEnum(value)` 是线性扫描匹配（`EnumWrapper.java:143-152`）。

## 多租户

核心类 3 个：`TenantManager`、`TenantFactory`、拼条件的 `TableInfo`。

```java
// mybatis-flex-core/src/main/java/com/mybatisflex/core/tenant/TenantFactory.java:18
public interface TenantFactory {
    @Deprecated Object[] getTenantIds();                      // :24 已废弃
    default Object[] getTenantIds(String tableName) { ... }   // :26 推荐实现，带表名
}
```

`TenantManager`：`setTenantFactory(f)`(:33)、`getTenantIds(tableName)`(:91)、`withoutTenantCondition(Supplier/Runnable)`(:40/:52)、`ignoreTenantCondition()`/`restoreTenantCondition()`(:65/:79)。

**忽略租户的机制**：源码中**没有** `ignoreTables` 配置。只有两条路：

1. `TenantManager.withoutTenantCondition(...)` / `ignoreTenantCondition()`（ThreadLocal 开关，`TenantManager.java:25`）；
2. 在 `TenantFactory.getTenantIds(tableName)` 里自己按 `tableName` 判断，返回 `null` 或空数组 → `TableInfo.buildTenantCondition` 不拼条件（`TableInfo.java:952`、`981`）。

**@Column(tenantId = true)** 位于 `Column.java:77`。也可全局省注解：`FlexGlobalConfig.getDefaultConfig().setTenantColumn("tenant_id")`（`FlexGlobalConfig.java:331`），匹配规则见 `TableInfoFactory.java:414`；一张表多于 1 个租户列会抛异常（`TableInfoFactory.java:419`）。

**值如何参与 SQL**：

| 操作 | 入口 | 拼接点 |
|---|---|---|
| insert | `EntitySqlProvider.insert:65` → `TableInfo.initTenantIdIfNecessary:1528` | 写入前给实体属性赋值，不用 SQL 条件 |
| deleteById / deleteBatchByIds | `EntitySqlProvider.java:167`、`:189` | `CommonsDialectImpl.java:719`、`:757` |
| update(entity) | `EntitySqlProvider.java:240` | `CommonsDialectImpl.java:893` |
| selectOneById / selectListByIds | `EntitySqlProvider.java:306`、`:329` | `CommonsDialectImpl.java:1001`、`:1019` |
| QueryWrapper 系 | `EntitySqlProvider.java:386` → `TableInfo.appendConditions` → `buildTenantCondition(QueryWrapper):974` | `CommonsDialectImpl.java:393` 等 |

单值生成 `AND tenant_id = ?`，多值生成 `AND tenant_id IN (?,?,...)`（`TableInfo.java:965-968`）。

```java
@Table("tb_article")
public class Article {
    @Id(keyType = KeyType.Auto) private Long id;
    @Column(tenantId = true)    private Long tenantId;   // 租户列
}

// 启动期配置一次；Spring 场景从 RequestContextHolder/ThreadLocal 取
TenantManager.setTenantFactory(() -> new Object[]{currentTenantId()});

// 跨租户查询（平台端）
List<Article> all = TenantManager.withoutTenantCondition(mapper::selectAll);
```

坑点：

- **未配置 `TenantFactory` 时不报错、直接不拼租户条件**（`TenantManager.java:95` 三元判空返回 null）——隔离会静默失效，必须在启动期断言 `getTenantFactory() != null`。
- 1.11.8 源码中，实体租户字段**已有值则跳过**（`TableInfo.java:1538-1541`，注释引用 issue I7OWYD/I920DK），只有 null 才用 `tenantIds[0]` 填充（`:1549`）；多个租户 ID 时插入只取第一个。
- 普通 `update(entity)` 会把 `tenantIdColumn` 从 SET 中剔除（`TableInfo.java:726`），即改不了数据的归属租户；只有 `withoutTenantCondition` 下才允许（`:721-728`）。
- `ignoreTenantCondition()`/`restoreTenantCondition()` **不可嵌套**：`restore` 是 `remove()` 而非恢复旧值（`TenantManager.java:79-81`），内层 `withoutTenantCondition` 退出会把外层的忽略标志一起清掉。
- Row 级 API（`Db.*`、`RowMapper.selectListByQuery`）不自动拼租户条件——`RowSqlProvider.selectListByQuery:297` 没有调用 `TableInfo.appendConditions`，只有 `EntitySqlProvider` 调了。
