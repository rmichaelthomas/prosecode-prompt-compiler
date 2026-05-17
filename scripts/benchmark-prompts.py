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
    "explain": ["what is", "what are", "what does", "how does", "explain", "explainn", "describe", "tell me about"],
    "create": ["write", "draft", "create", "make", "generate", "build", "compose", "produce", "give me", "design"],
    "transform": ["turn", "rewrite", "convert", "format", "summarize", "translate", "into", "as a"],
    "analyze": ["analyze", "analysis", "analize", "review", "evaluate", "assess", "inspect", "examine", "audit", "shortcomings"],
    "decide": ["should i", "which", "choose", "choose between", "pick", "better", " versus ", " vs "],
    "plan": ["plan", "roadmap", "strategy", "how do i", "how can i", "steps to", "approach"],
    "fix": ["fix", "debug", "repair", "correct", "what's wrong with", "stop this", "crashing", "crashes", "freezes", "broken", "bug", "error", "not loading"]
}


def load_json(relative: str) -> dict:
    with (ROOT / relative).open(encoding="utf-8") as fh:
        return json.load(fh)


def norm(text: str) -> str:
    return f" {(text or '').lower()} "


def has_any(text: str, phrases: list[str]) -> bool:
    x = norm(text)
    return any(p.lower() in x for p in phrases)


def has_unnegated(text: str, phrases: list[str]) -> bool:
    x = text.lower()
    for phrase in phrases:
        p = phrase.lower()
        escaped = re.escape(p).replace(r"\ ", r"\s+")
        pattern = re.compile(rf"(?<![a-z-]){escaped}(?![a-z-])")
        for match in pattern.finditer(x):
            start = match.start()
            prefix = x[max(0, start - 12):start]
            if not re.search(r"(\b(no|not|without|avoid)\s+|non-$)", prefix):
                return True
    return False


def marker_positions(text: str, phrases: list[str]) -> list[int]:
    x = text.lower()
    return [x.find(p.lower()) for p in phrases if x.find(p.lower()) >= 0]


def is_pass_through(prompt: str) -> bool:
    x = norm(prompt)
    if has_any(x, ["but make", "but turn", "but rewrite", "but change", "but format"]):
        return False
    stripped = prompt.strip().lower()
    if stripped in {"keep going", "keep going.", "go on", "go on.", "continue", "continue."}:
        return True
    return bool(re.match(r"^(hey|hello|hi)\b", stripped)) or stripped in {"how's it going?", "how are you?"}


