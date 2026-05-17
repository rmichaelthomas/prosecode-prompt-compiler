#!/usr/bin/env python3
"""Validate the prompt-reformatter skill package with standard library only."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def report(label: str, ok: bool, detail: str = "") -> bool:
    status = "PASS" if ok else "FAIL"
    suffix = f" - {detail}" if detail else ""
    print(f"{status}: {label}{suffix}")
    return ok


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing opening frontmatter delimiter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("missing closing frontmatter delimiter")
    raw = text[4:end]
    body = text[end + 5:]
    data: dict[str, object] = {}
    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
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
            if value:
                data[key] = value.strip("\"'")
            else:
                nested = {}
                i += 1
                while i < len(lines) and lines[i].startswith("  "):
                    child = lines[i].strip()
                    if ":" in child:
                        child_key, child_value = child.split(":", 1)
                        nested[child_key.strip()] = child_value.strip().strip("\"'")
                    i += 1
                data[key] = nested
                continue
        i += 1
    return data, body


def load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    checks: list[bool] = []

    skill_path = ROOT / "SKILL.md"
    try:
        frontmatter, body = parse_frontmatter(skill_path)
        checks.append(report("SKILL.md frontmatter parses", True))
    except Exception as exc:
        checks.append(report("SKILL.md frontmatter parses", False, str(exc)))
        frontmatter, body = {}, ""

    name = str(frontmatter.get("name", ""))
    description = str(frontmatter.get("description", ""))
    checks.append(report("name is kebab-case 1-64 chars", bool(re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?", name))))
    checks.append(report("description is 1-1024 chars", 1 <= len(description) <= 1024, f"{len(description)} chars"))
    checks.append(report("name matches parent dir", name == ROOT.name, f"name={name!r}, dir={ROOT.name!r}"))
    checks.append(report("frontmatter uses portable fields", set(frontmatter).issubset({"name", "description", "license", "metadata"})))
    checks.append(report("SKILL.md body under 500 lines", len(body.splitlines()) < 500, f"{len(body.splitlines())} lines"))

    json_paths = sorted((ROOT / "references").glob("*.json")) + sorted((ROOT / "assets").glob("*.json"))
    json_data = {}
    for path in json_paths:
        try:
            json_data[path.name] = load_json(path)
            checks.append(report(f"{path.relative_to(ROOT)} parses", True))
        except Exception as exc:
            checks.append(report(f"{path.relative_to(ROOT)} parses", False, str(exc)))

    signatures = json_data.get("verb-signatures.json", {})
    markers = json_data.get("phrase-markers.json", {})
    tests = json_data.get("test-prompts.json", {})
    contradictions = json_data.get("contradiction-rules.json", {})

    verbs = signatures.get("verbs", []) if isinstance(signatures, dict) else []
    verb_words = {v.get("word") for v in verbs if isinstance(v, dict)}
    marker_verbs = set(markers) - {"schema_version"} if isinstance(markers, dict) else set()

    checks.append(report("7 verbs", len(verbs) == 7, f"{len(verbs)} found"))
    slot_count = sum(len(v.get("slots", [])) for v in verbs if isinstance(v, dict))
    checks.append(report("24 total slots", slot_count == 24, f"{slot_count} found"))
    checks.append(report("every verb has phrase markers", verb_words.issubset(marker_verbs), f"missing={sorted(verb_words - marker_verbs)}"))

    marker_slot_gaps = []
    for verb in verbs:
        word = verb.get("word")
        for slot in verb.get("slots", []):
            slot_name = slot.get("name")
            if not isinstance(markers, dict) or slot_name not in markers.get(word, {}):
                marker_slot_gaps.append(f"{word}.{slot_name}")
    checks.append(report("every slot has phrase markers", not marker_slot_gaps, f"missing={marker_slot_gaps}"))

    test_items = tests.get("tests", []) if isinstance(tests, dict) else []
    checks.append(report("24 test prompts", len(test_items) == 24, f"{len(test_items)} found"))
    unknown_expected = sorted({
        item.get("expected_verb")
        for item in test_items
        if item.get("expected_verb") is not None and item.get("expected_verb") not in verb_words
    })
    checks.append(report("expected verbs exist", not unknown_expected, f"unknown={unknown_expected}"))

    rules = contradictions.get("rules", []) if isinstance(contradictions, dict) else []
    checks.append(report("8+ contradiction rules", len(rules) >= 8, f"{len(rules)} found"))

    print()
    if all(checks):
        print("All validation checks passed.")
        return 0
    print("Validation failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
