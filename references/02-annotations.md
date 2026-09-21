# 注解详解

## 实体注解

### @Table

```java
@Table("tb_account")
public class Account { }
```

`value` 支持：
- **表名：** `"tb_account"`
- **Schema：** `"myschema.tb_account"` 或 `@Table(value = "tb_account", schema = "myschema")`
- **SQL：** `"(SELECT * FROM tb_account) temp"` 子查询

### @Id

```java
@Id(keyType = KeyType.Auto)
private Long id;
```

| KeyType | 说明 |
|---------|------|
| `Auto` | 数据库自增 |
| `Sequence` | 通过执行数据库 SQL 生成（如序列） |
| `Generator` | 主键生成器（如雪花算法），通过 `value` 指定生成器名称 |
| `None` | 其他方式（代码层手动设置），默认值 |

KeyType 枚举与 `@Id` 默认值源码：`mybatis-flex-annotation/src/main/java/com/mybatisflex/annotation/KeyType.java:21-44`、`mybatis-flex-annotation/src/main/java/com/mybatisflex/annotation/Id.java:33-42`。

### @Column

```java
@Column(value = "user_name", ignore = true)
private String userName;
```

- `value`：列名（默认驼峰转下划线）
- `typeHandler`：类型处理器
- `ignore`：忽略该字段
- `isLarge`：是否大字段

### @ColumnAlias

给字段（或 getter 方法）设置查询别名，用于解决多表同名列覆盖，查询时自动追加 `as`：

```java
public class AccountVO {
    @ColumnAlias("account_id")
    private Long id;
}
```

注意：`@ColumnAlias` 只能标注在字段或方法上（`@Target({ElementType.FIELD, ElementType.METHOD})`），**不能**标注在类上；`value` 是完整别名，不是自动拼接的“前缀”。源码：`mybatis-flex-annotation/src/main/java/com/mybatisflex/annotation/ColumnAlias.java:29-37`。

### @Relation

#### @RelationOneToOne

一对一关联：

```java
@RelationOneToOne(
    selfField = "id",
    targetField = "accountId"
)
private IDCard idCard;
```

#### @RelationOneToMany

一对多关联：

```java
@RelationOneToMany(
    selfField = "id",
    targetField = "accountId"
)
private List<Article> articles;
```

#### @RelationManyToOne

多对一关联：

```java
@RelationManyToOne(
    selfField = "accountId",
    targetField = "id"
)
private Account account;
```

#### @RelationManyToMany

多对多关联：

```java
@RelationManyToMany(
    joinTable = "tb_article_tag_mapping",
    selfField = "id",
    joinSelfColumn = "article_id",
    targetField = "id",
    joinTargetColumn = "tag_id"
)
private List<Tag> tags;
```

#### 关联查询方法

```java
// 查询所有关联
mapper.selectAllWithRelations();

// 指定关联查询
mapper.selectListWithRelationsByQuery(query);

// 条件查询关联
mapper.selectOneWithRelationsByQuery(query);
```

## 其他注解

注意：MyBatis-Flex **没有** `@Version`、`@LogicDelete`、`@OnInsert`、`@OnUpdate`、`@ColumnListener` 这些独立注解（1.11.8 源码 `mybatis-flex-annotation/src/main/java/com/mybatisflex/annotation/` 目录下不存在）。乐观锁、逻辑删除、数据填充全部通过 `@Column` / `@Table` 的属性或监听器接口实现，不要按旧资料误写。

### 乐观锁

```java
@Column(version = true)
private Integer version;
```

更新时校验版本号，更新成功后版本号 +1，只能用于数值字段。源码：`mybatis-flex-annotation/src/main/java/com/mybatisflex/annotation/Column.java:66-72`。

### 逻辑删除

```java
@Column(isLogicDelete = true)
private Boolean isDelete;
```

一张表只能有一个逻辑删除字段，删除时置 1、正常为 0（可通过 `FlexGlobalConfig` 修改）。源码：`mybatis-flex-annotation/src/main/java/com/mybatisflex/annotation/Column.java:59-64`。

### 数据填充

- SQL 层默认值（直接拼接进 SQL，不走参数）：`@Column(onInsertValue = "NOW()")`、`@Column(onUpdateValue = "NOW()")`，源码 `Column.java:44-52`。
- Java 层监听器：`@Table(onInsert = XxxInsertListener.class, onUpdate = XxxUpdateListener.class, onSet = XxxSetListener.class)`，源码 `mybatis-flex-annotation/src/main/java/com/mybatisflex/annotation/Table.java:55-68`；监听器接口为 `com.mybatisflex.annotation.InsertListener` / `UpdateListener` / `SetListener`（`AbstractInsertListener`、`AbstractUpdateListener`、`NoneListener` 为辅助实现）。

## APT 生成的 TableDef

```java
// 自动生成
public class AccountTableDef extends TableDef {
    public static final AccountTableDef ACCOUNT = new AccountTableDef();
    
    public final QueryColumn ID = new QueryColumn(this, "id");
    public final QueryColumn USER_NAME = new QueryColumn(this, "user_name");
    public final QueryColumn AGE = new QueryColumn(this, "age");
    public final QueryColumn BIRTHDAY = new QueryColumn(this, "birthday");
    
    // 所有列：单个 QueryColumn，SQL 值为 "*"（不是数组）
    public final QueryColumn ALL_COLUMNS = new QueryColumn(this, "*");
    
    // 默认字段：QueryColumn 数组，不含逻辑删除、大字段
    public final QueryColumn[] DEFAULT_COLUMNS = {ID, USER_NAME, AGE, BIRTHDAY};
}
```

生成逻辑源码：`mybatis-flex-processor/src/main/java/com/mybatisflex/processor/builder/ContentBuilder.java:116`（`ALL_COLUMNS`）与 `ContentBuilder.java:130`（`DEFAULT_COLUMNS`）。

使用静态导入：

```java
import static com.example.common.entity.table.AccountTableDef.ACCOUNT;

// 类型安全查询
QueryWrapper.create()
    .select(ACCOUNT.DEFAULT_COLUMNS)
    .from(ACCOUNT)
    .where(ACCOUNT.ID.ge(100));
```
