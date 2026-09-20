# MyBatis-Flex 项目指导（消费方模板）

> 本文件既作为 `mybatis-flex-skill` 技能仓库的自述，也可**复制到消费方项目根**（或 `~/.agents/AGENTS.md` 用户全局），
> 作为 Codex / OpenCode 等项目指导，提升技能在项目内的触发稳定性。

## 触发条件

仅当目标项目明确使用 MyBatis-Flex 时使用 `mybatis-flex-skill`，证据包括：

- `com.mybatis-flex` Maven/Gradle 依赖（groupId 为 `com.mybatis-flex`）
- `mybatis-flex.config` 文件，或 `application.yml` 中的 `mybatis-flex:` 配置
- `com.mybatisflex.*` 导入、`TableDef`、`QueryChain`、`UpdateChain`、`DbChain`、`UpdateEntity`
- MyBatis-Flex 注解（`@Table`、`@Id`、`@Column`、`@Relation*`）或 APT 代码生成

MyBatis-Plus（`com.baomidou`）、原生 MyBatis、JPA 项目不适用本技能。

## 使用方式

按 `SKILL.md` 的"快速路由"表，按任务场景读取 `references/` 下对应文档；不要一次性加载全部参考文件。

## 安装

见 `README.md`。Claude Code 与 Codex 支持插件形态（带 SessionStart hook，自动检测并注入激活上下文）。
