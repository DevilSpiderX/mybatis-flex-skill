# UpdateChain 链式更新

`UpdateChain` 用于 MyBatis-Flex 链式更新和删除。官网示例中常见写法是：

```java
UpdateChain.of(Account.class)
    .set(Account::getUserName, "张三")
    .setRaw(Account::getAge, "age + 1")
    .where(Account::getId).eq(1)
    .update();
```

生成语义类似：

```sql
UPDATE `tb_account` SET `user_name` = ? , `age` = age + 1
WHERE `id` = ?
```

## 何时优先使用

- 用户要求链式更新、动态更新、只更新传入字段、字段非空才更新时，优先考虑 `UpdateChain`。
- 已有 `where` 条件明确、更新字段较少、需要 `setRaw` 做原子增减时，优先考虑 `UpdateChain`。
- 需要区分“未传字段 / 传了 null / 传了值”时，优先结合 `OptionalField` 或 `UpdateEntity`，不要只靠普通 null 判空。

## 条件 set

`UpdateChain` 的 `set` 和 `setRaw` 支持第三个条件参数；当条件为 `false` 时，该字段不参与更新。条件参数支持三种形式：

- `boolean isEffective`
- `BooleanSupplier isEffective`
- `Predicate<V> isEffective`

```java
UpdateChain.of(Account.class)
    .set(Account::getUserName, dto.getUserName(), If::hasText)
    .set(Account::getAge, dto.getAge(), If::notNull)
    .where(Account::getId).eq(id)
    .update();
```

也可以使用 APT 生成的 `TableDef` 字段：

```java
UpdateChain.of(Account.class)
    .set(ACCOUNT.USER_NAME, dto.getUserName(), If::hasText)
    .set(ACCOUNT.AGE, dto.getAge(), If::notNull)
    .set(ACCOUNT.UPDATE_TIME, LocalDateTime.now(), true)
    .where(ACCOUNT.ID.eq(id))
    .update();
```

## 字符串判空

根据业务语义选择判空条件：

```java
// 空字符串代表“不更新”
UpdateChain.of(Account.class)
    .set(Account::getUserName, dto.getUserName(), If::hasText)
    .where(Account::getId).eq(id)
    .update();

// 空字符串是合法值，只跳过 null
UpdateChain.of(Account.class)
    .set(Account::getUserName, dto.getUserName(), If::notNull)
    .where(Account::getId).eq(id)
    .update();

// 只在空白字符串时才写入默认值
UpdateChain.of(Account.class)
    .set(Account::getUserName, "匿名用户", If.noText(dto.getUserName()))
    .where(Account::getId).eq(id)
    .update();
```

不要默认把 `If::hasText` 套到所有字符串字段；先确认空字符串是否有业务含义。

## If 条件速查

`If` 来自 `com.mybatisflex.core.query.If`。

| 方法 | 语义 | 适用场景 |
|------|------|----------|
| `If::hasText` | 字符串有非空白文本才生效 | 表单输入有值才更新 |
| `If::noText` | 字符串为空或空白才生效 | 为空时写默认值 |
| `If::notNull` | 对象非 null 才生效 | 普通对象、数字、日期、空字符串合法值 |
| `If::isNull` | 对象为 null 才生效 | 为空时写默认值 |
| `If::notEmpty` | 集合、数组、Map 非空才生效 | 批量字段、JSON 数组字段 |
| `If::isEmpty` | 集合、数组、Map 为空才生效 | 为空时写默认集合或标记 |

```java
UpdateChain.of(KnowledgeDocument.class)
    .set(KNOWLEDGE_DOCUMENT.METADATA_JSON, document.getMetadataJson(), If::hasText)
    .set(KNOWLEDGE_DOCUMENT.UPDATE_USER, document.getUpdateUser(), If::notNull)
    .set(KNOWLEDGE_DOCUMENT.UPDATE_TIME, LocalDateTime.now(), () -> document.getId() != null)
    .where(KNOWLEDGE_DOCUMENT.ID.eq(document.getId()))
    .update();
```

## set 与 setRaw

- `set(field, value)` 用参数绑定，适合普通值更新。
- `setRaw(field, rawSql)` 直接拼接 SQL 片段，适合 `age + 1`、`now()`、数据库函数、子查询等场景。
- `setRaw` 不接收用户输入直拼；如必须使用，先限制白名单或改用参数化方案。

```java
UpdateChain.of(Account.class)
    .set(Account::getUserName, dto.getUserName(), If::hasText)
    .setRaw(Account::getAge, "age + 1", dto::isIncreaseAge)
    .where(Account::getId).eq(id)
    .update();
```

## 与 UpdateEntity 的边界

`UpdateChain` 适合在调用点明确列出更新字段。若 DTO 需要表达三态语义：

- `MISSING`：不更新
- `VALUE`：更新为具体值
- `NULL`：显式更新为 `null`

优先阅读 `references/12-optional-field.md`，使用 `OptionalField` 或 `UpdateEntity`，避免普通 `dto.getX() != null` 把“传了 null”误判成“不更新”。
