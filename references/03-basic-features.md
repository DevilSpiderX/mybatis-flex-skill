# 官网基础功能用例补齐

本文件补齐官网基础功能页的常用用例。写代码时优先复用项目既有 Mapper、Service、DTO 和异常风格。

## 增、删、改

```java
accountMapper.insert(entity);
accountMapper.insertSelective(entity);

accountMapper.update(entity);
accountMapper.update(entity, true);
accountMapper.updateByQuery(entity, queryWrapper);

accountMapper.deleteById(id);
accountMapper.deleteByQuery(queryWrapper);
```

- `insert(entity)` 不忽略 null。
- `insertSelective(entity)` 忽略 null，数据库默认值才会生效。
- `update(entity)` 根据主键更新，实体属性为 null 时默认不更新。
- 显式更新部分字段为 null 时，使用 `UpdateEntity` 或 `OptionalField`。

## 基础查询

```java
Account account = accountMapper.selectOneById(id);

List<Account> accounts = accountMapper.selectListByQuery(
    QueryWrapper.create()
        .where(ACCOUNT.AGE.ge(18))
);

Page<Account> page = accountMapper.paginate(
    pageNumber,
    pageSize,
    QueryWrapper.create().where(ACCOUNT.AGE.ge(18))
);
```

## 自动映射

多表查询、VO/DTO 查询时，优先使用 `as` 显式映射，避免同名字段覆盖。

```java
QueryWrapper wrapper = QueryWrapper.create()
    .select(
        ACCOUNT.ID,
        ACCOUNT.USER_NAME,
        BOOK.TITLE.as(AccountBookVO::getBookTitle)
    )
    .from(ACCOUNT)
    .leftJoin(BOOK).on(BOOK.ACCOUNT_ID.eq(ACCOUNT.ID))
    .where(ACCOUNT.ID.eq(id));

AccountBookVO vo = accountMapper.selectOneByQueryAs(wrapper, AccountBookVO.class);
```

## 关联查询

MyBatis-Flex 官网提供三类关联方案：

- Relations 注解：`@RelationOneToOne`、`@RelationOneToMany`、`@RelationManyToOne`、`@RelationManyToMany`
- Field Query：通过字段映射查询关联数据
- Join Query：使用 `leftJoin`、`innerJoin` 等 SQL join

Relations 注解不会在普通查询中自动生效，必须调用 withRelations 系列方法。

```java
Account account = accountMapper.selectOneWithRelationsById(id);

AccountVO vo = accountMapper.queryChain()
    .where(ACCOUNT.ID.eq(id))
    .oneWithRelationsAs(AccountVO.class);
```

## 批量操作

```java
accountMapper.insertBatch(accounts);
accountMapper.insertBatchSelective(accounts);
```

大批量 SQL 或非实体场景可评估 `Db.executeBatch`。批量更新前必须确认数据量、事务边界和失败回滚策略。

## Db + Row

`Db + Row` 适合无实体映射、临时表、管理工具、通用 SQL 场景。

```java
Row row = new Row();
row.set("id", 100);
row.set(ACCOUNT.USER_NAME, "Michael");

Db.insert("tb_account", row);

Row result = Db.selectOneById("tb_account", "id", 100);
Account account = result.toEntity(Account.class);
```

业务核心表优先使用实体和 Mapper；不要用字符串表名绕过权限、租户、审计和统一拦截逻辑。

## Active Record

Entity 继承 `Model` 后可以使用 Active Record 风格。项目中仍必须注入对应实体的 `BaseMapper`。

```java
public class Account extends Model<Account> {
}

Account.create()
    .setAge(100)
    .where(Account::getId).eq(1L)
    .update();

Account account = Account.create()
    .where(Account::getId).eq(1L)
    .one();
```

若项目已经采用分层 Service/Mapper，除非现有代码就是 Active Record 风格，否则不要新引入这种写法。

## IService

官网 `IService` 提供 Service 层通用 CRUD。当前技能默认约束是 Service 直接注入 Mapper，不主动让 `ServiceImpl` 继承 `IService`。只有既有项目已统一使用 `IService` 时，才按官网 Service 风格补代码。

## SpringBoot 配置文件

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/flex_test
    username: root
    password: 123456

mybatis-flex:
  mapper-locations: classpath*:/mapper/**/*.xml
  configuration:
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
```

配置项变更影响面通常较大，修改前确认环境、 profile、数据源、SQL 打印是否允许在当前环境启用。

## MyBatisFlexCustomizer

`MyBatisFlexCustomizer` 用于 SpringBoot 或 Solon 启动期初始化 MyBatis-Flex 全局能力。

```java
@Configuration
public class MyBatisFlexConfiguration implements MyBatisFlexCustomizer {

    @Override
    public void customize(FlexGlobalConfig globalConfig) {
        // 全局配置、主键生成器、多租户、动态表名、审计、SQL 打印等
    }
}
```

只有全局能力确实需要统一初始化时才新增 customizer；普通 Mapper 查询不要引入全局配置。
