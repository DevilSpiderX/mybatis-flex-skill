# MyBatis-Flex 核心源码解析 — If 条件判断工具类

## If - 条件判断工具类

`If` 是 MyBatis-Flex 提供的条件判断工具类（`com.mybatisflex.core.query.If`），常与 `isEffective` 参数配合使用，实现动态条件控制。

### 方法列表

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

### 典型用法

```java
// 配合 UpdateChain 的 Predicate 重载
UpdateChain.of(Account.class)
    .set(ACCOUNT.NAME, name, If::notNull)              // name 非 null 才更新
    .set(ACCOUNT.TAGS, tags, If::notEmpty)             // tags 集合非空才更新
    .set(ACCOUNT.KEYWORD, keyword, If::hasText)        // keyword 有文本才更新
    .where(ACCOUNT.ID.eq(1))
    .update();

// 配合 QueryWrapper 的 Predicate 重载
QueryWrapper.create()
    .and(ACCOUNT.NAME.like(keyword, If::hasText))
    .and(ACCOUNT.STATUS.eq(status, If::notNull))
    .and(ACCOUNT.AGE.between(minAge, maxAge, If::notNull));
```
