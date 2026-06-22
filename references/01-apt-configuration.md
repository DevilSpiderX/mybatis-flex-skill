# APT 代码生成配置

MyBatis-Flex 使用 APT（Annotation Processing Tool）在编译期根据 Entity 生成类型安全的 `TableDef` 辅助类，也可以按配置生成对应的 `Mapper` 接口。官方文档入口：

- APT 设置：https://mybatis-flex.com/zh/others/apt.html
- Maven 依赖：https://mybatis-flex.com/zh/intro/maven.html
- Gradle 依赖：https://mybatis-flex.com/zh/intro/gradle.html
- KAPT 设置：https://mybatis-flex.com/zh/others/kapt.html

## 使用边界

- `TableDef` 是类型安全查询、更新的首选列引用来源，例如 `ACCOUNT.USER_NAME`、`ACCOUNT.ID`。
- `Mapper` 自动生成从 `1.1.9` 起默认关闭；需要自动生成时必须显式配置 `processor.mapper.generateEnable=true`。
- `mybatis-flex.config` 放在 Maven 根模块，即 `pom.xml` 所在目录。多模块项目优先放在实体所在模块的 Maven 根目录。
- APT 生成目录默认是 `target/generated-sources/annotations`；测试源码默认生成到 `target/generated-test-sources/test-annotations`。
- 生成目录不要手写到 `src/main/java`，不要提交 `target/generated-sources/**` 这类构建产物。

## Maven 配置

`mybatis-flex-processor` 提供 APT 服务，推荐放入 `maven-compiler-plugin` 的 `annotationProcessorPaths`。配置后通常不需要再在 `<dependencies>` 中声明 `mybatis-flex-processor`。

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <configuration>
        <annotationProcessorPaths>
            <path>
                <groupId>com.mybatis-flex</groupId>
                <artifactId>mybatis-flex-processor</artifactId>
                <version>${mybatis-flex.version}</version>
            </path>
        </annotationProcessorPaths>
    </configuration>
</plugin>
```

如果项目同时使用 Lombok、MapStruct，也要把它们的 processor 一起放在 `annotationProcessorPaths`，否则可能出现某一类生成代码缺失。

```xml
<annotationProcessorPaths>
    <path>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <version>${lombok.version}</version>
    </path>
    <path>
        <groupId>org.mapstruct</groupId>
        <artifactId>mapstruct-processor</artifactId>
        <version>${mapstruct.version}</version>
    </path>
    <path>
        <groupId>com.mybatis-flex</groupId>
        <artifactId>mybatis-flex-processor</artifactId>
        <version>${mybatis-flex.version}</version>
    </path>
</annotationProcessorPaths>
```

依赖坐标使用官方 Maven groupId：

```xml
<dependency>
    <groupId>com.mybatis-flex</groupId>
    <artifactId>mybatis-flex-spring-boot3-starter</artifactId>
    <version>${mybatis-flex.version}</version>
</dependency>
```

## Gradle 配置

Java / Groovy DSL：

```groovy
dependencies {
    annotationProcessor "com.mybatis-flex:mybatis-flex-processor:${mybatisFlexVersion}"
}
```

Kotlin DSL：

```kotlin
dependencies {
    annotationProcessor("com.mybatis-flex:mybatis-flex-processor:$mybatisFlexVersion")
}
```

Kotlin 项目使用 `kapt`，不要只配 `annotationProcessor`：

```kotlin
plugins {
    kotlin("kapt") version kotlinVersion
}

dependencies {
    kapt("com.mybatis-flex:mybatis-flex-processor:$mybatisFlexVersion")
}
```

## mybatis-flex.config

最小推荐配置：

```properties
# mybatis-flex.config
processor.enable=true

