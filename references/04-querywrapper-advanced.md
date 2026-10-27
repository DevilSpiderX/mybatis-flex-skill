# QueryWrapper 高级用法

## 基础查询

```java
QueryWrapper query = QueryWrapper.create()
    .select(ACCOUNT.ID, ACCOUNT.USER_NAME, ACCOUNT.AGE)
    .from(ACCOUNT)
    .where(ACCOUNT.ID.ge(100))
    .and(ACCOUNT.USER_NAME.like("michael"))
    .orderBy(ACCOUNT.ID.desc());
```

## 多表关联

### Left Join

```java
QueryWrapper query = QueryWrapper.create()
    .select(ACCOUNT.ALL_COLUMNS, ARTICLE.TITLE)
    .from(ACCOUNT)
    .leftJoin(ARTICLE).on(ACCOUNT.ID.eq(ARTICLE.ACCOUNT_ID))
    .where(ACCOUNT.AGE.ge(10));
```

### Right Join

```java
QueryWrapper query = QueryWrapper.create()
    .select()
    .from(ACCOUNT)
    .rightJoin(DEPARTMENT).on(ACCOUNT.DEPT_ID.eq(DEPARTMENT.ID));
```

### Inner Join

```java
QueryWrapper query = QueryWrapper.create()
    .select()
    .from(ACCOUNT)
    .innerJoin(ARTICLE).on(ACCOUNT.ID.eq(ARTICLE.ACCOUNT_ID));
```

### Cross Join

```java
QueryWrapper query = QueryWrapper.create()
    .select()
    .from(ACCOUNT)
    .crossJoin(ARTICLE);
```

## 动态条件

在 `where`、`and`、`or` 等方法中，**推荐使用 APT 生成的 `QueryColumn`（如 `ACCOUNT.AGE`、`ACCOUNT.USER_NAME`）**，而不是 `Lambda`（如 `Account::getAge`）。`when`、`If::hasText` 等条件判断保持 `Lambda` 写法即可。

### 基础动态

```java
// 当 flag = false 时忽略该条件
QueryWrapper query = QueryWrapper.create()
    .select().from(ACCOUNT)
    .where(ACCOUNT.ID.ge(100).when(flag))
    .and(ACCOUNT.USER_NAME.like(name, If::hasText));
```

### 复杂动态

```java
QueryWrapper query = QueryWrapper.create()
    .select().from(ACCOUNT)
    .where(ACCOUNT.AGE.ge(minAge).when(minAge != null))
    .and(ACCOUNT.AGE.le(maxAge).when(maxAge != null))
    .and(ACCOUNT.USER_NAME.like(userName, If::hasText));
```

## 子查询

```java
// 条件中的子查询
QueryWrapper query = QueryWrapper.create()
    .select().from(ACCOUNT)
    .where(ACCOUNT.ID.in(
        QueryWrapper.create()
            .select(ARTICLE.ACCOUNT_ID)
            .from(ARTICLE)
            .where(ARTICLE.STATUS.eq(1))
    ));

// FROM 子查询
QueryWrapper query = QueryWrapper.create()
    .select()
    .from(QueryWrapper.create()
        .select(ACCOUNT.ID, ACCOUNT.USER_NAME)
        .from(ACCOUNT)
        .as("temp_account")
    );
```

## SQL 函数

### 常用函数

