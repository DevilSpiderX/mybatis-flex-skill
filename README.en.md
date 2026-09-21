# MyBatis-Flex Development Skill

[中文](README.md) | English

A LobeHub Skill that provides intelligent assistance for writing Java persistence layer code using the MyBatis-Flex framework.

## 📖 Introduction

This skill activates only when a backend project clearly uses MyBatis-Flex dependencies or syntax, including:

- Entity class definitions
- CRUD operations
- Chain queries
- Association queries
- Batch operations
- Transaction management

It should not activate for plain MyBatis, MyBatis-Plus, JPA, or other ORM persistence tasks unless there is MyBatis-Flex evidence such as `com.mybatisflex` dependencies, `mybatis-flex.config`, `QueryChain`, `UpdateChain`, `DbChain`, `UpdateEntity`, `TableDef`, or `com.mybatisflex.*` imports.

## 🚀 Core Features

### Chain Operations First

```java
// QueryChain (BaseMapper has no queryChain() method; at mapper level use QueryChain.of(mapper))
List<Account> accounts = QueryChain.of(accountMapper)
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
    // Project-side UUIDv7 key generator (implementation & registration: 08-base-entities.md)
    @Id(keyType = KeyType.Generator, value = UUIDv7KeyGenerator.NAME)
    private String id;
    private String userName;
    private Integer age;
}
```

APT automatically generates TableDef classes for type-safe queries.

> 💡 **Recommended**: Enable APT auto-generation of Mapper interfaces. Configure `processor.mapper.generateEnable=true` and `processor.mapper.annotation=true` in `mybatis-flex.config`.

> ⚠️ **Key generator recommendation**: standardize on the project-side `UUIDv7KeyGenerator` from 08-base-entities.md (time-ordered, `char(32)` column; implement `IKeyGenerator` and register via `KeyGeneratorFactory.register(...)`). MyBatis-Flex 1.11.8 ships only `uuid` / `flexId` / `snowFlakeId` / `ulid` (`com.mybatisflex.core.keygen.KeyGenerators`) and has **no** UUIDv7 — do **not** use the built-in `KeyGenerators` constants directly; `BaseEntity` in the example is project-side code as well.

### APT Code Generation (Recommended)

MyBatis-Flex uses APT to automatically generate `TableDef` classes and `Mapper` interfaces at compile time.

**Configuration (`mybatis-flex.config` in project root):**
```properties
# mybatis-flex.config
processor.enable=true

# Enable Mapper interface auto-generation
processor.mapper.generateEnable=true

# Add @Mapper annotation to generated Mapper
processor.mapper.annotation=true

# Optional TableDef package
processor.tableDef.package=${entityPackage}.table
```

**Maven annotation processor:**
```xml
<path>
    <groupId>com.mybatis-flex</groupId>
    <artifactId>mybatis-flex-processor</artifactId>
    <version>${mybatis-flex.version}</version>
</path>
```

> See `references/01-apt-configuration.md` for details.

### Service Layer Best Practices

> ⚠️ **This skill's recommendation**: by default the Service layer **does not extend** the framework's IService/ServiceImpl; inject the Mapper directly (the framework does provide IService/ServiceImpl — whether to extend them is a project-style decision, not a framework restriction).

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

### OptionalField Ternary Value Type (Project-side Capability, NOT a Framework API)

> ⚠️ OptionalField is a **project-side custom** ternary value type (it does not exist in MyBatis-Flex 1.11.8), for handling partial update scenarios (e.g., PATCH requests). The framework-side counterpart is `UpdateEntity` (`com.mybatisflex.core.util.UpdateEntity.of(...)`).

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

> See [12-optional-field.md](references/12-optional-field.md) for details.

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
| [11-source-api.md](references/11-source-api.md) | Core source code analysis index (class hierarchy, sub-file navigation) |
| [11a-source-api.md](references/11a-source-api.md) | QueryMethods SQL functions (math/string/date/aggregate/CASE WHEN, etc.) |
| [11b-source-api.md](references/11b-source-api.md) | QueryWrapper / QueryWrapperAdapter / chained query source analysis |
| [11c-source-api.md](references/11c-source-api.md) | PropertySetter / UpdateWrapper / UpdateChain source analysis |
| [11d-source-api.md](references/11d-source-api.md) | If conditional utility class |
| [12-optional-field.md](references/12-optional-field.md) | OptionalField tri-state type (**project-side capability, not a framework API**) |
| [12a-optional-field-source.md](references/12a-optional-field-source.md) | OptionalField source code implementation (**project-side code, not framework source**) |
| [13-transaction-util.md](references/13-transaction-util.md) | TransactionUtil transaction utility (**project-side capability**; the framework-native programmatic API is `Db.tx`) |

## 📋 Common Imports

```java
import com.mybatisflex.core.query.QueryWrapper;
import com.mybatisflex.core.query.QueryChain;
import com.mybatisflex.core.update.UpdateChain;
import com.mybatisflex.core.row.Db;
import com.mybatisflex.core.row.DbChain;
import com.mybatisflex.core.paginate.Page;
import com.mybatisflex.annotation.Id;
import com.mybatisflex.annotation.KeyType;

// Project-side UUIDv7 key generator (see 08-base-entities.md)
import com.example.mybatisflex.keygen.UUIDv7KeyGenerator;

// APT-generated TableDef
import static com.example.common.entity.table.AccountTableDef.ACCOUNT;

// SQL functions
import com.mybatisflex.core.query.QueryMethods;
```

