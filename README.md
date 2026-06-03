# MyBatis-Flex 开发技能

[English](#english) | 中文

一个 LobeHub Skill，为使用 MyBatis-Flex 框架编写 Java 持久层代码提供智能辅助。

## 📖 简介

当您需要使用 MyBatis-Flex 框架编写 Java 持久层代码时，此技能将自动激活，包括：

- 实体类定义
- CRUD 操作
- 链式查询
- 关联查询
- 批量操作
- 事务管理

## 🚀 核心特性

### 优先使用链式操作

```java
// QueryChain 查询
List<Account> accounts = accountMapper.queryChain()
    .where(ACCOUNT.AGE.ge(18))
    .and(ACCOUNT.USER_NAME.like("michael"))
    .list();

// UpdateChain 更新
UpdateChain.of(Account.class)
    .set(Account::getUserName, "张三")
    .where(Account::getId).eq("xxx")
    .update();
```

### 实体类定义

```java
@Table("tb_account")
public class Account extends BaseEntity {
    @Id(keyType = KeyType.Generator, value = UUIDv7KeyGenerator.NAME)
    private String id;
    private String userName;
    private Integer age;
}
```

APT 自动生成 TableDef 类，用于类型安全查询。

### Service 层最佳实践

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
}
```

### OptionalField 三态值类型（可选功能）

> OptionalField 是自定义的三态值类型，用于处理部分更新场景（如 PATCH 请求）。

| 状态 | 含义 | UpdateEntity 行为 |
|------|------|-------------------|
| `VALUE` | 有值 | `set(field, value)` |
| `NULL` | 字段存在但为 null | `set(field, null)` |
| `MISSING` | 字段不存在 | 忽略，不调用 set |

```java
// DTO 定义
@Data
public class UserUpdateDTO {
    private OptionalField<String> name = OptionalField.missing();  // 不修改
    private OptionalField<Integer> age = OptionalField.of(25);     // 设置为 25
    private OptionalField<String> email = OptionalField._null();   // 设置为 null
}

// Service 使用
public void updateUser(String userId, UserUpdateDTO dto) {
    User updateEntity = OptionalDtoUtil.toUpdateEntity(dto, User.class, userId);
    userMapper.update(updateEntity);
}
```

> 详细信息请查阅 `references/07-optional-field.md`

## 📚 参考文档

详细信息请查阅 `references/` 目录：

| 文档 | 说明 |
|------|------|
| [01-annotations.md](references/01-annotations.md) | 实体注解详解（@Table、@Id、@Column、@Relation 等） |
| [02-querywrapper-advanced.md](references/02-querywrapper-advanced.md) | QueryWrapper 高级用法（多表关联、子查询、SQL 函数等） |
| [03-base-entities.md](references/03-base-entities.md) | 基础实体类与配置（BaseEntity、UUIDv7、自动填充、TransactionUtil） |
| [04-service-mapper.md](references/04-service-mapper.md) | Service 与 Mapper 操作参考 |
| [05-type-handling.md](references/05-type-handling.md) | 数据类型处理（枚举、JSON、日期等） |

## 📋 常用导入

```java
import com.mybatisflex.core.query.QueryWrapper;
import com.mybatisflex.core.query.QueryChain;
import com.mybatisflex.core.update.UpdateChain;
import com.mybatisflex.core.row.Db;
import com.mybatisflex.core.row.DbChain;
import com.mybatisflex.annotation.Id;
import com.mybatisflex.annotation.KeyType;

// APT 生成的 TableDef
import static com.example.common.entity.table.AccountTableDef.ACCOUNT;

// SQL 函数
import com.mybatisflex.core.query.QueryMethods;
```

## 🛠️ 安装与使用

### 作为 LobeHub Skill 安装

```bash
# 通过 LobeHub 市场安装
lobe skill install mybatis-flex-skill
```

### 配置要求

- Java 17+
- MyBatis-Flex 1.9+
- Spring Boot 3.x

### APT 配置

```properties
# mybatis-flex.config
processor.enable=true
processor.mapper.generateEnable=true
processor.mapper.annotation=true
```

## 📝 功能速查

### 基础 CRUD

```java
// 新增
accountMapper.insert(entity);
accountMapper.insertSelective(entity);  // 忽略 null

// 查询
accountMapper.selectOneById("xxx");
accountMapper.selectAll();

// 更新
accountMapper.update(entity);  // ID 更新，忽略 null

// 删除
accountMapper.deleteById("xxx");
```

### 分页查询

```java
Page<Account> page = accountMapper.queryChain()
    .where(ACCOUNT.AGE.ge(18))
    .page(1, 10);
```

### 事务管理

```java
TransactionUtil.execute(transactionManager, status -> {
    orderMapper.insert(order);
    return null;
});
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

<a name="english"></a>
## English

# MyBatis-Flex Development Skill

A LobeHub Skill that provides intelligent assistance for writing Java persistence layer code using the MyBatis-Flex framework.

### Features

- Entity class definition
- CRUD operations
- Chain queries
- Association queries
- Batch operations
- Transaction management

### Documentation

See the `references/` directory for detailed documentation.

### License

MIT License
