# 数据类型处理参考

## 常见映射

| Java 类型 | 数据库类型 | 说明 |
|-----------|-----------|------|
| String | varchar/char/text | 自动转换 |
| Integer | int/int4 | 自动转换 |
| Long | bigint/int8 | 自动转换 |
| BigDecimal | numeric/decimal | 金额建议使用 |
| Double/Float | float/double | 精度不敏感场景 |
| Boolean | boolean/tinyint | 自动转换 |
| Date | datetime/timestamp | 日期时间 |
| LocalDate | date | 仅日期 |
| LocalDateTime | datetime/timestamp | 日期时间 |
| JSON | json/jsonb | JSON 类型 |

## BigDecimal 使用建议

金额相关字段务必使用 BigDecimal：

```java
@Column("amount")
private BigDecimal amount;

@Column("price")
private BigDecimal price;
```

**对比：**
```java
// ❌ 错误 - 精度丢失
0.1 + 0.2 == 0.3  // false

// ✅ 正确
new BigDecimal("0.1").add(new BigDecimal("0.2")).equals(new BigDecimal("0.3"))  // true
```

## 枚举映射

### 推荐枚举写法

```java
@Getter
@RequiredArgsConstructor
public enum SignFlowStatus {
    Waiting(1, "盖章中"),
    Success(2, "已完成"),
    Cancel(3, "已撤销"),
    Expired(4, "已过期"),
    Rejected(5, "已拒签"),
    Error(6, "错误"),
    ;

    @EnumValue
    @JsonValue
    private final int value;
    private final String desc;

    @JsonCreator
    public static @Nullable SignFlowStatus valueOf(final int value) {
        for (final var item : values()) {
            if (item.value == value) {
                return item;
            }
        }
        return null;
    }
}
```

**说明：**
- `@EnumValue` - MyBatis-Flex 注解，指定数据库存储的值
- `@JsonValue` - Jackson 注解，序列化时使用 value 字段
- `@JsonCreator` - Jackson 注解，反序列化时使用静态方法

### 或者直接使用枚举的 name()

```java
@Getter
@RequiredArgsConstructor
public enum Status {
    DISABLED("禁用"),
    ENABLED("启用");

    private final String desc;
}
```

### 基础枚举

```java
public enum Status {
    DISABLED(0, "禁用"),
    ENABLED(1, "启用");
    
    private int code;
    private String desc;
}

@Column(value = "status", typeHandler = IEnumTypeHandler.class)
private Status status;
```

### 枚举处理器

| 处理器 | 说明 |
|--------|------|
| `IEnumTypeHandler` | 按 `IEnum.getCode()` 映射 |
| `EnumTypeHandler` | 按枚举序号映射（默认） |
| `EnumOrdinalTypeHandler` | 按 ordinal 映射 |

### 全局配置

```yaml
mybatis-flex:
  mapper-impl:
    enum-as-integer: true
```

## JSON 字段映射

### 推荐使用 JacksonTypeHandler

```java
@Column(value = "options", typeHandler = JacksonTypeHandler.class)
private Map<String, Object> options;

@Column(value = "tags", typeHandler = JacksonTypeHandler.class)
private List<String> tags;

@Column(value = "config", typeHandler = JacksonTypeHandler.class)
private YourConfigClass config;
```

### 其他 JSON 处理器

```java
// Fastjson 处理器
@Column(value = "options", typeHandler = FastjsonTypeHandler.class)
private Map<String, Object> options;

// Fastjson2 处理器
@Column(value = "options", typeHandler = Fastjson2TypeHandler.class)
private Map<String, Object> options;
```

### 自定义 TypeHandler

```java
public class JsonTypeHandler extends AbstractJsonTypeHandler<Object> {
    private Class<?> type;
    
    @Override
    protected Object parseJson(String json) {
        return JSON.parseObject(json, type);
    }
    
    @Override
    protected String toJson(Object obj) {
        return JSON.toJSONString(obj);
    }
}
```

### JSON 处理器对比

