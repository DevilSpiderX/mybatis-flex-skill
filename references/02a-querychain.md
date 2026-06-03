# QueryChain 链式查询

QueryChain 是对 QueryWrapper 的封装，提供了链式调用的便利，可以直接执行查询并返回结果。

## 基础用法

### 在 Service 中使用

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

当 SQL 只返回 1 列、1 条数据时使用：

```java
// 查询单个值
String userName = QueryChain.of(accountMapper)
    .select(ACCOUNT.USER_NAME)
    .from(ACCOUNT)
    .where(ACCOUNT.ID.eq(1))
    .obj();
```

### objList() - 查询单列列表

当 SQL 只返回 1 列时使用：

```java
// 查询单列列表
List<String> userNames = QueryChain.of(accountMapper)
    .select(ACCOUNT.USER_NAME)
    .from(ACCOUNT)
    .where(ACCOUNT.AGE.ge(18))
    .objList();
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

### oneWithRelations() - 查询单条及关联数据

```java
// 查询账户及其关联的文章列表
Account account = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.ID.eq(1))
    .oneWithRelations();
```

### listWithRelations() - 查询列表及关联数据

```java
// 查询所有账户及其关联数据
List<Account> accounts = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.AGE.ge(18))
    .listWithRelations();
```

### oneWithRelationsAs() - 查询关联数据并转换

```java
AccountVO vo = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.ID.eq(1))
    .oneWithRelationsAs(AccountVO.class);
```

### listWithRelationsAs() - 查询关联列表并转换

```java
List<AccountVO> voList = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.AGE.ge(18))
    .listWithRelationsAs(AccountVO.class);
```

## 方法汇总

| 方法 | 说明 |
|------|------|
| `one()` | 获取一条数据 |
| `oneOpt()` | 返回 Optional 类型 |
| `oneAs(asType)` | 查询并转换为 DTO/VO |
| `oneAsOpt(asType)` | 返回 Optional 并转换 |
| `oneWithRelations()` | 查询一条数据及关联数据 |
| `oneWithRelationsOpt()` | 返回 Optional 及关联数据 |
| `oneWithRelationsAs(asType)` | 查询关联数据并转换 |
| `oneWithRelationsAsOpt(asType)` | 返回 Optional 关联数据并转换 |
| `list()` | 查询数据列表 |
| `listAs(asType)` | 查询列表并转换 |
| `listWithRelations()` | 查询列表及关联数据 |
| `listWithRelationsAs(asType)` | 查询关联列表并转换 |
| `page(page)` | 分页查询 |
| `pageAs(page, asType)` | 分页查询并转换 |
| `obj()` | 查询单值（单列单行） |
| `objList()` | 查询单列列表 |
| `count()` | 查询数据条数 |
| `exists()` | 判断是否存在 |

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
