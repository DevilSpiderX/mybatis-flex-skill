---
name: mybatis-flex-skill
description: >-
  MyBatis-Flex 开发技能。当用户请求涉及 MyBatis-Flex 框架时激活，
  包括编写代码、检查代码、优化代码、代码重构、问题排查、代码解释、
  最佳实践咨询、版本迁移等场景，涵盖实体类定义、CRUD 操作、
  链式查询、关联查询、批量操作等。
---

# MyBatis-Flex 开发技能

优先使用链式操作（Chain Operations）：QueryChain、UpdateChain、DbChain。

## Entity 实体类定义

```java
@Table("tb_account")
public class Account extends BaseEntity {
    @Id(keyType = KeyType.Generator, value = UUIDv7KeyGenerator.NAME)
    private String id;
    private String userName;
    private Integer age;
}
```

APT 自动生成 TableDef 类（如 `ACCOUNT`），用于类型安全查询。

> 💡 **推荐配置**：启用 APT 自动生成 Mapper 接口，避免手动编写。在 `mybatis-flex.config` 中配置 `processor.mapper.generateEnable=true` 和 `processor.mapper.annotation=true`，并在 `pom.xml` 中添加 `mybatis-flex-processor`。

## APT 代码生成（推荐）

MyBatis-Flex 通过 APT 在编译期自动生成 `TableDef` 类和 `Mapper` 接口。

### 配置方式

**1. 创建 `mybatis-flex.config` 文件（项目根目录）：**
```properties
# mybatis-flex.config

# 启用 Mapper 接口自动生成
processor.mapper.generateEnable=true

# 生成的 Mapper 添加 @Mapper 注解
processor.mapper.annotation=true

# 指定实体类包路径
processor.mapper.generateInclude=com.example.entity.*
```

**2. Maven 依赖：**
```xml
<dependency>
    <groupId>com.mybatisflex</groupId>
    <artifactId>mybatis-flex-processor</artifactId>
    <version>${mybatis-flex.version}</version>
    <scope>provided</scope>
</dependency>
```

### 生成内容

| 生成物 | 说明 | 示例 |
|--------|------|------|
| `TableDef` | 类型安全的列引用 | `ACCOUNT.AGE.ge(18)` |
| `Mapper` | 继承 BaseMapper 的接口 | `AccountMapper extends BaseMapper<Account>` |

### 使用示例

```java
// 静态导入 TableDef
import static com.example.entity.table.AccountTableDef.ACCOUNT;

// 类型安全查询
List<Account> accounts = accountMapper.queryChain()
    .where(ACCOUNT.AGE.ge(18))
    .and(ACCOUNT.USER_NAME.like("michael"))
    .list();
```

> 详细配置请参考 `references/00-apt-configuration.md`

## 链式操作（Chain Operations）- 优先使用

### QueryChain 查询

```java
// 基本查询
List<Account> accounts = accountMapper.queryChain()
    .where(ACCOUNT.AGE.ge(18))
    .and(ACCOUNT.USER_NAME.like("michael"))
    .list();

// 查询单条
Account account = accountMapper.queryChain()
    .where(ACCOUNT.ID.eq("xxx"))
    .one();

// 分页查询（Pagination）
Page<Account> page = accountMapper.queryChain()
    .where(ACCOUNT.AGE.ge(18))
    .page(1, 10);

// Lambda 条件
List<Account> list = accountMapper.queryChain()
    .where(Account::getId).ge("xxx")
    .and(Account::getUserName).like("michael")
    .list();
```

**常用方法（Common Methods）：** `one()` / `list()` / `page()` / `count()` / `exists()` / `oneAs()` / `listAs()` / `oneWithRelations()` / `listWithRelations()`

### UpdateChain 更新

```java
// 更新字段
UpdateChain.of(Account.class)
    .set(Account::getUserName, "张三")
    .set(Account::getAge, 25)
    .where(Account::getId).eq("xxx")
    .update();

// 原子更新（Atomic Update）
UpdateChain.of(Account.class)
    .set(Account::getAge, ACCOUNT.AGE.add(1))
    .where(Account::getId).ge("xxx")
    .update();
```

