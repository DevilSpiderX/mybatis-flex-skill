# APT 代码生成配置

MyBatis-Flex 提供了 APT（Annotation Processing Tool）代码生成功能在编译期自动生成 `TableDef` 类和 `Mapper` 接口，提供类型安全的查询体验。

## 推荐配置

在项目根目录创建 `mybatis-flex.config` 文件（properties 格式）：

```properties
# mybatis-flex.config

# 启用 Mapper 接口自动生成（推荐）
processor.mapper.generateEnable=true

# 生成的 Mapper 添加 @Mapper 注解（推荐）
processor.mapper.annotation=true

# 指定实体类包路径（可选，默认扫描所有）
processor.mapper.generateInclude=com.example.entity.*

# 启用 TableDef 类自动生成（默认 true）
processor.entity.generateEnable=true
```

### 配置项说明

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `processor.mapper.generateEnable` | `false` | 是否启用 Mapper 接口自动生成 |
| `processor.mapper.annotation` | `false` | 生成的 Mapper 是否添加 `@Mapper` 注解 |
| `processor.mapper.generateInclude` | `*` | 指定需要生成 Mapper 的实体类包路径 |
| `processor.mapper.generateExclude` | - | 排除不需要生成的实体类包路径 |
| `processor.entity.generateEnable` | `true` | 是否启用 TableDef 类自动生成 |
| `processor.entity.package` | - | 指定 TableDef 类的生成包路径 |

同时在 `pom.xml` 中配置 APT 处理器：

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <configuration>
                <annotationProcessorPaths>
                    <path>
                        <groupId>com.mybatisflex</groupId>
                        <artifactId>mybatis-flex-processor</artifactId>
                        <version>${mybatis-flex.version}</version>
                    </path>
                    <!-- Lombok 支持 -->
                    <path>
                        <groupId>org.projectlombok</groupId>
                        <artifactId>lombok</artifactId>
                        <version>${lombok.version}</version>
                    </path>
                </annotationProcessorPaths>
            </configuration>
        </plugin>
    </plugins>
</build>
```

## 自动生成内容

### 1. TableDef 类

APT 会为每个 `@Table` 注解的实体类生成对应的 `TableDef` 类，提供类型安全的列引用。

**实体类：**
```java
@Table("tb_account")
public class Account extends BaseEntity {
    @Id(keyType = KeyType.Generator, value = UUIDv7KeyGenerator.NAME)
    private String id;
    private String userName;
    private Integer age;
}
```

**自动生成的 TableDef：**
```java
public class AccountTableDef extends TableDef {
    public static final AccountTableDef ACCOUNT = new AccountTableDef();
    
    public final QueryColumn ID = new QueryColumn(this, "id");
    public final QueryColumn USER_NAME = new QueryColumn(this, "user_name");
    public final QueryColumn AGE = new QueryColumn(this, "age");
    
    // 所有列
    public final QueryColumn[] ALL_COLUMNS = {ID, USER_NAME, AGE};
}
```

**使用方式：**
```java
import static com.example.entity.table.AccountTableDef.ACCOUNT;

// 类型安全查询
QueryWrapper query = QueryWrapper.create()
    .select(ACCOUNT.ALL_COLUMNS)
    .from(ACCOUNT)
    .where(ACCOUNT.AGE.ge(18))
    .and(ACCOUNT.USER_NAME.like("michael"));
```

### 2. Mapper 接口

APT 可以为每个实体类自动生成继承 `BaseMapper` 的 Mapper 接口。

**自动生成的 Mapper：**
```java
@Mapper
public interface AccountMapper extends BaseMapper<Account> {
    // 继承 BaseMapper 的所有方法
    // 可在此添加自定义查询方法
}
```

**使用方式：**
```java
@Service
@RequiredArgsConstructor
public class AccountService {
    private final AccountMapper accountMapper;
    
    public List<Account> list() {
        return accountMapper.selectAll();
    }
    
    // 使用链式查询
    public List<Account> listActive() {
        return accountMapper.queryChain()
            .where(ACCOUNT.STATUS.eq(1))
            .list();
    }
}
```

## TableDef 命名规则

| 实体类 | TableDef 类 | 静态实例 |
|--------|-------------|----------|
| `Account` | `AccountTableDef` | `ACCOUNT` |
| `UserInfo` | `UserInfoTableDef` | `USER_INFO` |
| `OrderDetail` | `OrderDetailTableDef` | `ORDER_DETAIL` |

命名规则：
- 类名：`{EntityName}TableDef`
- 实例名：实体类名转大写下划线（驼峰转下划线）

## 使用 TableDef 的优势

### 1. 类型安全

```java
// ✅ 推荐：使用 TableDef（编译期检查）
.where(ACCOUNT.AGE.ge(18))