```java
import static com.mybatisflex.core.query.QueryMethods.*;

// 聚合函数
QueryWrapper.create()
    .select(
        count(),
        count(ACCOUNT.ID).as("cnt"),
        max(ACCOUNT.AGE).as("maxAge"),
        min(ACCOUNT.AGE).as("minAge"),
        sum(ACCOUNT.AGE).as("totalAge"),
        avg(ACCOUNT.AGE).as("avgAge")
    )
    .from(ACCOUNT);

// 字符串函数
QueryWrapper.create()
    .select(
        upper(ACCOUNT.USER_NAME),
        lower(ACCOUNT.USER_NAME),
        length(ACCOUNT.USER_NAME),
        concat(ACCOUNT.USER_NAME, string(" - "), ACCOUNT.AGE),
        substring(ACCOUNT.USER_NAME, 1, 3)
    )
    .from(ACCOUNT);

// 日期函数
QueryWrapper.create()
    .select(
        year(ACCOUNT.BIRTHDAY),
        month(ACCOUNT.BIRTHDAY),
        day(ACCOUNT.BIRTHDAY),
        curDate(),
        now()
    )
    .from(ACCOUNT);

// 条件函数
QueryWrapper.create()
    .select(
        coalesce(ACCOUNT.NICK_NAME, ACCOUNT.USER_NAME),
        if_(ACCOUNT.AGE.ge(18), "成年", "未成年")
    )
    .from(ACCOUNT);

// 格式化
QueryWrapper.create()
    .select(
        format(ACCOUNT.SALARY, number(2)),
        round(ACCOUNT.SCORE, 2),
        floor(ACCOUNT.SCORE),
        ceil(ACCOUNT.SCORE),
        abs(ACCOUNT.BALANCE)
    )
    .from(ACCOUNT);
```

> **坑点**（源码位置均为 mybatis-flex-core/src/main/java/com/mybatisflex/core/query/QueryMethods.java）：
> - 当前日期方法是 `curDate()`（:1192），Java 大小写敏感，不存在小写的 `curdate()`。
> - `concat` 只有「全 String」（:732）和「全 QueryColumn」（:739）两组重载；混合字符串字面量与列时必须用 `string(" - ")`（:2430）转为查询列。
> - `format` 没有 `(QueryColumn, int)` 重载，只有 `(String, String)`（:2070）、`(QueryColumn, QueryColumn)`（:2077）、`(LambdaGetter, LambdaGetter)`（:2084）；位数参数要用 `number(2)`（:2423）转成查询列。`round` 才有 `(QueryColumn, Integer)` 重载（:274）。
> - 1.11.8 的 `QueryMethods` 没有 `nullif`（全量检索无 NULLIF），不要调用；确需 `NULLIF` 时用原生 SQL 或原生列实现。

### Case When

```java
// 简单 Case
QueryWrapper.create()
    .select(
        ACCOUNT.ID,
        case_(ACCOUNT.STATUS)
            .when(1).then("启用")
            .when(0).then("禁用")
            .else_("未知")
            .end()
            .as("statusName")
    )
    .from(ACCOUNT);

// 搜索 Case
QueryWrapper.create()
    .select(
        ACCOUNT.ID,
        case_()
            .when(ACCOUNT.AGE.ge(60)).then("老年")
            .when(ACCOUNT.AGE.ge(40)).then("中年")
            .when(ACCOUNT.AGE.ge(18)).then("青年")
            .else_("未成年")
            .end()
            .as("ageGroup")
    )
    .from(ACCOUNT);
```

## 分组与过滤

### Group By

```java
QueryWrapper query = QueryWrapper.create()
    .select(
        ACCOUNT.DEPT_ID,
        count().as("empCount"),
        avg(ACCOUNT.SALARY).as("avgSalary")
    )
    .from(ACCOUNT)
    .groupBy(ACCOUNT.DEPT_ID);
```

### Having

```java
QueryWrapper query = QueryWrapper.create()
    .select(
        ACCOUNT.DEPT_ID,
        count().as("empCount")
    )
    .from(ACCOUNT)
    .groupBy(ACCOUNT.DEPT_ID)
    .having(count().ge(5));
```

## Exists 与 Not Exists

```java
// Exists
QueryWrapper query = QueryWrapper.create()
    .select().from(ACCOUNT)
    .where(exists(
        QueryWrapper.create()
            .select().from(ARTICLE)
            .where(ARTICLE.ACCOUNT_ID.eq(ACCOUNT.ID))
    ));

// Not Exists
QueryWrapper query = QueryWrapper.create()
    .select().from(ACCOUNT)
    .where(notExists(
        QueryWrapper.create()
            .select().from(ARTICLE)
            .where(ARTICLE.ACCOUNT_ID.eq(ACCOUNT.ID))
    ));
```

## Union 查询

```java
// Union（去重）：union(QueryWrapper) 每次传入一个查询
QueryWrapper query1 = QueryWrapper.create()
    .select().from(ACCOUNT).where(ACCOUNT.AGE.ge(18));

QueryWrapper query2 = QueryWrapper.create()
    .select().from(ACCOUNT).where(ACCOUNT.DEPT_ID.eq(1));

QueryWrapper query = query1.union(query2);

// Union All（不去重）
QueryWrapper queryAll = query1.unionAll(query2);
```

