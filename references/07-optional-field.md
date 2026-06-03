# OptionalField 三态值类型

> ⚠️ **前提条件**：使用 `OptionalField` 三态值类型前，必须先确保项目中已引入该类型。源码实现请参考 [07-1-optional-field-source.md](07-1-optional-field-source.md)。

> OptionalField 是一个自定义的三态值类型，用于处理部分更新场景。它表示字段的三种状态：有值、null、不存在。

## 核心概念

| 状态 | 枚举值 | 含义 | UpdateEntity 行为 |
|------|--------|------|-------------------|
| 有值 | `VALUE` | 字段有实际值 | `set(field, value)` |
| null | `NULL` | 字段存在但为 null | `set(field, null)` |
| 缺失 | `MISSING` | 字段不存在 | 忽略，不调用 set |

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

## 源码实现

完整的源码实现请参考 [07-1-optional-field-source.md](07-1-optional-field-source.md)，包含：

- `OptionalField` 类 - 三态值类型核心实现
- `OptionalDtoUtil` 工具类 - DTO 转换为 UpdateEntity

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

### 2. Service 层使用

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

### 3. Controller 层使用

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

### 4. JSON 请求示例

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

### 5. 配合 UpdateChain 使用

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

### 6. Record 类型 DTO

```java
public record UserUpdateRecord(
    OptionalField<String> name,
    OptionalField<Integer> age,
    OptionalField<String> email
) {
    public UserUpdateRecord {
        // 默认值
        if (name == null) name = OptionalField.missing();
        if (age == null) age = OptionalField.missing();
        if (email == null) email = OptionalField.missing();
    }
}
```

## 注意事项

1. **JSON 序列化/反序列化**：需要配置 Jackson 以正确处理 `OptionalField` 类型
2. **字段默认值**：DTO 中的 `OptionalField` 字段应默认设置为 `OptionalField.missing()`
3. **null 安全**：使用 `OptionalField.of(value)` 时，如果 value 为 null，会自动转换为 `NULL` 状态
4. **类型安全**：`OptionalField` 是泛型类型，确保类型正确

## 与其他框架的对比

| 概念 | JavaScript | JSON | OptionalField |
|------|------------|------|---------------|
| 有值 | `value` | `{"field": value}` | `OptionalField.of(value)` |
| null | `null` | `{"field": null}` | `OptionalField._null()` |
| 不存在 | `undefined` | 字段不存在 | `OptionalField.missing()` |

## 相关文档

- [07-1-optional-field-source.md](07-1-optional-field-source.md) - 源码实现
