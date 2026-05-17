# prompt-reformatter

`prompt-reformatter` is a portable Agent Skill that helps an agent invisibly classify and restructure user prompts before answering. It maps natural language requests into a bounded verb-and-slot scaffold, checks for missing required information and contradictory constraints, then lets the agent generate from the scaffold rather than the raw prompt alone.

The user never sees the scaffold. They just get a clearer, better-targeted response.

The skill is intentionally token-conscious: `SKILL.md` stays compact, detailed tables live in references, and the internal scaffold is meant to be small enough to reduce wasted output rather than add overhead.

## Intent Verbs

The skill uses seven intent verbs:

| Verb | User wants to... | Required slots |
|---|---|---|
| `explain` | Understand something | `target` |
| `create` | Have an artifact produced | `artifact` |
| `transform` | Change existing material into another form | `source`, `target-form` |
| `analyze` | Have something examined and findings reported | `target` |
| `decide` | Choose between options | `options` |
| `plan` | Design a strategy or approach | `goal` |
| `fix` | Correct or debug something | `target` |

## Structure

```text
prompt-reformatter/
├── SKILL.md
├── references/
│   ├── verb-signatures.json
│   ├── phrase-markers.json
│   ├── contradiction-rules.json
│   ├── human-prompt-patterns.json
│   └── DESIGN_PROVENANCE.md
├── assets/
│   ├── test-prompts.json
│   ├── adversarial-test-prompts.json
│   └── live-eval-results.json
└── scripts/
    ├── validate-skill.py
    ├── benchmark-prompts.py
    └── install-check.py
```

## Provenance

This skill adapts patterns from three existing codebases:

- Liminate: bounded verb-slot vocabulary and narrow reorderer acceptance rules
- Loom MVP: lowercase bounded phrase matching and contradiction detection
- Narratia MVP: fallback scaffolding for vague input

See [references/DESIGN_PROVENANCE.md](references/DESIGN_PROVENANCE.md) for the full source map.

## Validation

Run the built-in validator:

```bash
python3 scripts/validate-skill.py
```

The validator checks:

- `SKILL.md` frontmatter portability
- JSON parseability
- verb and slot table consistency
- test prompt coverage
- expected counts for verbs, slots, test cases, and contradiction rules

## Benchmarking

Run the deterministic prompt benchmark:

```bash
python3 scripts/benchmark-prompts.py --verbose
```

This benchmark checks the bundled prompt cases against the bounded marker vocabulary, contradiction rules, gap detection, and human-context markers. It reports verb classification accuracy, contradiction and human flag recall, expected slot-key recall, and required-gap recall. It is a reference-table smoke test, not a live model evaluation.

Current suites:

- `assets/test-prompts.json`: canonical coverage for the seven intent verbs, compounds, contradictions, and pass-through prompts.
- `assets/adversarial-test-prompts.json`: messy human prompts with uncertainty, typos, vague asks, false-positive substring traps, high-stakes contexts, and reversed priorities.
- `assets/live-eval-results.json`: pre-install response-behavior review for ten messy prompts.

## Installation

Before installing, run:

```bash
python3 scripts/install-check.py
```

Copy the `prompt-reformatter` folder into a skills directory supported by your agent environment.

For Codex, that is commonly:

```text
~/.codex/skills/prompt-reformatter
```

For other tools, use the skill installation path documented by that tool. The skill intentionally uses only portable Agent Skills frontmatter fields: `name`, `description`, `license`, and `metadata`.

## License

MIT
