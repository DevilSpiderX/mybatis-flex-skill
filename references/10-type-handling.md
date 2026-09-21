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

### 无注解枚举（按 name 存取）

```java
@Getter
@RequiredArgsConstructor
public enum Status {
    DISABLED("禁用"),
    ENABLED("启用");

    private final String desc;
}
```

不标 `@EnumValue` 时，实体枚举字段由 `CompositeEnumTypeHandler` 处理：检测到 `@EnumValue`（字段或方法）
才委托 `FlexEnumTypeHandler`，否则退回 MyBatis 的 `EnumTypeHandler`，按枚举 `name()` 存取
（`mybatis-flex-core/src/main/java/com/mybatisflex/core/handler/CompositeEnumTypeHandler.java:38-52`，
注册点 `TableInfo.java:836`）。

### 枚举处理器对照

| 处理器 | 来源 | 说明 |
|--------|------|------|
| `CompositeEnumTypeHandler` | MyBatis-Flex | 实体枚举列默认入口，按有无 `@EnumValue` 委托 |
| `FlexEnumTypeHandler` | MyBatis-Flex | 按 `@EnumValue` 字段/方法取值；读库值匹配不到时返回 `null` |
| `EnumTypeHandler` | MyBatis | 按枚举 `name()` 存取 |
| `EnumOrdinalTypeHandler` | MyBatis | 按 ordinal 存取；枚举顺序变动即错位，慎用 |

注意：源码中不存在 `IEnumTypeHandler` / `IEnum`（1.11.8 已移除），也不存在
`mybatis-flex.mapper-impl.enum-as-integer` 配置项，不要按旧版资料编写。

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

坑点：`JacksonTypeHandler` 只有 `(Class<?> propertyType)` 和 `(Class<?>, Class<?>)` 两个构造器
（`mybatis-flex-core/.../handler/JacksonTypeHandler.java:36-43`），由框架按字段类型实例化，**泛型参数丢失**——
`List<Bean>` 反序列化回来元素是 `Map` 而不是 `Bean`。需要精确泛型时为该字段写专用 handler。

### 其他 JSON 处理器

```java
// Fastjson 处理器（需 com.alibaba:fastjson 依赖）
@Column(value = "options", typeHandler = FastjsonTypeHandler.class)
private Map<String, Object> options;

// Fastjson2 处理器（需 com.alibaba.fastjson2:fastjson2 依赖）
@Column(value = "options", typeHandler = Fastjson2TypeHandler.class)
private Map<String, Object> options;

// Gson 处理器（需 com.google.code.gson:gson 依赖）
@Column(value = "options", typeHandler = GsonTypeHandler.class)
private Map<String, Object> options;
```

注意：Fastjson/Fastjson2/Gson 都是**可选依赖**，不引入对应 jar 时使用其 handler 会类找不到；并非
"自动检测"。`Fastjson2TypeHandler` 还有个特性：属性类型是接口或抽象类时会写入类型名（`WriteClassName`），
库中 JSON 会带 `@type` 字段（`Fastjson2TypeHandler.java:39-41,77-82`）。

### 逗号分隔字符串 ↔ List<String>

```java
@Column(value = "tags", typeHandler = CommaSplitTypeHandler.class)
private List<String> tags;   // 库中存 "a,b,c"，空串/null 读回来是 null
```

`CommaSplitTypeHandler` 直接用英文逗号拆分/拼接（`mybatis-flex-core/.../handler/CommaSplitTypeHandler.java:32`），
元素本身不能含逗号；需要引号包裹等复杂格式时用 JSON handler 代替。

### 自定义 TypeHandler

```java
public class MyJsonTypeHandler extends BaseJsonTypeHandler<Object> {
    private final Class<?> type;

    public MyJsonTypeHandler(Class<?> type) {
        this.type = type;
    }

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

基类是 `BaseJsonTypeHandler<T>`（**不是** `AbstractJsonTypeHandler`），已实现 `BaseTypeHandler` 的空串/null
处理，子类只需实现 `parseJson(String)` / `toJson(T)` 两个抽象方法
（`mybatis-flex-core/.../handler/BaseJsonTypeHandler.java:27-54`）。构造器带 `Class` 参数才能被
`@Column(typeHandler = ...)` 按字段类型实例化。

### JSON 处理器对比

| 处理器 | 依赖 | 说明 |
|--------|------|------|
| `JacksonTypeHandler` | Jackson（推荐） | Spring Boot 常见，功能全 |
| `FastjsonTypeHandler` | Fastjson（`com.alibaba:fastjson`） | 阿里旧版 |
| `Fastjson2TypeHandler` | Fastjson2（`com.alibaba.fastjson2:fastjson2`） | 接口/抽象类型写 `@type` |
| `GsonTypeHandler` | Gson（`com.google.code.gson:gson`） | Google |
| `CommaSplitTypeHandler` | 无 | 逗号分隔字符串 ↔ `List<String>` |

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

`isLarge = true` 的效果：APT 生成的 TableDef 默认不把该列放入 `DEFAULT_COLUMNS`
（官方说明见 `docs/zh/core/column.md:140-180`），即一切走 `DEFAULT_COLUMNS` 的查询都不会带出该列。
需要查它时显式选择列：

```java
// QueryChain：显式 select 大字段列
Account account = QueryChain.of(accountMapper)
    .select(ACCOUNT.CONTENT)
    .where(ACCOUNT.ID.eq(id))
    .one();