// ❌ 不推荐：使用字符串（容易出错）
.where("age >= ?", 18)
```

### 2. IDE 支持

- 自动补全列名
- 重构时自动更新引用
- 跳转到定义

### 3. 防止拼写错误

```java
// ✅ 编译期发现错误
.where(ACCOUNT.AGE.ge(18))  // 如果 AGE 不存在，编译报错

// ❌ 运行时才发现错误
.where("agee >= ?", 18)  // 拼写错误，运行时 SQL 报错
```

## 完整配置示例

### Maven 项目

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>mybatis-flex-demo</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <mybatis-flex.version>1.9.0</mybatis-flex.version>
        <lombok.version>1.18.30</lombok.version>
    </properties>

    <dependencies>
        <!-- MyBatis-Flex -->
        <dependency>
            <groupId>com.mybatisflex</groupId>
            <artifactId>mybatis-flex-spring-boot3-starter</artifactId>
            <version>${mybatis-flex.version}</version>
        </dependency>

        <!-- MyBatis-Flex APT 处理器 -->
        <dependency>
            <groupId>com.mybatisflex</groupId>
            <artifactId>mybatis-flex-processor</artifactId>
            <version>${mybatis-flex.version}</version>
            <scope>provided</scope>
        </dependency>

        <!-- Lombok -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <version>${lombok.version}</version>
            <scope>provided</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
                <configuration>
                    <source>17</source>
                    <target>17</target>
                    <annotationProcessorPaths>
                        <path>
                            <groupId>com.mybatisflex</groupId>
                            <artifactId>mybatis-flex-processor</artifactId>
                            <version>${mybatis-flex.version}</version>
                        </path>
                        <path>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                            <version>${lombok.version}</version>
                        </path>
                    </annotationProcessorPaths>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

### Gradle 项目

```kotlin
plugins {
    java
    id("org.springframework.boot") version "3.2.0"
}

java {
    sourceCompatibility = JavaVersion.VERSION_17
}

dependencies {
    // MyBatis-Flex
    implementation("com.mybatisflex:mybatis-flex-spring-boot3-starter:1.9.0")
    
    // Lombok
    compileOnly("org.projectlombok:lombok:1.18.30")
    annotationProcessor("org.projectlombok:lombok:1.18.30")
    
    // MyBatis-Flex APT
    annotationProcessor("com.mybatisflex:mybatis-flex-processor:1.9.0")
}
```

## 常见问题

### 1. TableDef 类未生成

**可能原因：**
- 未添加 `mybatis-flex-processor` 依赖
- 实体类未添加 `@Table` 注解
- 未执行编译（`mvn compile` 或 `gradle build`）

**解决方案：**
```bash
# Maven
mvn clean compile

# Gradle
gradle clean build
```

### 2. Mapper 接口未生成

**可能原因：**
- 未在配置中启用 Mapper 生成
- 实体类包路径未包含在生成范围内

**解决方案：**

在项目根目录的 `mybatis-flex.config` 中添加：
```properties
processor.mapper.generateEnable=true
processor.mapper.annotation=true
processor.mapper.generateInclude=com.example.entity.*
```

### 3. 编译时找不到 TableDef 类

**解决方案：**
1. 确保 APT 处理器在 `annotationProcessorPaths` 中
2. 执行 `mvn clean compile` 重新生成
3. 在 IDE 中刷新 Maven/Gradle 项目

## 最佳实践

1. **始终使用 TableDef**：提供类型安全和 IDE 支持
2. **静态导入**：使用 `import static` 导入 TableDef 实例
3. **统一命名**：遵循驼峰转下划线的命名规则
4. **版本一致**：确保 APT 处理器版本与 MyBatis-Flex 核心版本一致

```java
// ✅ 推荐写法
import static com.example.entity.table.AccountTableDef.ACCOUNT;

QueryWrapper query = QueryWrapper.create()
    .select(ACCOUNT.ALL_COLUMNS)
    .from(ACCOUNT)
    .where(ACCOUNT.AGE.ge(18));

// ❌ 不推荐写法（字符串方式）
QueryWrapper query = QueryWrapper.create()
    .select("*")
    .from("tb_account")
    .where("age >= ?", 18);
```
