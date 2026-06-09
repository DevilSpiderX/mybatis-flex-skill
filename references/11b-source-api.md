# MyBatis-Flex 核心源码解析 — 查询（QueryWrapper / 链式查询）

## QueryWrapper - 核心查询方法

### 创建方式

```java
// 空 QueryWrapper
QueryWrapper.create()

// 根据实体类自动构建条件
QueryWrapper.create(entity)

// 根据 Map 构建条件
QueryWrapper.create(map)
```

### WHERE 条件方法

源码中 `QueryWrapper` 提供了以下 MyBatis-Plus 兼容方法：

| 方法 | SQL | 说明 |
|------|-----|------|
| `eq(col, val)` | `col = val` | 等于 |
| `ne(col, val)` | `col != val` | 不等于 |
| `gt(col, val)` | `col > val` | 大于 |
| `ge(col, val)` | `col >= val` | 大于等于 |
| `lt(col, val)` | `col < val` | 小于 |
| `le(col, val)` | `col <= val` | 小于等于 |
| `in(col, values)` | `col IN (...)` | IN 查询 |
| `notIn(col, values)` | `col NOT IN (...)` | NOT IN |
| `between(col, start, end)` | `col BETWEEN x AND y` | 范围查询 |
| `notBetween(col, start, end)` | `col NOT BETWEEN x AND y` | 范围排除 |
| `like(col, val)` | `col LIKE %val%` | 模糊匹配 |
| `likeLeft(col, val)` | `col LIKE val%` | 左模糊 |
| `likeRight(col, val)` | `col LIKE %val` | 右模糊 |
| `notLike(col, val)` | `col NOT LIKE %val%` | 模糊排除 |
| `isNull(col)` | `col IS NULL` | 空值判断 |
| `isNotNull(col)` | `col IS NOT NULL` | 非空判断 |

每个方法都有带 `isEffective` 参数的重载，支持 `boolean`、`BooleanSupplier`、`Predicate<V>` 三种形式，配合 `If` 工具类可实现动态条件控制（详见上方 **If - 条件判断工具类** 章节）。

### JOIN 方法

| 方法 | 说明 |
|------|------|
| `leftJoin(table)` | LEFT JOIN |
| `rightJoin(table)` | RIGHT JOIN |
| `innerJoin(table)` | INNER JOIN |
| `fullJoin(table)` | FULL JOIN |
| `crossJoin(table)` | CROSS JOIN |
| `join(table)` | JOIN |

### 其他方法

| 方法 | 说明 |
|------|------|
| `groupBy(col)` | 分组 |
| `having(condition)` | HAVING 条件 |
| `orderBy(col, asc)` | 排序（支持动态 Boolean） |
| `limit(rows)` | 限制行数 |
| `offset(offset)` | 偏移量 |
| `union(wrapper)` | UNION |
| `unionAll(wrapper)` | UNION ALL |
| `forUpdate()` | FOR UPDATE 锁 |
| `datasource(key)` | 指定数据源 |
| `hint(sql)` | SQL 提示 |
| `toSQL()` | 调试：查看生成的 SQL |

---

## ChainQuery - 链式查询接口

`ChainQuery<T>` 是链式查询的基础接口，定义了通用查询方法：

| 方法 | 返回类型 | 说明 |
|------|----------|------|
| `one()` | `T` | 查询单条 |
| `oneOpt()` | `Optional<T>` | 查询单条（Optional） |
| `oneAs(type)` | `<R>` | 查询单条并转换类型 |
| `oneAsOpt(type)` | `Optional<R>` | 查询单条并转换（Optional） |
| `list()` | `List<T>` | 查询列表 |
| `listAs(type)` | `List<R>` | 查询列表并转换 |
| `page(page)` | `Page<T>` | 分页查询 |
| `pageAs(page, type)` | `Page<R>` | 分页查询并转换 |

---

## MapperQueryChain - Mapper 链式查询

`MapperQueryChain<T>` 继承 `ChainQuery`，扩展了更多方法：

| 方法 | 返回类型 | 说明 |
|------|----------|------|
| `baseMapper()` | `BaseMapper<T>` | 获取 Mapper |
| `toQueryWrapper()` | `QueryWrapper` | 转换为 QueryWrapper |
| `count()` | `long` | 查询数量 |
| `exists()` | `boolean` | 判断是否存在 |
| `obj()` | `Object` | 获取第一列第一条数据 |
| `objAs(type)` | `<R>` | 获取第一列并转换 |
| `objOpt()` | `Optional<Object>` | 获取第一列（Optional） |
| `objList()` | `List<Object>` | 获取第一列所有数据 |
| `objListAs(type)` | `List<R>` | 获取第一列并转换 |
| `withFields()` | `FieldsBuilder<T>` | Fields 关联查询 |
| `withRelations()` | `RelationsBuilder<T>` | Relations 关联查询 |

---

## QueryChain - QueryWrapper 链式调用

`QueryChain<T>` 继承 `QueryWrapperAdapter`，实现 `MapperQueryChain`，是完整的链式查询实现。

### 创建方式

```java
// 通过实体类
QueryChain.of(Account.class)

// 通过 Mapper
QueryChain.of(accountMapper)
```

### 完整示例

```java
// 基础查询
Account account = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.ID.eq(1))
    .one();

// DTO 转换
AccountVO vo = QueryChain.of(accountMapper)
    .select(ACCOUNT.ID, ACCOUNT.USER_NAME)
    .from(ACCOUNT)
    .where(ACCOUNT.ID.eq(1))
    .oneAs(AccountVO.class);

// 分页查询
Page<Account> page = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.AGE.ge(18))
    .page(Page.of(1, 10));

// 查询单值
String name = (String) QueryChain.of(accountMapper)
    .select(ACCOUNT.USER_NAME)
    .from(ACCOUNT)
    .where(ACCOUNT.ID.eq(1))
    .obj();

// 关联查询
List<AccountVO> list = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.AGE.ge(18))
    .listWithRelationsAs(AccountVO.class);
```

> 类继承关系图和参考来源见 [11-source-api.md](11-source-api.md)。