> **注意**：`union` / `unionAll` 只接受单个 `QueryWrapper` 参数
> （mybatis-flex-core/src/main/java/com/mybatisflex/core/query/QueryWrapper.java:610、618），
> **没有 `union(List<QueryWrapper>)` 重载**；多个 UNION 请链式调用 `query1.union(q2).union(q3)`。

## 自定义排序

```java
// CASE WHEN 排序
QueryWrapper query = QueryWrapper.create()
    .select().from(ACCOUNT)
    .orderBy(
        case_(ACCOUNT.STATUS)
            .when(1).then(0)
            .when(0).then(1)
            .end()
            .asc()
    );
```

## With ROLLUP

**1.11.8 的 `QueryWrapper` 没有 `withRollup()` 方法**（对 mybatis-flex-core 全量检索无任何 ROLLUP 相关 API）。
需要 `GROUP BY ... WITH ROLLUP` 时请改用原生 SQL（`@Select` 注解或 XML），不要调用不存在的方法。

## FOR UPDATE

```java
QueryWrapper query = QueryWrapper.create()
    .select().from(ACCOUNT)
    .where(ACCOUNT.ID.eq(1))
    .forUpdate();
```

## Distinct 去重查询

`QueryWrapper` 和 `QueryColumn` 上**没有 `distinct()` 方法**；去重列使用
`QueryMethods.distinct(...)`（mybatis-flex-core/src/main/java/com/mybatisflex/core/query/QueryMethods.java:2359、2364，
需静态导入 `com.mybatisflex.core.query.QueryMethods`）。

```java
import static com.mybatisflex.core.query.QueryMethods.*;

// 基础 distinct
QueryWrapper query = QueryWrapper.create()
    .select(distinct(ACCOUNT.DEPT_ID))
    .from(ACCOUNT);

// 多列去重
QueryWrapper query = QueryWrapper.create()
    .select(distinct(ACCOUNT.DEPT_ID, ACCOUNT.SEX))
    .from(ACCOUNT);
```

> **注意**：`COUNT(DISTINCT col)` 没有专用封装，可用原生列
> `column("COUNT(DISTINCT dept_id)")`（QueryMethods.column，QueryMethods.java:2444 起）或原生 SQL 实现。

## Select 别名（as）

```java
// 字段别名
QueryWrapper query = QueryWrapper.create()
    .select(
        ACCOUNT.ID.as("accountId"),
        ACCOUNT.USER_NAME.as("userName")
    )
    .from(ACCOUNT);

// 表别名
QueryWrapper query = QueryWrapper.create()
    .select(ACCOUNT.ALL_COLUMNS)
    .from(ACCOUNT.as("a"))
    .where(ACCOUNT.AGE.ge(18));

// 关联查询时，字段映射到 DTO 的属性
QueryWrapper query = QueryWrapper.create()
    .select(ARTICLE.ALL_COLUMNS)
    .select(
        ACCOUNT.USER_NAME.as(ArticleDTO::getAuthorName),
        ACCOUNT.AGE.as(ArticleDTO::getAuthorAge)
    )
    .from(ARTICLE)
    .leftJoin(ACCOUNT).on(ARTICLE.ACCOUNT_ID.eq(ACCOUNT.ID));

List<ArticleDTO> results = mapper.selectListByQueryAs(query, ArticleDTO.class);
```

## limit...offset 分页

MyBatis-Flex 会自动识别数据库类型，生成对应的方言 SQL。

```java
QueryWrapper query = QueryWrapper.create()
    .select().from(ACCOUNT)
    .orderBy(ACCOUNT.ID.desc())
    .limit(10)
    .offset(20);
```

各数据库生成的 SQL：
- **MySQL**: `SELECT * FROM tb_account ORDER BY id DESC LIMIT 20, 10`
- **PostgreSQL**: `SELECT * FROM tb_account ORDER BY id DESC LIMIT 20 OFFSET 10`
- **Oracle**: 内部自动转换为 ROWNUM 方式