// QueryWrapper：同上
accountMapper.selectOneByQuery(QueryWrapper.create()
    .select(ACCOUNT.CONTENT)
    .where(ACCOUNT.ID.eq(id)));
```

注意：文档中不存在 `selectById(id, "content")` 这种 BaseMapper 方法，不要凭印象调用。

## 数据脱敏

**注意：`@Column` 没有 `mask` 属性，也不能写 `typeHandler = MaskTypeHandler.class`**——`MaskTypeHandler`
只有接收规则名的构造器 `MaskTypeHandler(String maskType)`，没有无参构造。正确入口是独立注解
`@ColumnMask`：

```java
@Table("tb_account")
public class Account {
    @ColumnMask(Masks.MOBILE)         // 138****5678
    private String mobile;

    @ColumnMask(Masks.CHINESE_NAME)   // 张三丰 -> 张**
    private String userName;
}
```

`@ColumnMask` 只支持 String 字段，规则名必须已在 `MaskManager` 注册，否则启动即抛
`IllegalStateException`；且**只读脱敏、写不脱敏**——编辑回显要用 `MaskManager.execWithoutMask(...)`
取原始值，否则会把脱敏值保存回库。

完整规则清单（内置 9 种）、自定义规则、与 `SetListener` 的区别见
[07-core-features.md](07-core-features.md) 脱敏章节。

## 类型处理器 TypeHandler

### MyBatis-Flex 内置处理器

`mybatis-flex-core/.../handler/` 包下共 8 个类（1.11.8）：

| 处理器 | 用途 |
|--------|------|
| `JacksonTypeHandler` | Jackson JSON（构造参数为字段类型） |
| `FastjsonTypeHandler` | Fastjson 1.x JSON（需 fastjson 依赖） |
| `Fastjson2TypeHandler` | Fastjson2 JSON（需 fastjson2 依赖；接口/抽象类型写 `@type`） |
| `GsonTypeHandler` | Gson JSON（需 gson 依赖） |
| `CommaSplitTypeHandler` | 逗号分隔字符串 ↔ `List<String>` |
| `BaseJsonTypeHandler` | JSON handler 抽象基类，自定义 JSON 处理继承它 |
| `CompositeEnumTypeHandler` | 实体枚举列默认入口，按有无 `@EnumValue` 委托 |
| `FlexEnumTypeHandler` | 按 `@EnumValue` 取值 |

常见标量类型（`LongTypeHandler`/`IntegerTypeHandler`/`StringTypeHandler`/`BigDecimalTypeHandler`/
`BooleanTypeHandler`/`DateTypeHandler`/`LocalDateTimeTypeHandler`/`LocalDateTypeHandler`）是 **MyBatis 自带**
（`org.apache.ibatis.type` 包），框架自动注册，无需也不应在 `@Column(typeHandler=...)` 里手写。
旧版资料里的 `JsonTypeHandler`、`IEnumTypeHandler` 在 1.11.8 源码中不存在，不要使用。

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
// 字段级：注解方式（最常见）
@Column(value = "phone", typeHandler = EncryptTypeHandler.class)
private String phone;
```

全局注册走**包扫描**，不是类列表（配置类 `MybatisFlexProperties.typeHandlersPackage`，
`mybatis-flex-spring-boot-starter/.../MybatisFlexProperties.java:104`，支持 `com.example.*.typehandler`
形式通配符，`mybatis-flex-spring/.../FlexSqlSessionFactoryBean.java:278-289`）：

```yaml
mybatis-flex:
  type-handlers-package: com.example.handler
```

坑点：

- 不存在 `mybatis-flex.type-handlers` 这种类列表写法。
- 包扫描注册依赖 `@MappedTypes`/`@MappedJdbcTypes` 注解，或从 `BaseTypeHandler<T>` 的泛型推断类型；
  两种都没有时注册不上。
- `@Column(typeHandler = ...)` 方式不需要 `@MappedTypes` 等注解，框架按字段类型实例化。

## TypeHandler 内联写法

`@Column(typeHandler` 只接受 `Class<? extends TypeHandler>`，没有字符串全类名的重载，直接写类引用即可：

```java
@Column(value = "options", typeHandler = JacksonTypeHandler.class)
private Map<String, Object> options;

@Column(value = "tags", typeHandler = CommaSplitTypeHandler.class)
private List<String> tags;

@Column(value = "password", typeHandler = EncryptTypeHandler.class)
private String password;
```
