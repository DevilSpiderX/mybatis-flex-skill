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

> 💡 **Recommended**: Enable APT auto-generation of Mapper interfaces. Configure `processor.mapper.generateEnable=true` and `processor.mapper.annotation=true` in `mybatis-flex.config`.

### APT Code Generation (Recommended)

MyBatis-Flex uses APT to automatically generate `TableDef` classes and `Mapper` interfaces at compile time.

**Configuration (`mybatis-flex.config` in project root):**
```properties
# mybatis-flex.config

# Enable Mapper interface auto-generation
processor.mapper.generateEnable=true

# Add @Mapper annotation to generated Mapper
processor.mapper.annotation=true

# Specify entity class package path
processor.mapper.generateInclude=com.example.entity.*
```

**Maven dependency:**
```xml
<dependency>
    <groupId>com.mybatisflex</groupId>
    <artifactId>mybatis-flex-processor</artifactId>
    <version>${mybatis-flex.version}</version>
    <scope>provided</scope>
</dependency>
```

> See `references/01-apt-configuration.md` for details.

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

> See `references/12-optional-field.md` for details.

## 📚 Reference Documentation

See the `references/` directory for details:

| Document | Description |
|----------|-------------|
| [00-index.md](references/00-index.md) | Official feature map and reference index |
| [01-apt-configuration.md](references/01-apt-configuration.md) | APT code generation configuration (TableDef, Mapper auto-generation) |
| [02-annotations.md](references/02-annotations.md) | Entity annotations (@Table, @Id, @Column, @Relation, etc.) |
| [03-basic-features.md](references/03-basic-features.md) | Official basic feature examples |
| [04-querywrapper-advanced.md](references/04-querywrapper-advanced.md) | QueryWrapper advanced usage (multi-table joins, subqueries, SQL functions, etc.) |
| [05-querychain.md](references/05-querychain.md) | QueryChain chained queries (chain call wrapper, direct result returns) |
| [06-updatechain.md](references/06-updatechain.md) | UpdateChain chained updates (conditional set, setRaw, partial update) |
| [07-core-features.md](references/07-core-features.md) | Official core feature examples |
| [08-base-entities.md](references/08-base-entities.md) | Base entity classes & configuration (BaseEntity, UUIDv7, auto-fill) |
| [09-service-mapper.md](references/09-service-mapper.md) | Service and Mapper operation reference |
| [10-type-handling.md](references/10-type-handling.md) | Data type handling (enums, JSON, dates, etc.) |
| [11-source-api.md](references/11-source-api.md) | Core source code analysis (QueryMethods SQL functions, advanced features, etc.) |
| [12-optional-field.md](references/12-optional-field.md) | OptionalField tri-state type (partial update scenarios) |
| [12a-optional-field-source.md](references/12a-optional-field-source.md) | OptionalField source code implementation |
| [13-transaction-util.md](references/13-transaction-util.md) | TransactionUtil transaction utility class (simplified programmatic transaction management) |

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
