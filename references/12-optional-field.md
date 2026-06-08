# OptionalField 三态值类型

> ⚠️ **前提条件**：使用 `OptionalField` 三态值类型前，必须先确保项目中已引入该类型。源码实现请参考 [12a-optional-field-source.md](12a-optional-field-source.md)。

> OptionalField 是一个自定义的三态值类型，用于处理部分更新场景。它表示字段的三种状态：有值、null、不存在。

## 核心概念

| 状态 | 枚举值 | 含义 | UpdateEntity 行为 |
|------|--------|------|-------------------|
| 有值 | `VALUE` | 字段有实际值 | `set(field, value)` |
| null | `NULL` | 字段存在但为 null | `set(field, null)` |
| 缺失 | `MISSING` | 字段不存在 | 忽略，不调用 set |

## 与 Optional 的区别

| 特性 | Optional | OptionalField |
|------|----------|---------------|
| 状态数量 | 二元（present/absent） | 三态（VALUE/NULL/MISSING） |
| 区分 null 和缺失 | ❌ 不支持 | ✅ 支持 |
| 三分支匹配 | ❌ 不支持 | ✅ 支持（match 方法） |
| 按状态返回默认值 | ❌ 不支持 | ✅ 支持（orElse 双参数） |

## 使用场景

在 REST API 的 PATCH 请求中，区分"字段未传"和"字段传了 null"：

**场景 1：只更新部分字段**
```json
// 只更新 name，age 和 email 不修改（MISSING 状态）
{
  "name": "张三"
}
```

**场景 2：更新字段为 null**
```json
// 更新 name 为 null，email 有值，age 不修改
{
  "name": null,
  "email": "user@example.com"
}
```

**场景 3：更新所有字段**
```json
// 更新所有字段
{
  "name": "王五",
  "age": 25,
  "email": "wangwu@example.com"
}
```

## API 参考

### 创建方法

| 方法 | 说明 | 示例 |
|------|------|------|
| `OptionalField.missing()` | 创建 MISSING 状态 | `OptionalField.missing()` |
| `OptionalField._null()` | 创建 NULL 状态 | `OptionalField._null()` |
| `OptionalField.of(value)` | 创建 VALUE 状态（null 值自动转为 NULL） | `OptionalField.of("hello")` |
| `OptionalField.of(field)` | 包装可能为 null 的 OptionalField | `OptionalField.of(field)` |

### 状态判断

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `isPresent()` | 是否有值（VALUE 状态） | `boolean` |
| `isNull()` | 是否为 NULL 状态 | `boolean` |
| `isMissing()` | 是否为 MISSING 状态 | `boolean` |
| `isEmpty()` | 是否为空（NULL 或 MISSING） | `boolean` |
| `getState()` | 获取当前状态枚举 | `State` |

### 获取值

| 方法 | 说明 |
|------|------|
| `getValue()` | 获取原始值（可能为 null） |
| `orElse(other)` | 获取值，无值时返回默认值 |
| `orElse(nullVal, missingVal)` | 获取值，按 NULL/MISSING 返回不同默认值 |
| `orElseThrow()` | 获取值，无值时抛出 NoSuchElementException |
| `orElseThrow(supplier)` | 获取值，无值时抛出自定义异常 |
| `orElseGet(supplier)` | 获取值，无值时通过 Supplier 延迟计算 |
| `orElseGet(nullSup, missingSup)` | 获取值，按状态通过不同 Supplier 计算 |

### 条件操作

| 方法 | 说明 |
|------|------|
| `ifPresent(action)` | 有值时执行 Consumer |
| `ifNull(action)` | NULL 状态时执行 Runnable |
| `ifMissing(action)` | MISSING 状态时执行 Runnable |
| `ifEmpty(action)` | 为空时执行 Runnable（NULL 或 MISSING） |

### 模式匹配

