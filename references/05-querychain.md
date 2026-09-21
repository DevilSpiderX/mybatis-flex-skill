# QueryChain 链式查询

QueryChain 是对 QueryWrapper 的封装，提供了链式调用的便利，可以直接执行查询并返回结果。

## 基础用法

### 在 Service 中使用

`queryChain()` 只在 Service 继承 `IService` 时可用
（mybatis-flex-core/src/main/java/com/mybatisflex/core/service/IService.java:677 起）。
1.11.8 起 `BaseMapper` 已移除 `queryChain()`；若项目 Service 不继承 `IService`，
请直接用 `QueryChain.of(mapper)`（见下）。

```java
@SpringBootTest
class ArticleServiceTest {

    @Autowired
    ArticleService articleService;

    @Test
    void testChain() {
        List<Article> articles = articleService.queryChain()
            .select(ARTICLE.ALL_COLUMNS)
            .from(ARTICLE)
            .where(ARTICLE.ID.ge(100))
            .list();
    }
}
```

### 在 Mapper 中使用

通过 `QueryChain.of(mapper)` 创建实例：

```java
List<Article> articles = QueryChain.of(mapper)
    .select(ARTICLE.ALL_COLUMNS)
    .from(ARTICLE)
    .where(ARTICLE.ID.ge(100))
    .list();
```

## 核心查询方法

### one() - 查询单条

```java
// 查询一条数据
Account account = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.ID.eq(1))
    .one();

// 返回 Optional
Optional<Account> opt = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.ID.eq(1))
    .oneOpt();
```

### list() - 查询列表

```java
// 查询多条数据
List<Account> accounts = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.AGE.ge(18))
    .list();
```

### page() - 分页查询

```java
// 分页查询
Page<Account> page = Page.of(1, 10); // 第1页，每页10条
Page<Account> result = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.AGE.ge(18))
    .page(page);
```

### obj() - 查询单值

当 SQL 只返回 1 列、1 条数据时使用。注意 `obj()` 返回 `Object`
（mybatis-flex-core/src/main/java/com/mybatisflex/core/query/MapperQueryChain.java:99），
需要具体类型时用 `objAs(Class)`

```java
// 查询单个值（返回 Object）
Object userNameObj = QueryChain.of(accountMapper)
    .select(ACCOUNT.USER_NAME)
    .from(ACCOUNT)
    .where(ACCOUNT.ID.eq(1))
    .obj();

// 查询单个值并转换为 String
String userName = QueryChain.of(accountMapper)
    .select(ACCOUNT.USER_NAME)
    .from(ACCOUNT)
    .where(ACCOUNT.ID.eq(1))
    .objAs(String.class);
```

### objList() - 查询单列列表

当 SQL 只返回 1 列时使用。注意 `objList()` 返回 `List<Object>`
（mybatis-flex-core/src/main/java/com/mybatisflex/core/query/MapperQueryChain.java:140），
需要具体元素类型时用 `objListAs(Class)`

```java
// 查询单列列表（返回 List<Object>）
List<Object> userNamesObj = QueryChain.of(accountMapper)
    .select(ACCOUNT.USER_NAME)
    .from(ACCOUNT)
    .where(ACCOUNT.AGE.ge(18))
    .objList();

// 查询单列列表并转换为 List<String>
List<String> userNames = QueryChain.of(accountMapper)
    .select(ACCOUNT.USER_NAME)
    .from(ACCOUNT)
    .where(ACCOUNT.AGE.ge(18))
    .objListAs(String.class);
```

### count() - 查询数量

```java
// 查询总数
long count = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.AGE.ge(18))
    .count();
```

### exists() - 判断是否存在

```java
// 判断是否存在（count > 0）
boolean exists = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.USER_NAME.like("admin"))
    .exists();
```

## 转换为 DTO/VO

### oneAs() - 查询并转换单条

```java
AccountVO vo = QueryChain.of(accountMapper)
    .select(ACCOUNT.ID, ACCOUNT.USER_NAME, ACCOUNT.AGE)
    .from(ACCOUNT)
    .where(ACCOUNT.ID.eq(1))
    .oneAs(AccountVO.class);
```

### listAs() - 查询列表并转换

```java
List<AccountVO> voList = QueryChain.of(accountMapper)
    .select(ACCOUNT.ID, ACCOUNT.USER_NAME, ACCOUNT.AGE)
    .from(ACCOUNT)
    .where(ACCOUNT.AGE.ge(18))
    .listAs(AccountVO.class);
```

### pageAs() - 分页查询并转换

