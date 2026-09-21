# MyBatis-Flex 核心源码解析 — If 条件判断工具类

> 源码位置：`com.mybatisflex.core.query.If`（mybatis-flex-core/src/main/java/com/mybatisflex/core/query/If.java，L23-89），私有构造的工具类，所有方法均为 `public static`。版本基线 1.11.8。

## If - 条件判断工具类

`If` 是 MyBatis-Flex 提供的条件判断工具类（`com.mybatisflex.core.query.If`），常与 `isEffective` 参数配合使用，实现动态条件控制。

### 方法列表

> 源码位置：`isNull` L31、`notNull` L38、`isEmpty(T[])` L42、`isNotEmpty(T[])` L47（`@Deprecated`）、`notEmpty(T[])` L51、`isEmpty(Map)` L55、`isNotEmpty(Map)` L60（`@Deprecated`）、`notEmpty(Map)` L64、`isEmpty(Collection)` L68、`isNotEmpty(Collection)` L73（`@Deprecated`）、`notEmpty(Collection)` L77、`hasText` L81、`noText` L85。

| 方法 | 说明 | 适用类型 |
|------|------|----------|
| `isNull(obj)` | 判断对象是否为 null | 任意对象 |
| `notNull(obj)` | 判断对象是否非 null | 任意对象 |
| `isEmpty(arr)` | 判断数组是否为空 | `T[]` |
| `notEmpty(arr)` | 判断数组是否非空 | `T[]` |
| `isEmpty(map)` | 判断 Map 是否为空 | `Map` |
| `notEmpty(map)` | 判断 Map 是否非空 | `Map` |
| `isEmpty(collection)` | 判断集合是否为空 | `Collection` |
| `notEmpty(collection)` | 判断集合是否非空 | `Collection` |
| `hasText(str)` | 判断字符串是否有文本（非 null、非空、非空白） | `String` |
| `noText(str)` | 判断字符串是否无文本 | `String` |

> **注意**：`isNotEmpty` 系列方法已标记为 `@Deprecated`，请使用 `notEmpty` 替代。
>
> `hasText` / `noText` 委托给 `StringUtil.hasText` / `StringUtil.noText`（StringUtil.java:176、L208），语义为"非 null、非空串、且不全为空白字符"。

### 典型用法

```java
// 配合 UpdateChain / PropertySetter 的 Predicate 重载
// （PropertySetter.set(String, V, Predicate<V>)，PropertySetter.java:71）
UpdateChain.of(Account.class)
    .set(ACCOUNT.NAME, name, If::notNull)              // name 非 null 才更新
    .set(ACCOUNT.TAGS, tags, If::notEmpty)             // tags 集合非空才更新
    .set(ACCOUNT.KEYWORD, keyword, If::hasText)        // keyword 有文本才更新
    .where(ACCOUNT.ID.eq(1))
    .update();

// 配合 QueryColumn 的条件重载（QueryColumn.java:153-168 / 644-672 / 570-588）
QueryWrapper.create()
    .and(ACCOUNT.NAME.like(keyword, If::hasText))   // like(T, Predicate<T>)
    .and(ACCOUNT.STATUS.eq(status, If::notNull))    // eq(T, Predicate<T>)
    // between 的条件参数是 BiPredicate 而非 Predicate（QueryColumn.java:586）
    .and(ACCOUNT.AGE.between(minAge, maxAge, (s, e) -> If.notNull(s) && If.notNull(e)));
```

> `If` 的方法签名都是"单参入、布尔出"，因此可直接作为 `Predicate`/`Function` 引用传入；但不能直接作为 `BooleanSupplier`（无参）或 `BiPredicate`（双参）使用。