## last() 追加 SQL

**1.11.8 的 `QueryWrapper` 没有 `last()` 方法**（对 mybatis-flex-core 全量检索无该方法）。
末尾追加 SQL 的官方能力只有内置的锁定子句：

```java
// FOR UPDATE / FOR UPDATE NOWAIT（QueryWrapper.java:626、631）
QueryWrapper query = QueryWrapper.create()
    .select().from(ACCOUNT)
    .where(ACCOUNT.ID.eq(1))
    .forUpdate();
```

其他"末尾追加 SQL"的场景（如 LIMIT 1）请使用 `limit()` / `offset()`
（mybatis-flex-core/src/main/java/com/mybatisflex/core/query/QueryWrapper.java:815、824），
或改用原生 SQL；不要臆造 `last("...")` 拼接方法。

## QueryWrapper 克隆

使用 `clone()` 方法可以深度复制 QueryWrapper，修改克隆对象不会影响原始对象。

```java
QueryWrapper queryWrapper = QueryWrapper.create()
    .from(ACCOUNT)
    .where(ACCOUNT.ID.eq(1));

QueryWrapper clone = queryWrapper.clone();

// 清空 SELECT 语句
CPI.setSelectColumns(clone, null);
// 重新设置 SELECT 语句
clone.select(ACCOUNT.ID, ACCOUNT.USER_NAME);

System.out.println(queryWrapper.toSQL());
// 输出: SELECT * FROM tb_account WHERE id = 1

System.out.println(clone.toSQL());
// 输出: SELECT id, user_name FROM tb_account WHERE id = 1
```

## CTE 公共表表达式（WITH 子句）

### with...select

```java
QueryWrapper query = new QueryWrapper()
    .with("CTE").asSelect(
        select().from(ARTICLE).where(ARTICLE.ID.ge(100))
    )
    .select().from(ACCOUNT)
    .where(ACCOUNT.SEX.eq(1));

// SQL: WITH CTE AS (SELECT * FROM tb_article WHERE id >= 100)
//      SELECT * FROM tb_account WHERE sex = 1
```

### withRecursive...select

```java
QueryWrapper query = new QueryWrapper()
    .withRecursive("CTE").asSelect(
        select().from(ARTICLE).where(ARTICLE.ID.ge(100))
    )
    .select().from(ACCOUNT)
    .where(ACCOUNT.SEX.eq(1));

// SQL: WITH RECURSIVE CTE AS (SELECT * FROM tb_article WHERE id >= 100)
//      SELECT * FROM tb_account WHERE sex = 1
```

### 多个 CTE

```java
QueryWrapper query = new QueryWrapper()
    .withRecursive("CTE").asSelect(
        select().from(ARTICLE).where(ARTICLE.ID.ge(100))
    )
    .with("xxx", "id", "name").asValues(
        Arrays.asList("a", "b"),
        union(select().from(ARTICLE).where(ARTICLE.ID.ge(200)))
    )
    .select().from(ACCOUNT)
    .where(ACCOUNT.SEX.eq(1));

// SQL: WITH RECURSIVE
//          CTE AS (SELECT * FROM tb_article WHERE id >= 100),
//          xxx(id, name) AS (VALUES (a, b) UNION (SELECT * FROM tb_article WHERE id >= 200))
//      SELECT * FROM tb_account WHERE sex = 1
```

### CTE 内的逻辑删除/租户条件（必须手写）

`TableInfo.appendConditions` 的自动条件追加**不遍历 `With` 结构**（1.11.8）：CTE 查询体只在 SQL 渲染期输出
（`CPI.getWith` 仅被 `CommonsDialectImpl.java:444` 消费），条件追加阶段访问不到。因此 `with`/`withRecursive`
+ `asSelect` 的查询体——锚定段、递归段、`unionAll` 各分支——里每张带逻辑删除/租户列的表都要手写条件
（如 `deleted = 0`）；主查询侧的表仍自动附加。子查询（where/having/EXISTS）与 join 不受此影响，会自动附加。

