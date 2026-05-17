#!/usr/bin/env python3
"""Internal token-discipline check for prompt-reformatter.

This is intentionally quiet: it is not a public performance benchmark. It
keeps the skill honest about progressive disclosure and compact scaffolding.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIMITS = {
    "skill_body_lines": 120,
    "skill_body_words": 1200,
    "description_chars": 1024,
    "scaffold_keys": 7,
    "scaffold_words": 80,
    "reference_file_words": 1200,
}
SCAFFOLD_KEYS = ["verb", "slots", "gaps", "flags", "assumptions", "secondary", "confidence"]


def report(label: str, ok: bool, detail: str = "") -> bool:
    status = "PASS" if ok else "FAIL"
    suffix = f" - {detail}" if detail else ""
    print(f"{status}: {label}{suffix}")
    return ok


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise ValueError("missing frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("missing closing frontmatter")
    raw = text[4:end]
    body = text[end + 5:]
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
    return data, body


def compact_scaffold(prompt: str, expected_verb: str | None, expected_slots: dict, expected_gaps: list, expected_flags: list) -> dict:
    if expected_verb is None:
        return {"verb": None}
    return {
        "verb": expected_verb,
        "slots": sorted(expected_slots),
        "gaps": expected_gaps,
        "flags": expected_flags,
        "assumptions": [] if not expected_gaps else ["ask one focused question"],
    }


def scaffold_word_count(scaffold: dict) -> int:
    return word_count(json.dumps(scaffold, separators=(",", ":"), ensure_ascii=False))


def main() -> int:
    checks: list[bool] = []

    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(skill_text)
    body_lines = len(body.splitlines())
    body_words = word_count(body)
    description_chars = len(frontmatter.get("description", ""))

    checks.append(report("SKILL.md body line budget", body_lines <= LIMITS["skill_body_lines"], f"{body_lines}/{LIMITS['skill_body_lines']} lines"))
    checks.append(report("SKILL.md body word budget", body_words <= LIMITS["skill_body_words"], f"{body_words}/{LIMITS['skill_body_words']} words"))
    checks.append(report("description char budget", description_chars <= LIMITS["description_chars"], f"{description_chars}/{LIMITS['description_chars']} chars"))
    checks.append(report("token discipline section present", "## Token Discipline" in body))

    for path in sorted((ROOT / "references").glob("*")):
        if path.suffix not in {".json", ".md"}:
            continue
        words = word_count(path.read_text(encoding="utf-8"))
        checks.append(report(f"reference file word budget: {path.name}", words <= LIMITS["reference_file_words"], f"{words}/{LIMITS['reference_file_words']} words"))

    prompts = []
    for path in sorted((ROOT / "assets").glob("*test-prompts.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        prompts.extend(data["tests"])

    max_keys = 0
    max_words = 0
    worst_prompt = ""
    for test in prompts:
        scaffold = compact_scaffold(
            test["prompt"],
            test["expected_verb"],
            test["expected_slots"],
            test["expected_gaps"],
            test["expected_flags"],
        )
        keys = len(scaffold)
        words = scaffold_word_count(scaffold)
        if words > max_words:
            max_words = words
            worst_prompt = test["prompt"]
        max_keys = max(max_keys, keys)

    checks.append(report("compact scaffold key budget", max_keys <= LIMITS["scaffold_keys"], f"{max_keys}/{LIMITS['scaffold_keys']} keys"))
    checks.append(report("compact scaffold word budget", max_words <= LIMITS["scaffold_words"], f"{max_words}/{LIMITS['scaffold_words']} words; worst={worst_prompt!r}"))

    print()
    print("token discipline data")
    print(f"skill_body_lines: {body_lines}")
    print(f"skill_body_words: {body_words}")
    print(f"description_chars: {description_chars}")
    print(f"prompt_cases_sampled: {len(prompts)}")
    print(f"max_scaffold_keys: {max_keys}")
    print(f"max_scaffold_words: {max_words}")

    print()
    if all(checks):
        print("Token discipline check passed.")
        return 0
    print("Token discipline check failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