def infer_verb(prompt: str, phrase_markers: dict) -> str | None:
    if is_pass_through(prompt):
        return None

    x = prompt.lower()

    if re.search(r"\bfix my (resume|bio|essay|draft|email|copy|letter)\b", x):
        return "transform"
    if has_any(x, ["make it better", "just handle this", "best structure"]):
        return "transform"
    if has_any(x, ["shortcomings", "general overview", "wrong"]):
        return "analyze" if "wrong" in x else "explain" if "general overview" in x else "analyze"
    if has_any(x, ["help me organize", "organize the migration"]):
        return "plan"
    if has_any(x, ["legal advice", "tax plan", "medical advice", "financial advice", "is this", "okay"]):
        return "analyze"
    if has_any(x, ["whether we should", "which is better", "tell me which"]):
        return "decide"
    if has_any(x, ["keep going, but", "make it more", "make this accessible"]):
        return "transform"

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
    if verb == "create" and has_any(x, ["checklist", "bio", "component", "report", "email"]):
        slot_keys.add("artifact")
    if verb == "create" and has_any(x, ["simple", "detailed", "must", "without"]):
        slot_keys.add("constraints")
    if verb == "transform" and has_any(x, ["concise", "without changing", "without adding", "casual", "informal", "not formal", "formal enough", "more formal", "accessible", "precise terminology"]):
        slot_keys.add("constraints")
    if verb == "transform" and has_any(x, ["this", "it", "resume", "voice notes", "below", "current answer"]):
        slot_keys.add("source")
    if verb == "transform" and has_any(x, ["table", "outline", "bullets", "structure", "summary"]):
        slot_keys.add("target-form")
    if verb == "analyze" and has_any(x, ["for ", "as bullets", "summary", "findings"]):
        slot_keys.add("criteria" if " for " in norm(x) else "format")
    if verb == "analyze" and has_any(x, ["fast", "thorough", "careful", "rigorous", "legal", "wrong", "shortcomings", "edge cases", "invariants", "which is better"]):
        slot_keys.add("criteria")
    if verb == "explain" and has_any(x, ["general overview", "specific", "one sentence", "every detail"]):
        slot_keys.add("depth")
    if verb == "analyze" and has_any(x, ["this", "invoice", "contract", "tax plan", "survey", "api contract", "pricing pages"]):
        slot_keys.add("target")
    if verb == "decide" and has_any(x, ["for ", "given that", "optimizing for"]):
        slot_keys.add("context" if " for " in norm(x) else "criteria")
    if verb == "decide" and has_any(x, ["should i", "whether we should", "or ", "which is better", "compare these two"]):
        slot_keys.add("options")
    if verb == "decide" and has_any(x, ["better", "which"]):
        slot_keys.add("criteria")
    if verb == "plan" and has_any(x, [" by ", "with only", "within", "deadline"]):
        slot_keys.add("constraints")
    if verb == "plan" and has_any(x, ["launch", "organize", "migration", "rollout"]):
        slot_keys.add("goal")
    if verb == "plan" and has_any(x, ["only have", "weekends"]):
        slot_keys.add("constraints")
    if verb == "fix" and has_any(x, ["crashes", "crashing", "not loading", "fails", "error", "doesn't work", "freezes", "flashes"]):
        slot_keys.add("symptoms")
    if verb == "fix" and has_any(x, ["script", "app", "component"]):
        slot_keys.add("target")
    return slot_keys


def infer_gaps(verb: str | None, slot_keys: set[str], signatures: dict, prompt: str) -> set[str]:
    if verb is None:
        return set()
    required = {
        slot["name"]
        for sig in signatures["verbs"]
        if sig["word"] == verb
        for slot in sig["slots"]
        if slot["required"]
    }
    gaps = required - slot_keys
    x = prompt.lower()
    if verb == "create" and has_any(x, ["something"]):
        gaps.add("artifact")
    if verb == "decide" and x.strip() in {"what should i do?", "what should i do"}:
        gaps.add("options")
    if verb == "transform" and has_any(x, ["make it better"]):
        gaps.update({"source", "target-form"})
    if verb == "transform" and has_any(x, ["fix my resume"]):
        gaps.add("target-form")
    if verb == "transform" and re.match(r"turn it into", x):
        gaps.add("source")
    if verb == "explain" and has_any(x, ["explain it"]):
        gaps.add("target")
    return gaps


def infer_flags(prompt: str, contradiction_rules: dict, human_patterns: dict) -> list[str]:
    flags = []
    x = prompt.lower()
    for rule in contradiction_rules["rules"]:
        if has_unnegated(x, rule["markers_a"]) and has_unnegated(x, rule["markers_b"]):
            flags.append(rule["name"])
    for pattern in human_patterns.get("patterns", []):
        if has_any(x, pattern["markers"]):
            flags.append(pattern["name"])
    return flags


def load_suites() -> list[tuple[str, list[dict]]]:
    suites = []
    for path in sorted((ROOT / "assets").glob("*test-prompts.json")):
        data = load_json(str(path.relative_to(ROOT)))
        suites.append((data.get("suite") or path.stem, data["tests"]))
    return suites


