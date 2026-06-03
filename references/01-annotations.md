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
| `Generator` | 主键生成器（如雪花算法） |

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

批量设置别名前缀：

```java
@ColumnAlias("acc")
public class AccountVO { }
```

等效于每个字段加别名前缀。

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

### @Version

乐观锁：

```java
@Version
private Integer version;
```

### @ColumnListener

字段监听器：

```java
@ColumnListener
private LocalDateTime createTime;
```

### @LogicDelete

逻辑删除：

```java
@LogicDelete
private Boolean isDelete;
```

### @OnInsert

插入时自动填充：

```java
@OnInsert
private LocalDateTime createTime;
```

### @OnUpdate

更新时自动填充：

```java
@OnUpdate
private LocalDateTime updateTime;
```

## APT 生成的 TableDef

```java
// 自动生成
public class AccountTableDef extends TableDef {
    public static final AccountTableDef ACCOUNT = new AccountTableDef();
    
    public final QueryColumn ID = new QueryColumn(this, "id");
    public final QueryColumn USER_NAME = new QueryColumn(this, "user_name");
    public final QueryColumn AGE = new QueryColumn(this, "age");
    public final QueryColumn BIRTHDAY = new QueryColumn(this, "birthday");
    
    // 所有列
    public final QueryColumn[] ALL_COLUMNS = {ID, USER_NAME, AGE, BIRTHDAY};
}
```

使用静态导入：

```java
import static com.your.package.entity.table.AccountTableDef.ACCOUNT;

// 类型安全查询
QueryWrapper.create()
    .select(ACCOUNT.ALL_COLUMNS)
    .from(ACCOUNT)
    .where(ACCOUNT.ID.ge(100));
```