### DbChain 操作

```java
// 新增（Insert）
DbChain.table("tb_account")
    .set("user_name", "zhang san")
    .set("age", 18)
    .save();

// 查询（Select）
DbChain.table("tb_account")
    .select("id", "user_name")
    .where("age > ?", 18)
    .list();
```

## BaseMapper 操作

```java
// 新增（Insert）
accountMapper.insert(entity);
accountMapper.insertSelective(entity);  // 忽略 null

// 查询（Select）
accountMapper.selectOneById("xxx");
accountMapper.selectAll();
accountMapper.selectListByQuery(query);
accountMapper.paginate(1, 10, query);

// 更新（Update）
accountMapper.update(entity);  // 通过 ID 更新，忽略 null
accountMapper.updateByQuery(entity, query);

// 删除（Delete）
accountMapper.deleteById("xxx");
accountMapper.deleteByQuery(query);
```

## Service 层

> ⚠️ **重要限制**：ServiceImpl **不能**继承 IService，直接注入 Mapper 使用。

直接注入 Mapper 使用，不继承 IService：

```java
@Service
@RequiredArgsConstructor
public class AccountService {
    private final AccountMapper accountMapper;
    
    public List<Account> list() {
        return accountMapper.selectAll();
    }
    
    public Account getById(String id) {
        return accountMapper.selectOneById(id);
    }
}
```

## 事务管理（Transaction Management）

### 方式一：使用 `@Transactional` 注解

推荐在 Service 方法上使用 Spring 的 `@Transactional` 注解：

```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderMapper orderMapper;
    
    @Transactional
    public void createOrder(Order order) {
        orderMapper.insert(order);
        // 其他数据库操作...
    }
    
    @Transactional(readOnly = true)
    public Order getOrder(String id) {
        return orderMapper.selectOneById(id);
    }
}
```

### 方式二：使用 `TransactionUtil` 工具类

适用于需要编程式事务控制的场景。需要 `spring-tx` 的 `PlatformTransactionManager`。

**源码位置**：见 `references/08-transaction-util.md`

**使用示例**：见 `references/08-transaction-util.md`

## 参考文档（Reference）

详细信息请查阅 `references/` 目录：

- **00-apt-configuration.md** - APT 代码生成配置（TableDef、Mapper 自动生成）
- **01-annotations.md** - 实体注解详解（@Table、@Id、@Column、@Relation 等）
- **02-querywrapper-advanced.md** - QueryWrapper 高级用法（多表关联、子查询、SQL 函数等）
- **02a-querychain.md** - QueryChain 链式查询详解（基于 QueryWrapper，提供 one/list/page/obj 等便捷方法）
- **03-base-entities.md** - 基础实体类与配置（BaseEntity、UUIDv7、自动填充、TransactionUtil）
- **04-service-mapper.md** - Service 与 Mapper 操作参考
- **05-type-handling.md** - 数据类型处理（枚举、JSON、日期等）
- **06-source-api.md** - 源码级 API 参考（QueryMethods、QueryWrapper、ChainQuery 完整方法列表）
- **07-optional-field.md** - OptionalField 三态值类型（部分更新场景）
- **08-transaction-util.md** - TransactionUtil 事务工具类源码

## 常用导入（Common Imports）

```java
import com.mybatisflex.core.query.QueryWrapper;
import com.mybatisflex.core.query.QueryChain;
import com.mybatisflex.core.update.UpdateChain;
import com.mybatisflex.core.update.UpdateEntity;
import com.mybatisflex.core.row.Db;
import com.mybatisflex.core.row.DbChain;
import com.mybatisflex.core.keygen.KeyGeneratorFactory;
import com.mybatisflex.annotation.Id;
import com.mybatisflex.annotation.KeyType;

// APT 生成的 TableDef
import static com.example.common.entity.table.AccountTableDef.ACCOUNT;

// SQL 函数（SQL Functions）
import com.mybatisflex.core.query.QueryMethods;
```