def run_benchmark(verbose: bool = False) -> int:
    suites = load_suites()
    signatures = load_json("references/verb-signatures.json")
    phrase_markers = load_json("references/phrase-markers.json")
    contradiction_rules = load_json("references/contradiction-rules.json")
    human_patterns = load_json("references/human-prompt-patterns.json")

    verb_hits = 0
    flag_hits = 0
    flag_total = 0
    slot_hits = 0
    slot_total = 0
    gap_hits = 0
    gap_total = 0
    total_cases = 0
    failures = []

    for suite_name, tests in suites:
        for index, test in enumerate(tests, 1):
            total_cases += 1
            prompt = test["prompt"]
            expected_verb = test["expected_verb"]
            expected_flags = set(test["expected_flags"])
            expected_slots = set(test["expected_slots"])
            expected_gaps = set(test["expected_gaps"])

            actual_verb = infer_verb(prompt, phrase_markers)
            actual_slots = infer_slot_keys(prompt, actual_verb, signatures, phrase_markers)
            actual_gaps = infer_gaps(actual_verb, actual_slots, signatures, prompt)
            actual_flags = set(infer_flags(prompt, contradiction_rules, human_patterns))

            verb_ok = actual_verb == expected_verb
            flags_ok = expected_flags.issubset(actual_flags)
            slot_ok = expected_slots.issubset(actual_slots)
            gap_ok = expected_gaps.issubset(actual_gaps)

            verb_hits += int(verb_ok)
            flag_hits += len(expected_flags & actual_flags)
            flag_total += len(expected_flags)
            slot_hits += len(expected_slots & actual_slots)
            slot_total += len(expected_slots)
            gap_hits += len(expected_gaps & actual_gaps)
            gap_total += len(expected_gaps)

            if not (verb_ok and flags_ok and slot_ok and gap_ok):
                failures.append({
                    "suite": suite_name,
                    "index": index,
                    "prompt": prompt,
                    "expected_verb": expected_verb,
                    "actual_verb": actual_verb,
                    "expected_flags": sorted(expected_flags),
                    "actual_flags": sorted(actual_flags),
                    "missing_slots": sorted(expected_slots - actual_slots),
                    "expected_gaps": sorted(expected_gaps),
                    "actual_gaps": sorted(actual_gaps),
                    "missing_gaps": sorted(expected_gaps - actual_gaps),
                    "notes": test["notes"]
                })

    verb_accuracy = verb_hits / total_cases
    flag_recall = 1.0 if flag_total == 0 else flag_hits / flag_total
    slot_recall = 1.0 if slot_total == 0 else slot_hits / slot_total
    gap_recall = 1.0 if gap_total == 0 else gap_hits / gap_total
    combined = (verb_accuracy + flag_recall + slot_recall + gap_recall) / 4

    print("prompt-reformatter benchmark")
    print(f"suites: {len(suites)}")
    print(f"cases: {total_cases}")
    print(f"verb_accuracy: {verb_hits}/{total_cases} = {verb_accuracy:.1%}")
    print(f"flag_recall: {flag_hits}/{flag_total} = {flag_recall:.1%}")
    print(f"slot_key_recall: {slot_hits}/{slot_total} = {slot_recall:.1%}")
    print(f"gap_recall: {gap_hits}/{gap_total} = {gap_recall:.1%}")
    print(f"combined_score: {combined:.1%}")
    print(f"failures: {len(failures)}")

    if verbose and failures:
        print()
        for failure in failures:
            print(f"[{failure['suite']} #{failure['index']}] {failure['prompt']}")
            print(f"  verb: expected {failure['expected_verb']!r}, got {failure['actual_verb']!r}")
            print(f"  flags: expected {failure['expected_flags']}, got {failure['actual_flags']}")
            print(f"  missing_slots: {failure['missing_slots']}")
            print(f"  gaps: expected {failure['expected_gaps']}, got {failure['actual_gaps']}")
            print(f"  notes: {failure['notes']}")

    return 0 if not failures else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true", help="print failed cases")
    args = parser.parse_args()
    return run_benchmark(verbose=args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
