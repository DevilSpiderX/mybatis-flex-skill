# MyBatis-Flex 核心源码解析 — 更新（PropertySetter / UpdateWrapper / UpdateChain）

## PropertySetter - 属性设置接口

`PropertySetter<R>` 是通用的属性设置接口，定义了 `set` 和 `setRaw` 方法族，供 `UpdateChain` 和 `UpdateWrapper` 共享。支持三种属性引用方式：**字符串名**、**QueryColumn**、**LambdaGetter**。

### set vs setRaw 区别

| 方法 | 说明 | 值处理 |
|------|------|--------|
| `set(property, value)` | 设置字段参数值 | 普通值直接绑定；若 value 为 `QueryWrapper`/`QueryColumn`/`QueryCondition`，自动包装为 `RawValue` |
| `setRaw(property, value)` | 设置字段原生值 | 始终包装为 `RawValue`，不走参数占位符，直接拼入 SQL |

### 属性引用方式

```java
// 1. 字符串属性名
.set("user_name", "张三")

// 2. QueryColumn
.set(ACCOUNT.USER_NAME, "张三")

// 3. LambdaGetter（类型安全）
.set(Account::getUserName, "张三")
```

### 条件生效控制（isEffective）

每个 `set`/`setRaw` 方法都有以下重载：

| 重载形式 | 说明 |
|----------|------|
| `set(prop, value)` | 无条件生效（`isEffective = true`） |
| `set(prop, value, boolean)` | 布尔值控制是否生效 |
| `set(prop, value, BooleanSupplier)` | 通过 `Supplier` 懒求值控制 |
| `set(prop, value, Predicate<V>)` | 通过 `Predicate` 对值本身做判断 |

```java
// 仅当 value 不为空时生效（使用 If 工具类）
.set("name", name, If::notNull)

// 仅当集合不为空时生效
.set("ids", ids, If::notEmpty)

// 仅当字符串有文本时生效
.set("keyword", keyword, If::hasText)

// 仅当 Predicate 为 true 时生效
.set("age", age, v -> v > 0)

// 通过 BooleanSupplier 懒求值
.set("status", status, () -> someCondition())
```

---

## UpdateWrapper - 更新包装器接口

`UpdateWrapper<T>` 是实体代理对象的更新接口，继承 `PropertySetter<UpdateWrapper<T>>`，同时实现 `Serializable`。

### 核心机制

`UpdateWrapper` 通过代理对象（Javassist `ProxyObject` 或 `Proxy`）获取 `ModifyAttrsRecordHandler`，从而维护一个 `Map<String, Object>` 存储待更新字段。

### set 方法自动识别

```java
// 普通值 → 直接存入 map
wrapper.set("name", "张三")          // map.put("name", "张三")

// RawValue 类型 → 自动包装为 RawValue（SQL 片段，不走参数占位符）
wrapper.set("age", QueryColumn)      // map.put("age", new RawValue(value))
wrapper.set("age", QueryWrapper)     // map.put("age", new RawValue(value))
wrapper.set("age", QueryCondition)   // map.put("age", new RawValue(value))
```

### setRaw 始终为 RawValue

```java
// 所有 setRaw 调用都直接包装为 RawValue
wrapper.setRaw("total", "price * quantity")  // map.put("total", new RawValue("price * quantity"))
```

### 创建方式

```java
// 从已有实体对象获取
UpdateWrapper<Account> wrapper = UpdateWrapper.of(account);

// 从 Class 创建空代理
UpdateWrapper<Account> wrapper = UpdateWrapper.of(Account.class);
```

### 关键方法

| 方法 | 返回类型 | 说明 |
|------|----------|------|
| `getUpdates()` | `Map<String, Object>` | 获取所有待更新的字段-值映射 |
| `set(prop, value, isEffective)` | `UpdateWrapper<T>` | 设置字段值（自动识别 RawValue） |
| `setRaw(prop, value, isEffective)` | `UpdateWrapper<T>` | 设置原生 SQL 值 |
| `toEntity()` | `T` | 返回实体对象本身（`this`） |

---

## UpdateChain - 数据更新/删除链式操作

`UpdateChain<T>` 继承 `QueryWrapperAdapter<UpdateChain<T>>`，实现 `PropertySetter<UpdateChain<T>>`，用于链式构建 UPDATE 和 DELETE 语句。

### 创建方式

```java
// 通过实体类
UpdateChain.of(Account.class)

// 通过 Mapper
UpdateChain.of(accountMapper)

// 通过实体对象（已有数据）
UpdateChain.of(accountObject)

// 通过实体对象 + Mapper
UpdateChain.of(accountObject, accountMapper)
```

### UPDATE 链式操作

```java
// 基础更新
boolean success = UpdateChain.of(Account.class)
    .set(Account::getUserName, "新名字")
    .set(Account::getAge, 25)
    .where(Account::getId, 1)
    .update();

// 条件生效控制
boolean success = UpdateChain.of(Account.class)
    .set("user_name", name, If::notNull)       // name 不为 null 才更新
    .set("age", age, v -> v > 0)                // age 大于 0 才更新
    .set("keyword", keyword, If::hasText)       // keyword 非空才更新
    .where(ACCOUNT.ID.eq(1))
    .update();

// 原生 SQL 值
boolean success = UpdateChain.of(Account.class)
    .setRaw("total", "price * quantity")
    .where(ACCOUNT.ID.eq(1))
    .update();

// 动态条件
boolean success = UpdateChain.of(Account.class)
    .set(Account::getStatus, 1)
    .where(ACCOUNT.AGE.ge(18))
    .and(ACCOUNT.STATUS.eq(0))
    .update();
```

### DELETE 链式操作

```java
// 通过条件删除
boolean success = UpdateChain.of(Account.class)
    .where(ACCOUNT.STATUS.eq(-1))
    .remove();

// Lambda 方式
boolean success = UpdateChain.of(Account.class)
    .where(Account::getStatus, -1)
    .remove();
```

### 核心方法

| 方法 | 返回类型 | 说明 |
|------|----------|------|
| `set(prop, value, isEffective)` | `UpdateChain<T>` | 设置要更新的字段值 |
| `setRaw(prop, value, isEffective)` | `UpdateChain<T>` | 设置原生 SQL 值 |
| `update()` | `boolean` | 执行 UPDATE 操作 |
| `remove()` | `boolean` | 执行 DELETE 操作 |
| `toSQL()` | `String` | 生成 SQL（调试用） |

### 继承自 QueryWrapperAdapter 的方法

`UpdateChain` 继承了所有查询条件方法，可直接用于 `WHERE` 子句：

```java
UpdateChain.of(Account.class)
    .set(Account::getStatus, 0)
    .where(ACCOUNT.AGE.ge(18))        // 来自 QueryWrapperAdapter
    .and(ACCOUNT.STATUS.eq(1))         // 来自 QueryWrapperAdapter
    .or(ACCOUNT.NAME.like("test"))   // 来自 QueryWrapperAdapter
    .update();
```

### toSQL 调试

```java
String sql = UpdateChain.of(Account.class)
    .set(Account::getUserName, "test")
    .set(Account::getAge, 25)
    .where(ACCOUNT.ID.eq(1))
    .toSQL();
// 输出类似: UPDATE tb_account SET user_name = 'test', age = 25 WHERE id = 1
```

> 类继承关系图和参考来源见 [11-source-api.md](11-source-api.md)。
