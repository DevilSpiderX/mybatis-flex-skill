#!/usr/bin/env python3
"""为多宿主生成可安装的分发包（Claude 插件、Codex 插件、portable skill）。

用法：
    python3 scripts/build.py            # 生成 dist/ 下全部宿主包
    python3 scripts/build.py --clean    # 先生成再校验（等效，校验始终执行）

产物结构（dist/）：
    claude-plugin/      Claude 插件：.claude-plugin/plugin.json + hooks/ + LICENSE
                       + skills/mybatis-flex-skill/{LICENSE, SKILL.md, references/}
    codex-plugin/       Codex 插件：.codex-plugin/plugin.json + hooks/ + LICENSE
                       + skills/mybatis-flex-skill/{LICENSE, SKILL.md, agents/, references/}
    portable-skill/     纯 skill 目录：SKILL.md + references/（各宿主通用，无 hooks）

仅依赖 Python 3 标准库。源文件缺失时失败退出并打印缺失项。
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DIST_ROOT = REPO_ROOT / "dist"

PACKAGES: dict[str, list[str]] = {
    # package: (复制规则) —— 元组为 (目标子路径, 源路径) 列表
    # 两个宿主包内部布局保持一致：skills/<name>/ + hooks/hooks.json + LICENSE
    # 仅 manifest 目录（.claude-plugin/ vs .codex-plugin/）与 hooks 内容不同。
    # Codex 包多一个 agents/openai.yaml（Codex 宿主规范）。
    "claude-plugin": [
        (".claude-plugin/plugin.json", ".claude-plugin/plugin.json"),
        ("LICENSE", "LICENSE"),
        ("hooks/hooks.json", "hooks/hooks.json"),
        ("hooks/session_activation.py", "hooks/session_activation.py"),
        ("skills/mybatis-flex-skill/LICENSE", "LICENSE"),
        ("skills/mybatis-flex-skill/SKILL.md", "SKILL.md"),
        ("skills/mybatis-flex-skill/references", "references"),
    ],
    "codex-plugin": [
        (".codex-plugin/plugin.json", ".codex-plugin/plugin.json"),
        ("LICENSE", "LICENSE"),
        ("hooks/hooks.json", "hooks/hooks.codex.json"),
        ("hooks/session_activation.py", "hooks/session_activation.py"),
        ("skills/mybatis-flex-skill/LICENSE", "LICENSE"),
        ("skills/mybatis-flex-skill/SKILL.md", "SKILL.md"),
        ("skills/mybatis-flex-skill/agents/openai.yaml", "agents/openai.yaml"),
        ("skills/mybatis-flex-skill/references", "references"),
    ],
    "portable-skill": [
        ("SKILL.md", "SKILL.md"),
        ("references", "references"),
    ],
}

MANIFEST_KEYS = {
    "claude-plugin": [
        ".claude-plugin/plugin.json",
        "LICENSE",
        "hooks/hooks.json",
        "skills/mybatis-flex-skill/LICENSE",
        "skills/mybatis-flex-skill/SKILL.md",
        "skills/mybatis-flex-skill/references",
    ],
    "codex-plugin": [
        ".codex-plugin/plugin.json",
        "LICENSE",
        "hooks/hooks.json",
        "skills/mybatis-flex-skill/LICENSE",
        "skills/mybatis-flex-skill/SKILL.md",
        "skills/mybatis-flex-skill/agents/openai.yaml",
        "skills/mybatis-flex-skill/references",
    ],
    "portable-skill": ["SKILL.md"],
}


def missing_sources(rules: list[tuple[str, str]]) -> list[str]:
    return [src for _dst, src in rules if not (REPO_ROOT / src).exists()]


def copy_package(name: str, rules: list[tuple[str, str]]) -> None:
    target = DIST_ROOT / name
    if target.exists():
        shutil.rmtree(target)
    for dst_rel, src_rel in rules:
        source = REPO_ROOT / src_rel
        dest = target / dst_rel
        if source.is_dir():
            shutil.copytree(source, dest, dirs_exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)


def validate_package(name: str) -> list[str]:
    problems: list[str] = []
    root = DIST_ROOT / name
    for rel in MANIFEST_KEYS[name]:
        if not (root / rel).exists():
            problems.append(f"{name}/{rel} 缺失")
    for manifest_rel in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
        manifest_path = root / manifest_rel
        if manifest_path.exists():
            try:
                json.loads(manifest_path.read_text(encoding="utf-8"))
            except (OSError, ValueError, RecursionError) as exc:
                problems.append(f"{name}/{manifest_rel} 不是合法 JSON: {exc}")
    return problems


def main() -> int:
    ok = True
    for package, rules in PACKAGES.items():
        missing = missing_sources(rules)
        if missing:
            print(f"[失败] {package}: 源文件缺失 -> {missing}", file=sys.stderr)
            ok = False
            continue
        copy_package(package, rules)
        problems = validate_package(package)
        if problems:
            print(f"[失败] {package}:", file=sys.stderr)
            for problem in problems:
                print(f"  - {problem}", file=sys.stderr)
            ok = False
        else:
            print(f"[完成] dist/{package}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
