#!/usr/bin/env python3
"""Run a deterministic prompt-classification benchmark for this skill.

This is a reference-table smoke test, not a model benchmark. It checks that
the bundled prompt cases are covered by the bounded marker vocabulary and
contradiction rules well enough to support the skill instructions.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERB_ORDER = ["explain", "create", "transform", "analyze", "decide", "plan", "fix"]
EDGE_MARKERS = {
    "greeting": ["hey", "hello", "hi ", "how's it going", "how are you"],
    "continuation": ["keep going", "go on", "continue", "more", "next"],
}
VERB_HINTS = {
    "explain": ["what is", "what are", "what does", "how does", "explain", "describe", "tell me about"],
    "create": ["write", "draft", "create", "make", "generate", "build", "compose", "produce", "give me", "design"],
    "transform": ["turn", "rewrite", "convert", "format", "summarize", "translate", "into", "as a"],
    "analyze": ["analyze", "analysis", "review", "evaluate", "assess", "inspect", "examine", "audit"],
    "decide": ["should i", "which", "choose", "choose between", "pick", "better", " versus ", " vs "],
    "plan": ["plan", "roadmap", "strategy", "how do i", "how can i", "steps to", "approach"],
    "fix": ["fix", "debug", "repair", "correct", "what's wrong with", "why is", "broken", "bug", "error", "crashes", "not loading"]
}


def load_json(relative: str) -> dict:
    with (ROOT / relative).open(encoding="utf-8") as fh:
        return json.load(fh)


def norm(text: str) -> str:
    return f" {(text or '').lower()} "


def has_any(text: str, phrases: list[str]) -> bool:
    x = norm(text)
    return any(p.lower() in x for p in phrases)


def marker_positions(text: str, phrases: list[str]) -> list[int]:
    x = text.lower()
    return [x.find(p.lower()) for p in phrases if x.find(p.lower()) >= 0]


def is_pass_through(prompt: str) -> bool:
    x = norm(prompt)
    return any(has_any(x, markers) for markers in EDGE_MARKERS.values())


def infer_verb(prompt: str, phrase_markers: dict) -> str | None:
    if is_pass_through(prompt):
        return None

    x = prompt.lower()

    # Reorderer rule 7: brokenness markers override apparent explanation.
    if has_any(x, VERB_HINTS["fix"]):
        return "fix"

    # Common transform form: "make/rewrite this/the X [style]".
    if re.search(r"\b(make|rewrite|turn|convert|format|summarize|translate)\b.*\b(this|the|my|following)\b", x):
        if has_any(x, phrase_markers["transform"]["constraints"] + phrase_markers["create"]["style"]):
            return "transform"

    # Compound intent: primary intent is the earliest recognizable verb.
    candidates: list[tuple[int, str, int]] = []
    for priority, verb in enumerate(VERB_ORDER):
        positions = marker_positions(x, VERB_HINTS[verb])
        if positions:
            candidates.append((min(positions), verb, priority))
    if candidates:
        candidates.sort(key=lambda item: (item[0], item[2]))
        return candidates[0][1]

    # Slot markers can still imply a verb when no direct intent word appears.
    scores: dict[str, int] = {}
    for verb, slots in phrase_markers.items():
        if verb == "schema_version":
            continue
        scores[verb] = sum(1 for markers in slots.values() if has_any(x, markers))
    best = max(scores, key=lambda verb: scores[verb])
    return best if scores[best] > 0 else None


def infer_slot_keys(prompt: str, verb: str | None, signatures: dict, phrase_markers: dict) -> set[str]:
    if verb is None:
        return set()
    x = prompt.lower()
    verb_sig = next(v for v in signatures["verbs"] if v["word"] == verb)
    slot_keys = set()
    for slot in verb_sig["slots"]:
        name = slot["name"]
        markers = phrase_markers.get(verb, {}).get(name, [])
        if slot["required"] or has_any(x, markers):
            slot_keys.add(name)

    # A few question-form and compound cases imply optional slots without a
    # clean marker phrase. This mirrors the SKILL.md reorderer rules.
    if verb == "create" and has_any(x, ["for my", "for new", "for customers", "for executives", "for the board"]):
        slot_keys.add("audience")
    if verb == "transform" and has_any(x, ["concise", "without changing", "casual", "formal enough"]):
        slot_keys.add("constraints")
    if verb == "analyze" and has_any(x, ["for ", "as bullets", "summary", "findings"]):
        slot_keys.add("criteria" if " for " in norm(x) else "format")
    if verb == "analyze" and has_any(x, ["fast", "thorough", "careful", "rigorous"]):
        slot_keys.add("criteria")
    if verb == "decide" and has_any(x, ["for ", "given that", "optimizing for"]):
        slot_keys.add("context" if " for " in norm(x) else "criteria")
    if verb == "plan" and has_any(x, [" by ", "with only", "within", "deadline"]):
        slot_keys.add("constraints")
    if verb == "fix" and has_any(x, ["crashes", "not loading", "fails", "error", "doesn't work"]):
        slot_keys.add("symptoms")
    return slot_keys


def infer_flags(prompt: str, contradiction_rules: dict) -> list[str]:
    flags = []
    for rule in contradiction_rules["rules"]:
        if has_any(prompt, rule["markers_a"]) and has_any(prompt, rule["markers_b"]):
            flags.append(rule["name"])
    return flags


def run_benchmark(verbose: bool = False) -> int:
    tests = load_json("assets/test-prompts.json")["tests"]
    signatures = load_json("references/verb-signatures.json")
    phrase_markers = load_json("references/phrase-markers.json")
    contradiction_rules = load_json("references/contradiction-rules.json")

    verb_hits = 0
    flag_hits = 0
    flag_total = 0
    slot_hits = 0
    slot_total = 0
    failures = []

    for index, test in enumerate(tests, 1):
        prompt = test["prompt"]
        expected_verb = test["expected_verb"]
        expected_flags = set(test["expected_flags"])
        expected_slots = set(test["expected_slots"])

        actual_verb = infer_verb(prompt, phrase_markers)
        actual_flags = set(infer_flags(prompt, contradiction_rules))
        actual_slots = infer_slot_keys(prompt, actual_verb, signatures, phrase_markers)

        verb_ok = actual_verb == expected_verb
        flags_ok = expected_flags.issubset(actual_flags)
        slot_ok = expected_slots.issubset(actual_slots)

        verb_hits += int(verb_ok)
        flag_hits += len(expected_flags & actual_flags)
        flag_total += len(expected_flags)
        slot_hits += len(expected_slots & actual_slots)
        slot_total += len(expected_slots)

        if not (verb_ok and flags_ok and slot_ok):
            failures.append({
                "index": index,
                "prompt": prompt,
                "expected_verb": expected_verb,
                "actual_verb": actual_verb,
                "expected_flags": sorted(expected_flags),
                "actual_flags": sorted(actual_flags),
                "missing_slots": sorted(expected_slots - actual_slots),
                "notes": test["notes"]
            })

    verb_accuracy = verb_hits / len(tests)
    flag_recall = 1.0 if flag_total == 0 else flag_hits / flag_total
    slot_recall = 1.0 if slot_total == 0 else slot_hits / slot_total
    combined = (verb_accuracy + flag_recall + slot_recall) / 3

    print("prompt-reformatter benchmark")
    print(f"cases: {len(tests)}")
    print(f"verb_accuracy: {verb_hits}/{len(tests)} = {verb_accuracy:.1%}")
    print(f"flag_recall: {flag_hits}/{flag_total} = {flag_recall:.1%}")
    print(f"slot_key_recall: {slot_hits}/{slot_total} = {slot_recall:.1%}")
    print(f"combined_score: {combined:.1%}")
    print(f"failures: {len(failures)}")

    if verbose and failures:
        print()
        for failure in failures:
            print(f"[{failure['index']}] {failure['prompt']}")
            print(f"  verb: expected {failure['expected_verb']!r}, got {failure['actual_verb']!r}")
            print(f"  flags: expected {failure['expected_flags']}, got {failure['actual_flags']}")
            print(f"  missing_slots: {failure['missing_slots']}")
            print(f"  notes: {failure['notes']}")

    return 0 if not failures else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true", help="print failed cases")
    args = parser.parse_args()
    return run_benchmark(verbose=args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
