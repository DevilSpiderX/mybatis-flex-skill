# MyBatis-Flex 开发技能

[English](README.en.md) | 中文

一个 LobeHub Skill，为使用 MyBatis-Flex 框架编写 Java 持久层代码提供智能辅助。

## 📖 简介

当后端项目明确使用 MyBatis-Flex 依赖或语法时，此技能将自动激活，包括：

- 实体类定义
- CRUD 操作
- 基础查询
- 自动映射
- 链式查询
- UpdateChain 条件更新
- 部分字段更新
- 关联查询
- 批量操作
- Db + Row
- Active Record
- IService
- SpringBoot 配置
- MyBatisFlexCustomizer
- 逻辑删除、乐观锁、多租户、权限、审计等核心能力
- 事务管理

不会因普通 MyBatis、MyBatis-Plus、JPA 或其他 ORM 持久层任务触发；除非项目中能看到 `com.mybatisflex` 依赖、`mybatis-flex.config`、`QueryChain`、`UpdateChain`、`DbChain`、`UpdateEntity`、`TableDef` 或 `com.mybatisflex.*` 导入等 MyBatis-Flex 证据。

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

// 字段有值才更新
UpdateChain.of(Account.class)
    .set(Account::getUserName, dto.getUserName(), If::hasText)
    .set(Account::getAge, dto.getAge(), If::notNull)
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

> 详细信息请查阅 `references/12-optional-field.md`

## 📚 参考文档

详细信息请查阅 `references/` 目录：

| 文档 | 说明 |
|------|------|
| [00-index.md](references/00-index.md) | 官网功能地图与当前 references 对照 |
| [01-apt-configuration.md](references/01-apt-configuration.md) | APT 代码生成配置（TableDef、Mapper 自动生成） |
| [02-annotations.md](references/02-annotations.md) | 实体注解详解（@Table、@Id、@Column、@Relation 等） |
| [03-basic-features.md](references/03-basic-features.md) | 官网基础功能用例补齐 |
| [04-querywrapper-advanced.md](references/04-querywrapper-advanced.md) | QueryWrapper 高级用法（多表关联、子查询、SQL 函数等） |
| [05-querychain.md](references/05-querychain.md) | QueryChain 链式查询（链式调用封装，直接返回结果） |
| [06-updatechain.md](references/06-updatechain.md) | UpdateChain 链式更新（条件 set、setRaw、部分更新） |
| [07-core-features.md](references/07-core-features.md) | 官网核心功能用例补齐 |
| [08-base-entities.md](references/08-base-entities.md) | 基础实体类与配置（BaseEntity、UUIDv7、自动填充） |
| [09-service-mapper.md](references/09-service-mapper.md) | Service 与 Mapper 操作参考 |
| [10-type-handling.md](references/10-type-handling.md) | 数据类型处理（枚举、JSON、日期等） |
| [11-source-api.md](references/11-source-api.md) | 核心源码解析（QueryMethods SQL 函数、高级特性等） |
| [12-optional-field.md](references/12-optional-field.md) | OptionalField 三态值类型（部分更新场景） |
| [12a-optional-field-source.md](references/12a-optional-field-source.md) | OptionalField 源码实现 |
| [13-transaction-util.md](references/13-transaction-util.md) | TransactionUtil 事务工具类（简化编程式事务管理） |

## 📋 常用导入

```java
import com.mybatisflex.core.query.QueryWrapper;
import com.mybatisflex.core.query.If;
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

### 配置要求

- Java 17+
- MyBatis-Flex 1.9+
- Spring Boot 3.x

### 安装方式

本技能遵循 [Agent Skills 开放标准](https://agentskills.io/)，支持多种 AI 编程工具。

> **💡 快速安装**：将整个项目目录（包含 `SKILL.md` 和 `references/`）复制到对应工具的 skills 目录下。
>
> ⚠️ **注意**：`references/` 目录包含核心参考文档，必须随 `SKILL.md` 一起安装，否则技能无法正常工作。

#### Claude Code

```bash
# 项目级别（推荐，随项目版本控制）
cp -r . /path/to/your-project/.claude/skills/mybatis-flex-skill

# 或用户全局级别（所有项目可用）
cp -r . ~/.claude/skills/mybatis-flex-skill
```

也可在项目根目录的 `CLAUDE.md` 中导入：

```markdown
@.claude/skills/mybatis-flex-skill/SKILL.md
```

#### Codex (OpenAI)

```bash
# 项目级别（推荐）
cp -r . /path/to/your-project/.agents/skills/mybatis-flex-skill

# 或用户全局级别
cp -r . ~/.agents/skills/mybatis-flex-skill
```

也可通过 Codex CLI 内置的 `$skill-installer` 安装（如果技能已发布到社区）。

#### OpenCode

```bash
# 项目级别（推荐）
cp -r . /path/to/your-project/.opencode/skills/mybatis-flex-skill

# 或用户全局级别
cp -r . ~/.config/opencode/skills/mybatis-flex-skill
```

> **📝 说明**：OpenCode 同时兼容 `.claude/skills/` 和 `.agents/skills/` 路径，如果你已经为 Claude Code 或 Codex 安装过，OpenCode 会自动发现。

#### LobeHub

```bash
# 通过 LobeHub 市场安装
lobe skill install mybatis-flex-skill
```

### 安装目录速查

| 工具 | 项目级路径 | 全局路径 |
|------|-----------|---------|
| Claude Code | `.claude/skills/mybatis-flex-skill/` | `~/.claude/skills/mybatis-flex-skill/` |
| Codex | `.agents/skills/mybatis-flex-skill/` | `~/.agents/skills/mybatis-flex-skill/` |
| OpenCode | `.opencode/skills/mybatis-flex-skill/` | `~/.config/opencode/skills/mybatis-flex-skill/` |
| LobeHub | 通过 LobeHub 市场安装 | — |

安装后目录结构应如下：

```
mybatis-flex-skill/
├── SKILL.md
└── references/
    ├── 00-index.md
    ├── 01-apt-configuration.md
    ├── 02-annotations.md
    ├── 03-basic-features.md
    ├── 04-querywrapper-advanced.md
    ├── 05-querychain.md
    ├── 06-updatechain.md
    ├── 07-core-features.md
    ├── 08-base-entities.md
    ├── 09-service-mapper.md
    ├── 10-type-handling.md
    ├── 11-source-api.md
    ├── 12-optional-field.md
    ├── 12a-optional-field-source.md
    └── 13-transaction-util.md
```

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