```java
Page<AccountVO> voPage = QueryChain.of(accountMapper)
    .select(ACCOUNT.ID, ACCOUNT.USER_NAME, ACCOUNT.AGE)
    .from(ACCOUNT)
    .where(ACCOUNT.AGE.ge(18))
    .pageAs(page, AccountVO.class);
```

## 关联查询（With Relations）

QueryChain **没有** `oneWithRelations()` / `listWithRelations()` 等方法。
关联查询通过 `withRelations()` 返回 `RelationsBuilder`，再调用 `one()` / `list()` / `page()`
（mybatis-flex-core/src/main/java/com/mybatisflex/core/query/MapperQueryChain.java:197、
RelationsBuilder.java:86、102、118）。

```java
// 查询账户及其关联的文章列表
Account account = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.ID.eq(1))
    .withRelations()
    .one();

// 查询所有账户及其关联数据
List<Account> accounts = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.AGE.ge(18))
    .withRelations()
    .list();

// 关联查询并转换为 DTO
AccountVO vo = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.ID.eq(1))
    .withRelations()
    .oneAs(AccountVO.class);

// 关联分页查询
Page<Account> accountPage = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .withRelations()
    .page(Page.of(1, 10));
```

> **注意**：`withRelations()` 还可链式配置 `ignoreRelations(...)`、`maxDepth(int)`、
> `extraConditionParam(key, value)`（mybatis-flex-core/src/main/java/com/mybatisflex/core/query/RelationsBuilder.java:43、65、77）。

## 方法汇总

| 方法 | 说明 | 源码位置 |
|------|------|----------|
| `one()` | 获取一条数据 | MapperQueryChain.java:82 |
| `oneOpt()` | 返回 Optional 类型 | ChainQuery.java:61 |
| `oneAs(asType)` | 查询并转换为 DTO/VO | MapperQueryChain.java:90 |
| `oneAsOpt(asType)` | 返回 Optional 并转换 | ChainQuery.java:72 |
| `list()` | 查询数据列表 | MapperQueryChain.java:158 |
| `listAs(asType)` | 查询列表并转换 | MapperQueryChain.java:165 |
| `page(page)` | 分页查询 | MapperQueryChain.java:172 |
| `pageAs(page, asType)` | 分页查询并转换 | MapperQueryChain.java:179 |
| `obj()` | 查询单值（单列单行），返回 Object | MapperQueryChain.java:99 |
| `objAs(asType)` | 查询单值并转换类型 | MapperQueryChain.java:110 |
| `objOpt()` | 查询单值并返回 Optional | MapperQueryChain.java:119 |
| `objAsOpt(asType)` | 查询单值转换类型并返回 Optional | MapperQueryChain.java:131 |
| `objList()` | 查询单列列表，返回 List<Object> | MapperQueryChain.java:140 |
| `objListAs(asType)` | 查询单列列表并转换元素类型 | MapperQueryChain.java:151 |
| `count()` | 查询数据条数 | MapperQueryChain.java:65 |
| `exists()` | 判断是否存在 | MapperQueryChain.java:74 |
| `withRelations()` | 进入关联查询构建器（RelationsBuilder） | MapperQueryChain.java:197 |

> 以上源码位置均为 mybatis-flex-core/src/main/java/com/mybatisflex/core/query/ 下的文件。

## 多表关联示例

```java
// 关联查询文章和作者信息
List<Article> articles = QueryChain.of(articleMapper)
    .select(ARTICLE.ALL_COLUMNS)
    .from(ARTICLE)
    .leftJoin(ACCOUNT).on(ARTICLE.ACCOUNT_ID.eq(ACCOUNT.ID))
    .where(ACCOUNT.AGE.ge(18))
    .list();

// 关联查询并转换为 DTO
List<ArticleDTO> dtoList = QueryChain.of(articleMapper)
    .select(ARTICLE.ALL_COLUMNS)
    .select(
        ACCOUNT.USER_NAME.as(ArticleDTO::getAuthorName),
        ACCOUNT.AGE.as(ArticleDTO::getAuthorAge)
    )
    .from(ARTICLE)
    .leftJoin(ACCOUNT).on(ARTICLE.ACCOUNT_ID.eq(ACCOUNT.ID))
    .where(ACCOUNT.AGE.ge(18))
    .listAs(ArticleDTO.class);
```

## 动态条件示例

```java
String userName = "michael";
Integer minAge = 18;

List<Account> accounts = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.USER_NAME.like(userName, If::hasText))
    .and(ACCOUNT.AGE.ge(minAge, minAge != null))
    .list();
```
