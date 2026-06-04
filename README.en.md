# MyBatis-Flex Development Skill

[中文](README.md) | English

A LobeHub Skill that provides intelligent assistance for writing Java persistence layer code using the MyBatis-Flex framework.

## 📖 Introduction

This skill activates automatically when you need to write Java persistence layer code using the MyBatis-Flex framework, including:

- Entity class definitions
- CRUD operations
- Chain queries
- Association queries
- Batch operations
- Transaction management

## 🚀 Core Features

### Chain Operations First

```java
// QueryChain
List<Account> accounts = accountMapper.queryChain()
    .where(ACCOUNT.AGE.ge(18))
    .and(ACCOUNT.USER_NAME.like("michael"))
    .list();

// UpdateChain
UpdateChain.of(Account.class)
    .set(Account::getUserName, "John")
    .where(Account::getId).eq("xxx")
    .update();
```

### Entity Class Definitions

```java
@Table("tb_account")
public class Account extends BaseEntity {
    @Id(keyType = KeyType.Generator, value = UUIDv7KeyGenerator.NAME)
    private String id;
    private String userName;
    private Integer age;
}
```

APT automatically generates TableDef classes for type-safe queries.

### Service Layer Best Practices

> ⚠️ **Important Limitation**: ServiceImpl **cannot** extend IService. Inject Mapper directly.

Inject Mapper directly without extending IService:

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

### OptionalField Ternary Value Type (Optional Feature)

> OptionalField is a custom ternary value type for handling partial update scenarios (e.g., PATCH requests).

| State | Meaning | UpdateEntity Behavior |
|-------|---------|----------------------|
| `VALUE` | Has value | `set(field, value)` |
| `NULL` | Field exists but is null | `set(field, null)` |
| `MISSING` | Field does not exist | Ignored, no set call |

```java
// DTO definition
@Data
public class UserUpdateDTO {
    private OptionalField<String> name = OptionalField.missing();  // No change
    private OptionalField<Integer> age = OptionalField.of(25);     // Set to 25
    private OptionalField<String> email = OptionalField._null();   // Set to null
}

// Service usage
public void updateUser(String userId, UserUpdateDTO dto) {
    User updateEntity = OptionalDtoUtil.toUpdateEntity(dto, User.class, userId);
    userMapper.update(updateEntity);
}
```

> See `references/07-optional-field.md` for details.

## 📚 Reference Documentation

See the `references/` directory for details:

| Document | Description |
|----------|-------------|
| [01-annotations.md](references/01-annotations.md) | Entity annotations (@Table, @Id, @Column, @Relation, etc.) |
| [02-querywrapper-advanced.md](references/02-querywrapper-advanced.md) | QueryWrapper advanced usage (multi-table joins, subqueries, SQL functions, etc.) |
| [02a-querychain.md](references/02a-querychain.md) | QueryChain chained queries (chain call wrapper, direct result returns) |
| [03-base-entities.md](references/03-base-entities.md) | Base entity classes & configuration (BaseEntity, UUIDv7, auto-fill) |
| [04-service-mapper.md](references/04-service-mapper.md) | Service and Mapper operation reference |
| [05-type-handling.md](references/05-type-handling.md) | Data type handling (enums, JSON, dates, etc.) |
| [06-source-api.md](references/06-source-api.md) | Core source code analysis (QueryMethods SQL functions, advanced features, etc.) |
| [07-optional-field.md](references/07-optional-field.md) | OptionalField tri-state type (partial update scenarios) |
| [07-1-optional-field-source.md](references/07-1-optional-field-source.md) | OptionalField source code implementation |
| [08-transaction-util.md](references/08-transaction-util.md) | TransactionUtil transaction utility class (simplified programmatic transaction management) |

## 📋 Common Imports