| 方法签名 | 说明 |
|----------|------|
| `match(Consumer, Runnable)` | 双分支匹配（忽略 MISSING） |
| `match(Consumer, Runnable, Runnable)` | 三分支匹配（无返回值） |
| `match(Function, Supplier, Supplier)` | 三分支匹配（有返回值） |

### 链式转换

| 方法 | 说明 |
|------|------|
| `map(Function)` | 有值时转换，无值时保持状态 |
| `flatMap(Function)` | 有值时展平嵌套 OptionalField |
| `filter(Predicate)` | 有值且满足谓词时保持，否则转为 NULL |
| `stream()` | 转换为 Stream（有值时为单元素流） |

## 使用示例

### 1. 定义 DTO

```java
import com.example.json.lang.OptionalField;
import lombok.Data;

@Data
public class UserUpdateDTO {
    // 不更新 name（MISSING 状态）
    private OptionalField<String> name = OptionalField.missing();
    
    // 更新 age 为 25
    private OptionalField<Integer> age = OptionalField.of(25);
    
    // 更新 email 为 null
    private OptionalField<String> email = OptionalField._null();
}
```

### 2. 状态判断与获取值

```java
OptionalField<String> field = ...;

// 状态判断
if (field.isPresent()) {
    // VALUE 状态
} else if (field.isNull()) {
    // NULL 状态（字段存在但值为 null）
} else if (field.isMissing()) {
    // MISSING 状态（字段不存在）
}

// 或使用 isEmpty() 统一判断
if (field.isEmpty()) {
    // NULL 或 MISSING 状态
}

// 获取值
String value = field.orElse("默认值");

// 区分 NULL 和 MISSING 返回不同默认值
String value = field.orElse("字段为null时的默认值", "字段不存在时的默认值");

// 必须有值时使用
String value = field.orElseThrow();
String value = field.orElseThrow(() -> new BusinessException("name 字段必填"));
```

### 3. 条件操作

```java
OptionalField<String> nickname = user.getOptionalNickname();

// 有值时执行
nickname.ifPresent(name -> log.info("昵称: {}", name));

// NULL 状态时执行
nickname.ifNull(() -> log.warn("昵称字段为 null"));

// MISSING 状态时执行
nickname.ifMissing(() -> log.warn("昵称字段缺失"));

// 为空时执行（NULL 或 MISSING）
nickname.ifEmpty(() -> log.warn("昵称不可用"));
```

### 4. 模式匹配

```java
OptionalField<String> status = record.getOptionalStatus();

// 双分支匹配（忽略 MISSING）
status.match(
    value -> log.info("状态: {}", value),     // VALUE
    () -> log.warn("状态为 null")              // NULL
);

// 三分支匹配
status.match(
    value -> log.info("状态: {}", value),     // VALUE
    () -> log.warn("状态为 null"),             // NULL
    () -> log.warn("状态字段缺失")              // MISSING
);

// 带返回值的三分支匹配
String display = status.match(
    value -> "状态: " + value,                 // VALUE
    () -> "状态未设置",                         // NULL
    () -> "状态字段缺失"                        // MISSING
);
```

### 5. 链式转换

```java
OptionalField<String> email = user.getOptionalEmail();

// map 转换
OptionalField<String> upperEmail = email.map(String::toUpperCase);
String display = upperEmail.orElse("N/A");

// flatMap 展平嵌套
OptionalField<OptionalField<String>> nested = ...;
OptionalField<String> flat = nested.flatMap(Function.identity());

// filter 过滤
OptionalField<String> validEmail = email.filter(e -> e.contains("@"));
// 如果 email 存在但不包含 @，validEmail 变为 NULL 状态
// 如果 email 字段不存在，validEmail 保持 MISSING 状态
```

### 6. Service 层使用

```java
@Service
@RequiredArgsConstructor
public class UserService {
    private final UserMapper userMapper;

    /**
     * 部分更新用户
     */
    public void updateUser(String userId, UserUpdateDTO dto) {
        // 转换 DTO 为 UpdateEntity
        User updateEntity = OptionalDtoUtil.toUpdateEntity(dto, User.class, userId);
        
        // 执行更新
        userMapper.update(updateEntity);
    }
}
```