## 🛠️ Installation & Usage

### Requirements

- Java 17+
- MyBatis-Flex 1.11.8 (API verification baseline for this documentation)
- Spring Boot 3.x

### Installation

This skill follows the [Agent Skills Open Standard](https://agentskills.io/) and supports multiple AI coding tools. It also ships as a **plugin** for Claude Code / Codex with a `SessionStart` hook that actively detects the project and injects an activation context at session start, for reliable triggering.

> **💡 Quick Install**: Copy the entire project directory (including `SKILL.md` and `references/`) to the corresponding tool's skills directory.
>
> ⚠️ **Note**: The `references/` directory contains core reference documents and **must** be installed together with `SKILL.md`, otherwise the skill will not work properly.
>
> 📦 **Multi-host packages**: Run `python3 scripts/build.py` to generate `dist/` containing the Claude plugin, Codex plugin, and portable skill packages.

#### Claude Code (CLI + Desktop)

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

**Plugin form (recommended, with SessionStart hook)**: copy the whole repo directory into `~/.claude/skills/mybatis-flex-skill/` (or project `.claude/skills/mybatis-flex-skill/`). Since it contains `.claude-plugin/plugin.json`, Claude Code loads it as the `mybatis-flex-skill@skills-dir` plugin and enables `hooks/hooks.json` automatically:

- `SessionStart` / `UserPromptSubmit` hooks **boundedly detect** whether the current project uses MyBatis-Flex;
- on a hit, a short activation context is injected so the model routes to `references/` per `SKILL.md`;
- on a miss, **zero output** — no tokens consumed (performance optimization);
- injected once per session (deduplicated); re-detected and refreshed after `resume`/`clear`/`compact`.

> Project-level `.claude/skills/` plugins require accepting the workspace trust dialog; user-level `~/.claude/skills/` has no such restriction.

#### Codex (OpenAI)

```bash
# Project level (recommended)
cp -r . /path/to/your-project/.agents/skills/mybatis-flex-skill

# Or user global level
cp -r . ~/.agents/skills/mybatis-flex-skill
```

**Plugin form (with hooks)**: use the build output `dist/codex-plugin/` (with `.codex-plugin/plugin.json` and `hooks/hooks.json`), following the Codex plugin installation flow; hook logic is identical to the Claude side.

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
├── .claude-plugin/plugin.json      # Claude plugin manifest (optional, active when the dir is installed)
├── hooks/
│   ├── hooks.json                  # Claude SessionStart/UserPromptSubmit/PreCompact/PostCompact/PostToolUse/PostToolUseFailure hook
│   ├── hooks.codex.json            # Codex hook config (built to dist/codex-plugin/hooks/hooks.json)
│   └── session_activation.py       # Bounded evidence detection + activation context injection
├── .codex-plugin/plugin.json       # Codex plugin manifest (optional)
├── scripts/build.py                # Multi-host package build script
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
    ├── 11a-source-api.md
    ├── 11b-source-api.md
    ├── 11c-source-api.md
    ├── 11d-source-api.md
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
processor.tableDef.package=${entityPackage}.table
```

## 🚀 Trigger Mechanism & Performance

In plugin form (Claude Code / Codex), the `SessionStart` / `UserPromptSubmit` hooks are driven by the bundled
`hooks/session_activation.py`, designed for "low noise, fast return, consistent across surfaces":

| Goal | Implementation |
|------|----------------|
| Reliable triggering | `SessionStart` covers all session starts: `startup`/`resume`/`clear`/`compact` (see the matcher in `hooks/hooks.json`); behavior is identical across CLI, desktop app, IDE extensions, and SSH remote sessions (officially, hook events fire the same wherever Claude Code runs) |
| Zero noise | Injects the activation context only when MyBatis-Flex evidence is found (`com.mybatisflex` dependency, `mybatis-flex.config`, `com.mybatisflex` imports, `mybatis-flex:` in `application.yml`); zero output and zero token cost on a miss |
| Fast return | Bounded detection: reads only the first 256 KiB of candidate build files, scans at most 256 source files at up to 8 levels deep; typically <10ms, hook timeout 5s |
| Dedup | Injected once per session; re-detected and refreshed after `resume`/`clear`/`compact` so restored sessions keep the context |
| Stateless fallback | Runs statelessly when `CLAUDE_PLUGIN_DATA` / `PLUGIN_DATA` is missing; state files capped at 64 and auto-pruned |

> The official guidance is to put static context in `CLAUDE.md` rather than SessionStart. This skill puts the
> dynamic part (evidence detection + activation reminder) in the hook, while static routing and reference docs
> stay in `SKILL.md` / `references/` (loaded on demand, not all at once).

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
Page<Account> page = QueryChain.of(accountMapper)
    .where(ACCOUNT.AGE.ge(18))
    .page(new Page<>(1, 10));  // QueryChain only has page(Page) — no page(int, int) overload
```

### Transaction Management

```java
// Framework-native programmatic transaction: rollback on false/null or exception
Db.tx(() -> {
    orderMapper.insert(order);
    return true;
});
```

> For the project-side `TransactionUtil` wrapper over Spring `TransactionTemplate`, see [13-transaction-util.md](references/13-transaction-util.md) (project-side utility, not a framework API).

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

MIT License