| 处理器 | 依赖 | 说明 |
|--------|------|------|
| `JacksonTypeHandler` | Jackson（推荐） | Spring Boot 默认，功能强大 |
| `FastjsonTypeHandler` | Fastjson | 阿里巴巴 JSON 库 |
| `Fastjson2TypeHandler` | Fastjson2 | Fastjson 升级版，性能更好 |

### Fastjson / Jackson / Gson

MyBatis-Flex 内置支持：
- Fastjson：`com.alibaba.fastjson`
- Jackson：`com.fasterxml.jackson`
- Gson：`com.google.gson`

无需额外配置，自动检测。

## 日期类型

### 常用日期

```java
// 创建时间（自动填充）
@Column(value = "create_time", onInsertValue = "now()")
private LocalDateTime createTime;

// 更新时间（自动填充）
@Column(value = "update_time", onUpdateValue = "now()")
private LocalDateTime updateTime;

// 生日
@Column("birthday")
private LocalDate birthday;
```

### 日期查询

```java
// 大于等于
QueryWrapper.create()
    .select().from(ACCOUNT)
    .where(ACCOUNT.CREATE_TIME.ge(LocalDateTime.of(2024, 1, 1, 0, 0)));

// 区间查询
QueryWrapper.create()
    .select().from(ACCOUNT)
    .where(ACCOUNT.CREATE_TIME.ge(startDate))
    .and(ACCOUNT.CREATE_TIME.le(endDate));
```

## 大字段处理

```java
@Column(value = "content", isLarge = true)
private String content;
```

`isLarge = true` 会导致：
- 不在 `select *` 中返回
- 需单独查询：`selectById(id, "content")`

## 数据脱敏

```java
@Column(value = "phone", typeHandler = MaskTypeHandler.class)
private String phone;

@Column(value = "email", typeHandler = MaskTypeHandler.class)
private String email;

@Column(value = "id_card", typeHandler = MaskTypeHandler.class)
private String idCard;
```

内置脱敏规则：
- 手机号：`138****5678`
- 邮箱：`zh****san@example.com`
- 身份证：`110***********1234`

## 类型处理器 TypeHandler

### 内置处理器

| 处理器 | 用途 |
|--------|------|
| `LongTypeHandler` | Long 类型 |
| `IntegerTypeHandler` | Integer 类型 |
| `StringTypeHandler` | String 类型 |
| `BigDecimalTypeHandler` | BigDecimal |
| `BooleanTypeHandler` | Boolean |
| `DateTypeHandler` | java.util.Date |
| `LocalDateTimeTypeHandler` | LocalDateTime |
| `LocalDateTypeHandler` | LocalDate |
| `JsonTypeHandler` | JSON 对象 |
| `IEnumTypeHandler` | 枚举类型 |
| `FastjsonTypeHandler` | Fastjson |
| `JacksonTypeHandler` | Jackson |
| `GsonTypeHandler` | Gson |

### 自定义处理器

```java
@MappedTypes(String.class)
@MappedJdbcTypes(JdbcType.VARCHAR)
public class EncryptTypeHandler extends BaseTypeHandler<String> {
    
    @Override
    public void setNonNullParameter(PreparedStatement ps, int i, 
                                    String parameter, JdbcType jdbcType) 
            throws SQLException {
        ps.setString(i, encrypt(parameter));
    }
    
    @Override
    public String getNullableResult(ResultSet rs, String columnName) 
            throws SQLException {
        return decrypt(rs.getString(columnName));
    }
    
    private String encrypt(String value) {
        // 加密逻辑
    }
    
    private String decrypt(String value) {
        // 解密逻辑
    }
}
```

### 注册处理器

```java
// 注解方式
@Column(value = "phone", typeHandler = EncryptTypeHandler.class)
private String phone;

// 全局注册
mybatis-flex:
  type-handlers:
    - com.example.handler.EncryptTypeHandler
```

## TypeHandler 内联写法

在注解中直接使用：

```java
@Column(value = "options", typeHandler = JsonTypeHandler.class)
private Map<String, Object> options;

// 或更明确
@Column(value = "options", 
        typeHandler = "com.alibaba.fastjson2.support.spring6x.web.FastJsonHttpMessageConverter")
private Map<String, Object> options;
```