```java
// 示意：tb_article 带逻辑删除列 is_delete
QueryWrapper query = new QueryWrapper()
    .withRecursive("CTE").asSelect(
        QueryWrapper.create().select().from(ARTICLE)
            .where(ARTICLE.ID.ge(100)
                .and(ARTICLE.IS_DELETE.eq(0)))   // 手写：CTE 内不自动附加逻辑删除条件
    )
    .select().from(ACCOUNT)
    .where(ACCOUNT.SEX.eq(1));                   // 主表自动附加 is_delete = 0
```

完整覆盖范围与源码位置见 `references/07-core-features.md` 逻辑删除章节。

## or/and 嵌套条件组合

### 基础嵌套

```java
// SQL: WHERE id >= 100 AND (sex = 1 OR sex = 2)
QueryWrapper query = QueryWrapper.create()
    .select().from(ACCOUNT)
    .where(ACCOUNT.ID.ge(100))
    .and(ACCOUNT.SEX.eq(1).or(ACCOUNT.SEX.eq(2)));
```

### 复杂嵌套

```java
// SQL: WHERE id >= 100
//      AND (sex = 1 OR sex = 2)
//      OR (age IN (18,19,20) AND user_name LIKE '%michael%')
QueryWrapper query = QueryWrapper.create()
    .select().from(ACCOUNT)
    .where(ACCOUNT.ID.ge(100))
    .and(ACCOUNT.SEX.eq(1).or(ACCOUNT.SEX.eq(2)))
    .or(ACCOUNT.AGE.in(18, 19, 20).and(ACCOUNT.USER_NAME.like("michael")));
```

### Lambda 方式嵌套

```java
QueryWrapper query = QueryWrapper.create()
    .select().from(ACCOUNT)
    .where(ACCOUNT.ID.ge(100))
    .and(wrapper -> wrapper.where(Account::getId).ge(100)
        .or(Account::getUserName).like("michael"));
```

## QueryColumnBehavior 全局配置

### 自动忽略空值

```java
// 全局配置：null 值自动忽略
QueryColumnBehavior.setIgnoreFunction(val -> val == null);

// 配置后，以下条件自动忽略
QueryWrapper.create().select().from(ACCOUNT)
    .where(ACCOUNT.USER_NAME.like(null));  // 该条件被忽略
```

### 智能 in 转 equals

```java
// 当集合只有 1 个元素时，自动将 IN 转为 =
QueryColumnBehavior.setSmartConvertInToEquals(true);

List<Integer> ids = Arrays.asList(1);
QueryWrapper qw = QueryWrapper.create().select().from(ACCOUNT)
    .where(ACCOUNT.ID.in(ids));
// SQL: SELECT * FROM tb_account WHERE id = 1

List<Integer> ids2 = Arrays.asList(1, 2, 3);
QueryWrapper qw2 = QueryWrapper.create().select().from(ACCOUNT)
    .where(ACCOUNT.ID.in(ids2));
// SQL: SELECT * FROM tb_account WHERE id IN (1, 2, 3)
```

## toSQL() 调试

使用 `toSQL()` 方法可以查看 QueryWrapper 生成的 SQL 语句，便于调试。
注意 `toSQL()` 会把参数值替换进 SQL（`SqlUtil.replaceSqlParams`，
mybatis-flex-core/src/main/java/com/mybatisflex/core/util/SqlUtil.java:121），
字符串参数会带上单引号。

⚠️ **陷阱（设计行为，非 bug）**：`toSQL()` 直接走 `DialectFactory.getDialect().forSelectByQuery(this)`
（`QueryWrapper.java:2666-2669`），**不经过** `EntitySqlProvider.appendTableConditions`，输出**不含**逻辑删除/
租户/乐观锁自动条件。测试**禁止用 `toSQL()` 断言 `deleted = 0`**（断言到的只会是手写条件）；验证自动条件请走
真实执行路径（Mapper/Db 查询）或看 SQL 日志。详见 `references/11b-source-api.md` toSQL 说明。

```java
QueryWrapper query = QueryWrapper.create()
    .select().from(ACCOUNT)
    .where(ACCOUNT.ID.ge(100))
    .and(ACCOUNT.USER_NAME.like("michael"));

System.out.println(query.toSQL());
// 输出: SELECT * FROM tb_account WHERE id >= 100 AND user_name LIKE 'michael'
```
