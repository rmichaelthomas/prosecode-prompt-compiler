#!/usr/bin/env python3
"""Pre-install sanity checks for the prosecode-prompt-compiler skill."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "references/intent-ir.md",
    "references/compiler-passes.md",
    "references/response-validation.md",
    "references/prompt-diffing.md",
    "references/skill-routing.md",
    "references/handoff-packets.md",
    "references/verb-signatures.json",
    "references/phrase-markers.json",
    "references/contradiction-rules.json",
    "references/human-prompt-patterns.json",
    "references/DESIGN_PROVENANCE.md",
    "assets/test-prompts.json",
    "assets/adversarial-test-prompts.json",
    "assets/live-eval-results.json",
    "scripts/validate-skill.py",
    "scripts/benchmark-prompts.py",
    "scripts/token-discipline-check.py",
    "scripts/install-check.py",
]


def report(label: str, ok: bool, detail: str = "") -> bool:
    status = "PASS" if ok else "FAIL"
    suffix = f" - {detail}" if detail else ""
    print(f"{status}: {label}{suffix}")
    return ok


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("missing closing frontmatter")
    raw = text[4:end]
    data: dict[str, str] = {}
    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value == ">":
                i += 1
                block = []
                while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                    block.append(lines[i].strip())
                    i += 1
                data[key] = " ".join(part for part in block if part).strip()
                continue
            data[key] = value.strip("\"'")
        i += 1
    return data


def target_path(path_text: str | None) -> Path:
    if path_text:
        return Path(path_text).expanduser()
    return Path.home() / ".codex" / "skills" / ROOT.name


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", help="optional installation target path")
    args = parser.parse_args()

    checks: list[bool] = []
    checks.append(report("running from prosecode-prompt-compiler folder", ROOT.name == "prosecode-prompt-compiler", str(ROOT)))

    for relative in REQUIRED_FILES:
        checks.append(report(f"required file exists: {relative}", (ROOT / relative).is_file()))

    try:
        frontmatter = parse_frontmatter(ROOT / "SKILL.md")
        checks.append(report("SKILL.md frontmatter parses", True))
    except Exception as exc:
        frontmatter = {}
        checks.append(report("SKILL.md frontmatter parses", False, str(exc)))

    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    checks.append(report("skill name matches folder", name == ROOT.name, f"name={name!r}"))
    checks.append(report("skill name is portable kebab-case", bool(re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?", name))))
    checks.append(report("description is under 1024 chars", 1 <= len(description) <= 1024, f"{len(description)} chars"))

    for relative in ["scripts/validate-skill.py", "scripts/benchmark-prompts.py", "scripts/token-discipline-check.py", "scripts/install-check.py"]:
        path = ROOT / relative
        checks.append(report(f"script executable: {relative}", os.access(path, os.X_OK)))

    target = target_path(args.target)
    checks.append(report("target parent exists or can be created", target.parent.exists() or target.parent.parent.exists(), str(target.parent)))
    if target.exists():
        checks.append(report("target is not an unexpected file", target.is_dir(), str(target)))
        checks.append(report("target is not already populated", not any(target.iterdir()) if target.is_dir() else False, str(target)))
    else:
        checks.append(report("target path available", True, str(target)))

    print()
    if all(checks):
        print(f"Install check passed. Ready to install to: {target}")
        return 0
    print("Install check failed. Resolve failures before installing.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