```java
import com.mybatisflex.core.query.QueryWrapper;
import com.mybatisflex.core.query.QueryChain;
import com.mybatisflex.core.update.UpdateChain;
import com.mybatisflex.core.row.Db;
import com.mybatisflex.core.row.DbChain;
import com.mybatisflex.annotation.Id;
import com.mybatisflex.annotation.KeyType;

// APT-generated TableDef
import static com.example.common.entity.table.AccountTableDef.ACCOUNT;

// SQL functions
import com.mybatisflex.core.query.QueryMethods;
```

## 🛠️ Installation & Usage

### Requirements

- Java 17+
- MyBatis-Flex 1.9+
- Spring Boot 3.x

### Installation

This skill follows the [Agent Skills Open Standard](https://agentskills.io/) and supports multiple AI coding tools.

> **💡 Quick Install**: Copy the entire project directory (including `SKILL.md` and `references/`) to the corresponding tool's skills directory.
>
> ⚠️ **Note**: The `references/` directory contains core reference documents and **must** be installed together with `SKILL.md`, otherwise the skill will not work properly.

#### Claude Code

```bash
# Project level (recommended, version-controlled with project)
cp -r . /path/to/your-project/.claude/skills/mybatis-flex-skill

# Or user global level (available in all projects)
cp -r . ~/.claude/skills/mybatis-flex-skill
```

Alternatively, import in your project root's `CLAUDE.md`:

```markdown
@.claude/skills/mybatis-flex-skill/SKILL.md
```

#### Codex (OpenAI)

```bash
# Project level (recommended)
cp -r . /path/to/your-project/.agents/skills/mybatis-flex-skill

# Or user global level
cp -r . ~/.agents/skills/mybatis-flex-skill
```

You can also use the built-in `$skill-installer` in the Codex CLI (if the skill has been published to the community).

#### OpenCode

```bash
# Project level (recommended)
cp -r . /path/to/your-project/.opencode/skills/mybatis-flex-skill

# Or user global level
cp -r . ~/.config/opencode/skills/mybatis-flex-skill
```

> **📝 Note**: OpenCode is also compatible with `.claude/skills/` and `.agents/skills/` paths. If you've already installed for Claude Code or Codex, OpenCode will discover it automatically.

#### LobeHub

```bash
# Install via LobeHub marketplace
lobe skill install mybatis-flex-skill
```

### Installation Directory Quick Reference

| Tool | Project-level Path | Global Path |
|------|-------------------|-------------|
| Claude Code | `.claude/skills/mybatis-flex-skill/` | `~/.claude/skills/mybatis-flex-skill/` |
| Codex | `.agents/skills/mybatis-flex-skill/` | `~/.agents/skills/mybatis-flex-skill/` |
| OpenCode | `.opencode/skills/mybatis-flex-skill/` | `~/.config/opencode/skills/mybatis-flex-skill/` |
| LobeHub | Install via LobeHub marketplace | — |

After installation, the directory structure should look like this:

```
mybatis-flex-skill/
├── SKILL.md
└── references/
    ├── 01-annotations.md
    ├── 02-querywrapper-advanced.md
    ├── 02a-querychain.md
    ├── 03-base-entities.md
    ├── 04-service-mapper.md
    ├── 05-type-handling.md
    ├── 06-source-api.md
    ├── 07-optional-field.md
    ├── 07-1-optional-field-source.md
    └── 08-transaction-util.md
```

### APT Configuration

```properties
# mybatis-flex.config
processor.enable=true
processor.mapper.generateEnable=true
processor.mapper.annotation=true
```

## 📝 Feature Cheat Sheet

### Basic CRUD

```java
// Insert
accountMapper.insert(entity);
accountMapper.insertSelective(entity);  // Ignore nulls

// Query
accountMapper.selectOneById("xxx");
accountMapper.selectAll();

// Update
accountMapper.update(entity);  // Update by ID, ignore nulls

// Delete
accountMapper.deleteById("xxx");
```

### Paginated Query

```java
Page<Account> page = accountMapper.queryChain()
    .where(ACCOUNT.AGE.ge(18))
    .page(1, 10);
```

### Transaction Management

```java
TransactionUtil.execute(transactionManager, status -> {
    orderMapper.insert(order);
    return null;
});
```

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

MIT License
