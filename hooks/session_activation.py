#!/usr/bin/env python3
"""MyBatis-Flex skill 的会话启动激活守卫。

SessionStart / UserPromptSubmit hook：有界检测当前项目是否使用 MyBatis-Flex，
命中时注入一段简短激活上下文，提醒模型按 SKILL.md 快速路由按需读取 references/ 文档。

设计目标：
- 快速：只读取少量候选文件的有界前缀，默认在 2 秒内返回。
- 零噪音：未检测到 MyBatis-Flex 证据时输出为空（不消耗任何 token）。
- 去重：同一会话内只注入一次激活上下文，后续 prompt 不重复注入（性能优化）。
- 无状态依赖：缺少 CLAUDE_PLUGIN_DATA 时仍可无状态运行。

仅依赖 Python 3 标准库。
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

MAX_INPUT_CHARS = 1 << 20  # 1 MiB，hook 输入上限
MAX_FILE_PREFIX = 256 * 1024  # 单文件只读前 256 KiB
MAX_SRC_FILES = 256  # 源码扫描文件数上限
MAX_STATE_FILES = 64  # 会话状态文件数上限
MAX_STATE_CHARS = 16 * 1024
SUCCESS_EXIT = 0

EVENT_SESSION_START = "SessionStart"
EVENT_USER_PROMPT_SUBMIT = "UserPromptSubmit"

DATA_ENV = "CLAUDE_PLUGIN_DATA"
DATA_ENV_FALLBACK = "PLUGIN_DATA"  # Codex 等宿主的环境变量名
DATA_DIR_NAME = "activation"
STATE_SUFFIX = ".json"
TEMP_SUFFIX = ".tmp"

# 构建文件与配置文件中的证据关键词（Maven / Gradle / mybatis-flex.config）
BUILD_FILE_NAMES = (
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "settings.gradle",
    "settings.gradle.kts",
    "gradle.properties",
    "mybatis-flex.config",
    "application.yml",
    "application.yaml",
    "application.properties",
)
BUILD_KEYWORDS = (
    "mybatis-flex",
    "com.mybatisflex",
    "mybatis-flex.config",
)
SRC_KEYWORDS = (
    "com.mybatisflex",
    "mybatis-flex.config",
    "mybatis-flex:",
    "mybatis-flex-spring",
    "mybatis-flex-starter",
)
SRC_PATTERNS = (
    ("src", "main", "java", (".java", ".kt", ".groovy")),
    ("src", "main", "kotlin", (".java", ".kt", ".groovy")),
    ("src", "main", "groovy", (".java", ".kt", ".groovy")),
    ("src", "main", "resources", (".yml", ".yaml", ".properties", ".xml", ".config")),
)
MAX_SRC_DEPTH = 8

ACTIVATION_CONTEXT = (
    "检测到当前项目使用 MyBatis-Flex（存在 com.mybatisflex 依赖、mybatis-flex.config "
    "或 com.mybatisflex 导入）。本会话已安装 mybatis-flex-skill：处理实体注解、"
    "QueryChain/UpdateChain、TableDef、APT 代码生成、逻辑删除、乐观锁、多租户、事务等 "
    "MyBatis-Flex 能力时，按该技能 SKILL.md 的快速路由表按需读取 references/ 对应文档，"
    "不要一次性加载全部参考文件。"
)


def read_hook_input() -> dict[str, Any]:
    """有界读取宿主 Hook 输入。"""
    raw = sys.stdin.read(MAX_INPUT_CHARS + 1)
    if len(raw) > MAX_INPUT_CHARS:
        return {}
    try:
        payload = json.loads(raw)
    except (ValueError, RecursionError):
        return {}
    return payload if isinstance(payload, dict) else {}


def project_root(payload: dict[str, Any]) -> Path:
    """确定项目根：优先事件 cwd，其次 CLAUDE_PROJECT_DIR，最后当前目录。"""
    cwd = payload.get("cwd")
    if isinstance(cwd, str) and cwd:
        return Path(cwd)
    env_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if env_dir:
        return Path(env_dir)
    return Path.cwd()


def file_has_keyword(path: Path, keywords: tuple[str, ...]) -> bool:
    """读取文件有界前缀并检查是否命中任一关键词。"""
    if not path.is_file():
        return False
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as source:
            head = source.read(MAX_FILE_PREFIX)
    except OSError:
        return False
    lower = head.lower()
    return any(keyword.lower() in lower for keyword in keywords)


def scan_src_root(root: Path, rel_parts: tuple[str, ...]) -> bool:
    """在给定源码根下有界扫描关键词；限制文件数、深度与文件后缀。"""
    base = root.joinpath(*rel_parts[:-1])
    suffixes = rel_parts[-1]
    if not base.is_dir():
        return False
    visited = 0
    for current, _dirs, files in os.walk(base):
        depth = len(Path(current).relative_to(base).parts)
        if depth > MAX_SRC_DEPTH:
            continue
        for name in files:
            if not name.endswith(suffixes):
                continue
            visited += 1
            if visited > MAX_SRC_FILES:
                return False
            if file_has_keyword(Path(current) / name, SRC_KEYWORDS):
                return True
    return False


def has_mybatis_flex_evidence(root: Path) -> bool:
    """有界检测项目是否使用 MyBatis-Flex，命中任一证据即返回 True。"""
    for name in BUILD_FILE_NAMES:
        if file_has_keyword(root / name, BUILD_KEYWORDS):
            return True
    for pattern in SRC_PATTERNS:
        if scan_src_root(root, pattern):
            return True
    return False


def session_fingerprint(payload: dict[str, Any]) -> str:
    """会话标识的不可逆指纹，避免把会话 id 写入磁盘明文。"""
    session_id = payload.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        return ""
    return hashlib.sha256(session_id.encode("utf-8")).hexdigest()


def state_path(fingerprint: str) -> Path | None:
    """返回当前会话的私有状态文件；缺少宿主数据目录时安全降级。"""
    data_dir = os.environ.get(DATA_ENV) or os.environ.get(DATA_ENV_FALLBACK)
    if not data_dir or not fingerprint:
        return None
    return Path(data_dir) / DATA_DIR_NAME / f"{fingerprint}{STATE_SUFFIX}"


def load_state(path: Path | None) -> dict[str, Any]:
    """读取会话状态；损坏或缺失按空状态处理。"""
    if path is None or not path.exists():
        return {}
    try:
        raw = path.read_text(encoding="utf-8")[:MAX_STATE_CHARS]
        state = json.loads(raw)
    except (OSError, ValueError, RecursionError):
        return {}
    return state if isinstance(state, dict) else {}


def prune_state_files(directory: Path) -> None:
    """限制会话状态文件数量，避免长期运行后无界增长。"""
    try:
        files = sorted(
            directory.glob(f"*{STATE_SUFFIX}"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
    except OSError:
        return
    for stale in files[MAX_STATE_FILES:]:
        try:
            stale.unlink()
        except OSError:
            continue


def save_state(path: Path | None, state: dict[str, Any], is_new: bool) -> None:
    """原子写入会话状态；新会话建档时清理历史状态文件。"""
    if path is None:
        return
    tmp = path.with_name(f"{path.name}.{os.getpid()}{TEMP_SUFFIX}")
    try:
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        tmp.write_text(json.dumps(state, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        tmp.chmod(0o600)
        tmp.replace(path)
        if is_new:
            prune_state_files(path.parent)
    except OSError:
        return
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def context_output(event_name: str, context: str) -> dict[str, Any]:
    """返回 hook 的附加上下文输出。"""
    return {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": context,
        }
    }


def handle_event(payload: dict[str, Any]) -> dict[str, Any] | None:
    """处理激活事件；只在命中证据且本会话尚未注入时输出上下文。"""
    event_name = payload.get("hook_event_name")
    if event_name not in (EVENT_SESSION_START, EVENT_USER_PROMPT_SUBMIT):
        return None

    root = project_root(payload)
    if not root.is_dir():
        return None

    fingerprint = session_fingerprint(payload)
    path = state_path(fingerprint)
    state = load_state(path)
    is_new = not path or not path.exists()

    # SessionStart 是会话级刷新点：startup/resume/clear/compact 后重新检测并刷新状态；
    # UserPromptSubmit 只做兜底——SessionStart 已被宿主跳过时也能补一次激活。
    reset = event_name == EVENT_SESSION_START
    if reset:
        state = {}

    # 已评估过的会话跳过重复扫描（性能优化）；SessionStart 重置后重新评估。
    if state.get("checked"):
        return None

    hit = has_mybatis_flex_evidence(root)

    # 无论是否命中都记录 checked，避免同一会话反复扫描文件系统；
    # 未命中不注入上下文（零 token 消耗），状态留在磁盘供后续 prompt 直接跳过。
    state["checked"] = True
    if hit:
        state["injected"] = True
        state["last_event"] = event_name
        state["count"] = min(int(state.get("count", 0)) + 1, 2**31 - 1)
    save_state(path, state, is_new)

    if not hit:
        return None

    return context_output(event_name, ACTIVATION_CONTEXT)


def main() -> int:
    try:
        payload = read_hook_input()
        output = handle_event(payload)
    except (OSError, ValueError, RecursionError):
        return SUCCESS_EXIT
    if output is not None:
        print(json.dumps(output, ensure_ascii=False))
    return SUCCESS_EXIT


if __name__ == "__main__":
    raise SystemExit(main())
