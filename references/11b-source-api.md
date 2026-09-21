# MyBatis-Flex 核心源码解析 — 查询（QueryWrapper / 链式查询）

> 源码位置：`QueryWrapper`（com/mybatisflex/core/query/QueryWrapper.java:34，`extends BaseQueryWrapper<QueryWrapper>`）、`BaseQueryWrapper`（BaseQueryWrapper.java:26）、`QueryWrapperAdapter`（QueryWrapperAdapter.java:36）、`ChainQuery`（ChainQuery.java:38）、`MapperQueryChain`（MapperQueryChain.java:44）、`QueryChain`（QueryChain.java:30）。版本基线 1.11.8。

## QueryWrapper - 核心查询方法

> 源码位置：QueryWrapper.java L34-2684；`create()` 系列工厂方法在 L36-81；MyBatis-Plus 兼容 WHERE 方法在 L850-2116；JOIN 方法在 L442-608；`groupBy`/`having`/`orderBy` 在 L661-762；`limit`/`offset`/`datasource`/`hint` 在 L815-847；`toSQL()` 在 L2666。

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

以上每个方法都有 `String` 列名与 `LambdaGetter` 两种形式，并配有带 `isEffective` 参数的重载，但**不同方法组支持的重载形式并不相同**（源码 QueryWrapper.java）：

- 带值条件（`eq`/`ne`/`gt`/`ge`/`lt`/`le`/`like`/`likeLeft`/`likeRight`/`notLike`）：`boolean` 与 `Predicate<V>`（以 `eq` 为例，L858-924）；
- `between`/`notBetween`：`boolean` 与 `BooleanSupplier`（L1693-1842，如 `between(String, Object, Object, boolean)` L1717、`notBetween(String, Object, Object, BooleanSupplier)` L1828）；
- `in`/`notIn`：`boolean` 与 `BooleanSupplier`，但 `BooleanSupplier` 仅出现在子查询（`QueryWrapper` 值）形式上（`in` L1484-1498、`notIn` L1664-1678），`Object[]`/`Collection` 值形式只有 `boolean`（如 `in(String, Object[], boolean)` L1402）；
- `isNull`/`isNotNull`：`boolean` 与 `BooleanSupplier`（L2329-2394、L2402-2462）。

配合 `If` 工具类可实现动态条件控制（详见 **11d-source-api.md — If 条件判断工具类**）。注意 `QueryColumn` 侧的对应签名略有差异：`between` 的条件参数是 `BiPredicate` 而非 `Predicate`（QueryColumn.java:586）。

### JOIN 方法

> 源码位置：QueryWrapper.java L442-608。每个 JOIN 都有 `QueryTable` / `String` / `Class<?>` / `QueryWrapper` 四类入参重载，以及带 `boolean when` 的动态重载；返回 `Joiner<Q>` 用于继续拼接 `ON` 条件。

| 方法 | 说明 |
|------|------|
| `leftJoin(table)` | LEFT JOIN |
| `rightJoin(table)` | RIGHT JOIN |
| `innerJoin(table)` | INNER JOIN |
| `fullJoin(table)` | FULL JOIN |
| `crossJoin(table)` | CROSS JOIN |
| `join(table)` | JOIN |

### 其他方法

> 源码位置：`groupBy` L661-695、`having` L697、`orderBy` L716-762、`limit`/`offset` L815-837、`datasource` L839、`hint` L844、`union`/`unionAll` L610-624、`forUpdate` L626、`toSQL` L2666。

| 方法 | 说明 |
|------|------|
| `groupBy(col)` | 分组 |
| `having(condition)` | HAVING 条件 |
| `orderBy(col, asc)` | 排序（支持动态 Boolean，`asc` 为 `null` 时不排序） |
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

> 源码位置：ChainQuery.java L38-110。`one()`、`oneAs()`、`list()`、`listAs()`、`page()`、`pageAs()` 为接口抽象方法；`oneOpt()`、`oneAsOpt()` 为 `default` 方法。

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

> 源码位置：MapperQueryChain.java L44-216，`public interface MapperQueryChain<T> extends ChainQuery<T>`。

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

> 源码位置：QueryChain.java L30-64，`public class QueryChain<T> extends QueryWrapperAdapter<QueryChain<T>> implements MapperQueryChain<T>`。

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

// 关联查询（Relations Query：QueryChain 本身没有 listWithRelationsAs 方法，
// 需通过 withRelations() 拿到 RelationsBuilder 后再调用 listAs）
List<AccountVO> list = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.AGE.ge(18))
    .withRelations()
    .listAs(AccountVO.class);
```

> 类继承关系图和参考来源见 [11-source-api.md](11-source-api.md)。