# Mapper 自动生成默认关闭；需要时显式开启
processor.mapper.generateEnable=true
processor.mapper.annotation=true
```

常用配置项：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `processor.enable` | `true` | 全局启用 APT |
| `processor.stopBubbling` | `false` | 是否停止向上级目录合并配置 |
| `processor.genPath` | `target/generated-sources/annotations` | APT 代码生成路径，可为绝对或相对路径 |
| `processor.charset` | `UTF-8` | 生成文件字符集 |
| `processor.allInTables.enable` | `false` | 是否把所有表辅助变量生成到统一 `Tables` 类 |
| `processor.allInTables.package` | `${entityPackage}.table` | `Tables` 包名 |
| `processor.allInTables.className` | `Tables` | `Tables` 类名 |
| `processor.mapper.generateEnable` | `false` | 是否启用 Mapper 自动生成 |
| `processor.mapper.annotation` | `false` | 生成的 Mapper 是否添加 `@Mapper` |
| `processor.mapper.baseClass` | `com.mybatisflex.core.BaseMapper` | 生成 Mapper 的父接口 |
| `processor.mapper.package` | `${entityPackage}.mapper` | 生成 Mapper 的包名 |
| `processor.tableDef.package` | `${entityPackage}.table` | 生成 TableDef 的包名 |
| `processor.tableDef.propertiesNameStyle` | `upperCase` | TableDef 字段风格 |
| `processor.tableDef.instanceSuffix` | 空字符串 | 表实例变量后缀 |
| `processor.tableDef.classSuffix` | `TableDef` | TableDef 类名后缀 |
| `processor.tableDef.ignoreEntitySuffixes` | - | 生成类名时忽略的 Entity 后缀 |

不要使用未在官方 APT 文档中出现的伪配置项，例如 `processor.entity.generateEnable`、`processor.entity.package`、`processor.mapper.generateInclude`、`processor.mapper.generateExclude`。如果要关闭单个实体的 Mapper 生成，优先使用实体注解配置，例如 `@Table(mapperGenerateEnable = false)`。

## 包名表达式

以下配置支持包名表达式：

```properties
processor.allInTables.package=${entityPackage}.table
processor.mapper.package=${entityPackage.parent}.mapper
processor.tableDef.package=${entityPackage}.table
```

- `${entityPackage}` 表示 Entity 所在包。
- `${entityPackage.parent}` 表示 Entity 上一级包；可以继续写 `${entityPackage.parent.parent}`。
- 如果实体分布在多个包，并启用 `processor.allInTables.enable=true`，必须显式设置 `processor.allInTables.package`，避免 `Tables` 生成到最后一个被处理的实体包下。

## TableDef 生成形态

实体示例：

```java
@Table("tb_account")
public class Account extends BaseEntity {
    @Id(keyType = KeyType.Generator, value = UUIDv7KeyGenerator.NAME)
    private String id;
    private String userName;
    private Integer age;
}
```

默认生成的 `TableDef` 形态接近：

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

默认命名规则：

| 实体类 | TableDef 类 | 静态实例 |
|--------|-------------|----------|
| `Account` | `AccountTableDef` | `ACCOUNT` |
| `UserInfo` | `UserInfoTableDef` | `USER_INFO` |
| `OrderDetail` | `OrderDetailTableDef` | `ORDER_DETAIL` |

字段风格可用 `processor.tableDef.propertiesNameStyle` 调整：

- `upperCase`：`USER_NAME`
- `lowerCase`：`user_name`
- `upperCamelCase`：`UserName`
- `lowerCamelCase`：`userName`

如果实体统一带 `Entity`、`Model`、`Dto` 等后缀，可用：

```properties
processor.tableDef.ignoreEntitySuffixes=Entity, Model, Dto
```

## TableDef 使用方式

优先静态导入表实例：

```java
import static com.example.entity.table.AccountTableDef.ACCOUNT;
```

查询：

```java
QueryWrapper query = QueryWrapper.create()
    .select(ACCOUNT.DEFAULT_COLUMNS)
    .from(ACCOUNT)
    .where(ACCOUNT.ID.eq(id))
    .and(ACCOUNT.USER_NAME.like(userName, If::hasText));
```

链式查询：

```java
List<Account> accounts = accountMapper.queryChain()
    .select(ACCOUNT.DEFAULT_COLUMNS)
    .where(ACCOUNT.USER_NAME.like(keyword, If::hasText))
    .list();
```

链式更新：

```java
UpdateChain.of(Account.class)
    .set(ACCOUNT.USER_NAME, dto.getUserName(), If::hasText)
    .where(ACCOUNT.ID.eq(id))
    .update();
```

不要退回字符串列名，除非项目没有实体、没有 `TableDef`，或正在处理受控的原生 SQL / `Db + Row` 场景。

## Mapper 自动生成

开启后，APT 会生成继承 `BaseMapper<Entity>` 的 Mapper 接口。需要 `@Mapper` 注解时同时配置：

```properties
processor.mapper.generateEnable=true
processor.mapper.annotation=true
```

默认父接口是 `com.mybatisflex.core.BaseMapper`。如果项目封装了公共 Mapper 父接口：

```properties
processor.mapper.baseClass=com.example.common.mapper.MyBaseMapper
```

如果希望 Mapper 生成到 Entity 的上级包下：

```properties
processor.mapper.package=${entityPackage.parent}.mapper
```

Service 层仍按项目既有风格注入 Mapper；不要因为启用了自动生成 Mapper 就引入 `IService` 继承链。

## 常见问题

### TableDef 类未生成

优先按顺序检查：

1. `maven-compiler-plugin` / Gradle 是否配置了 `com.mybatis-flex:mybatis-flex-processor`。
2. 是否执行了编译阶段，例如 `mvn clean compile`、`mvn clean package` 或 `gradle clean build`。
3. IDE 是否启用了 annotation processing，并把 `target/generated-sources/annotations` 标记为 generated sources。
4. `processor.enable` 是否被设置为 `false`。
5. `mybatis-flex.config` 是否放在正确模块根目录；多模块项目不要只放在聚合根。
6. 包名自定义后，静态导入路径是否仍指向旧包。

### Mapper 接口未生成

优先检查：

1. 是否配置 `processor.mapper.generateEnable=true`。
2. 单个实体是否通过 `@Table(mapperGenerateEnable = false)` 关闭了 Mapper 生成。
3. `processor.mapper.package` 是否把 Mapper 生成到了另一个包。
4. 是否需要 `processor.mapper.annotation=true` 让 Spring 扫描到生成 Mapper。

### IDE 无法识别生成类

Maven 项目先执行：

```bash
mvn clean compile
```

然后在 IDE 中执行 Maven 的 `Generate Sources and Update Folders` 或重新导入项目。Gradle 项目执行：

```bash
gradle clean build
```

如果是 Kotlin 项目，确认 `kapt` 在编译前运行。
