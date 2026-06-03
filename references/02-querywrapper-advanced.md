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
        concat(ACCOUNT.USER_NAME, " - ", ACCOUNT.AGE),
        substring(ACCOUNT.USER_NAME, 1, 3)
    )
    .from(ACCOUNT);

// 日期函数
QueryWrapper.create()
    .select(
        year(ACCOUNT.BIRTHDAY),
        month(ACCOUNT.BIRTHDAY),
        day(ACCOUNT.BIRTHDAY),
        curdate(),
        now()
    )
    .from(ACCOUNT);

// 条件函数
QueryWrapper.create()
    .select(
        coalesce(ACCOUNT.NICK_NAME, ACCOUNT.USER_NAME),
        if_(ACCOUNT.AGE.ge(18), "成年", "未成年"),
        nullif(ACCOUNT.AGE, 0)
    )
    .from(ACCOUNT);

// 格式化
QueryWrapper.create()
    .select(
        format(ACCOUNT.SALARY, 2),
        round(ACCOUNT.SCORE, 2),
        floor(ACCOUNT.SCORE),
        ceil(ACCOUNT.SCORE),
        abs(ACCOUNT.BALANCE)
    )
    .from(ACCOUNT);
```

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
// Union（去重）
QueryWrapper query1 = QueryWrapper.create()
    .select().from(ACCOUNT).where(ACCOUNT.AGE.ge(18));
    
QueryWrapper query2 = QueryWrapper.create()
    .select().from(ACCOUNT).where(ACCOUNT.DEPT_ID.eq(1));

List<QueryWrapper> unions = new ArrayList<>();
unions.add(query2);
QueryWrapper query = query1.union(unions);

// Union All（不去重）
QueryWrapper query = query1.unionAll(unions);
```

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

```java
QueryWrapper query = QueryWrapper.create()
    .select(ACCOUNT.DEPT_ID, ACCOUNT.AGE, count())
    .from(ACCOUNT)
    .groupBy(ACCOUNT.DEPT_ID, ACCOUNT.AGE)
    .withRollup();
```

## FOR UPDATE

```java
QueryWrapper query = QueryWrapper.create()
    .select().from(ACCOUNT)
    .where(ACCOUNT.ID.eq(1))
    .forUpdate();
```