### 7. Controller 层使用

```java
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;

    /**
     * PATCH 部分更新
     */
    @PatchMapping("/{id}")
    public ResponseEntity<Void> updateUser(
            @PathVariable String id,
            @RequestBody UserUpdateDTO dto) {
        userService.updateUser(id, dto);
        return ResponseEntity.noContent().build();
    }
}
```

### 8. JSON 请求示例

```json
// 请求 1：只更新 age
{
  "age": 30
}

// 请求 2：更新 name 和 email
{
  "name": "李四",
  "email": null
}

// 请求 3：更新所有字段
{
  "name": "王五",
  "age": 25,
  "email": "wangwu@example.com"
}
```

### 9. 配合 UpdateChain 使用

> ⚠️ **重要**：在 `where`、`set` 等方法中，**推荐使用 APT 生成的 `QueryColumn`**（如 `USER.ID`、`USER.NAME`），而不是 Lambda（如 `User::getId`）。

```java
import static com.example.entity.table.UserTableDef.USER;

public void updateUserWithChain(String userId, UserUpdateDTO dto) {
    UpdateChain chain = UpdateChain.of(User.class)
        .where(USER.ID.eq(userId));

    // 处理 OptionalField 字段
    dto.getName().match(
        value -> chain.set(USER.NAME, value),      // VALUE
        () -> chain.set(USER.NAME, null),          // NULL
        () -> {}                                    // MISSING：忽略
    );

    dto.getAge().match(
        value -> chain.set(USER.AGE, value),
        () -> chain.set(USER.AGE, null),
        () -> {}
    );

    dto.getEmail().match(
        value -> chain.set(USER.EMAIL, value),
        () -> chain.set(USER.EMAIL, null),
        () -> {}
    );

    chain.update();
}
```

### 10. 使用 OptionalDtoUtil 简化

```java
public void updateUserWithUtil(String userId, UserUpdateDTO dto) {
    // 转换 DTO 为 UpdateEntity
    User updateEntity = OptionalDtoUtil.toUpdateEntity(dto, User.class, userId);
    
    // 执行更新
    userMapper.update(updateEntity);
}
```

**支持 Record 类型 DTO：**

```java
public record UserUpdateRecord(
    OptionalField<String> name,
    OptionalField<Integer> age,
    OptionalField<String> email
) {
    public UserUpdateRecord {
        if (name == null) name = OptionalField.missing();
        if (age == null) age = OptionalField.missing();
        if (email == null) email = OptionalField.missing();
    }
}

// 使用方式相同
User updateEntity = OptionalDtoUtil.toUpdateEntity(record, User.class, userId);
```

**OptionalDtoUtil 特性：**
- 支持普通类和 Record 类型 DTO
- 自动缓存 PropertyDescriptor 和 Getter 方法，避免重复反射
- 支持嵌套对象递归转换
- 自动识别 OptionalField 类型字段

## 注意事项

1. **JSON 序列化/反序列化**：需要配置 Jackson 以正确处理 `OptionalField` 类型
2. **字段默认值**：DTO 中的 `OptionalField` 字段应默认设置为 `OptionalField.missing()`
3. **null 安全**：使用 `OptionalField.of(value)` 时，如果 value 为 null，会自动转换为 `NULL` 状态
4. **类型安全**：`OptionalField` 是泛型类型，确保类型正确
5. **filter 语义**：`filter` 方法在谓词不满足时返回 `NULL`（而非 `MISSING`），保留了"字段存在但值无效"的语义

## 与其他框架的对比

| 概念 | JavaScript | JSON | OptionalField |
|------|------------|------|---------------|
| 字段不存在 | `undefined` | 字段缺失 | `MISSING` |
| 字段为 null | `null` | `null` | `NULL` |
| 字段有值 | 任意值 | 任意值 | `VALUE` |
