# prosecode-prompt-compiler

Turns a messy prompt into a clean instruction before the agent answers.

*Part of the Prosecode family — a set of tools for writing, verifying, and transferring structured reasoning.*

It maps natural-language requests into a small verb-and-slot scaffold, flags missing information and contradictions, and lets the agent generate from the structured form rather than the raw words. The user never sees the scaffold. They just get a better-targeted response.

## What it does

Most prompts are a mix of intent, context, constraints, and noise. The compiler reads the prompt once and produces a compact intent record: which of seven verbs the user is asking for, which slots are filled, which are missing, and whether the constraints conflict.

The agent then has two things instead of one — the original prompt, and a clear statement of what was actually being asked. It can ask one targeted clarifying question instead of guessing, or proceed with the right posture if the intent is already clear.

## Example

**Raw prompt:**

> "can you help me figure out why the checkout is breaking? users say orders go through but never appear in the admin panel. also if you could rewrite the error message that would be great"

**Compiled intent:**

```
verb: analyze
target: checkout flow — order submission to admin panel propagation
symptoms: orders submit successfully, do not appear in admin
secondary-verb: transform
secondary-target: error message
contradiction: none
missing: none
posture: investigative; user has not yet shared logs or code
```

The agent now knows it has two requests (analyze, then rewrite), what the symptom signature is, and that it should ask for logs before guessing.

## Built by Liminate

Liminate is a prose-as-syntax language where plain English sentences execute directly. These five repos form a system for writing, verifying, and transferring structured reasoning.

| | Repo | What it does |
|---|---|---|
| | [liminate](https://github.com/rmichaelthomas/liminate) | The language and interpreter. Bounded vocabulary, deterministic execution, domain packs. |
| | [liminate-session-contracts](https://github.com/rmichaelthomas/liminate-session-contracts) | Tracks verified sources, inferred claims, locked decisions, and user corrections as executable `.limn` contracts. |
| **← this repo** | [**prosecode-prompt-compiler**](https://github.com/rmichaelthomas/prosecode-prompt-compiler) | **Compiles user prompts into structured intent before the agent responds. Seven verbs, twenty-four slots.** |
| | [prosecode-context-pager](https://github.com/rmichaelthomas/prosecode-context-pager) | Scores conversation history against current intent. Decides what to keep, summarize, or drop. |
| | [prosecode-handoff-packet](https://github.com/rmichaelthomas/prosecode-handoff-packet) | Packages a working session for another agent to continue — preserving what was verified and what wasn't. |

→ [liminate.dev](https://liminate.dev)

## Install

This skill follows the [agentskills.io](https://agentskills.io) SKILL.md standard. Any compliant agent can load it.

```bash
# Claude Code — all projects
git clone https://github.com/rmichaelthomas/prosecode-prompt-compiler.git ~/.claude/skills/prosecode-prompt-compiler

# Claude Code — one project
git clone https://github.com/rmichaelthomas/prosecode-prompt-compiler.git .claude/skills/prosecode-prompt-compiler

# Codex CLI
git clone https://github.com/rmichaelthomas/prosecode-prompt-compiler.git ~/.codex/skills/prosecode-prompt-compiler

# Gemini CLI
git clone https://github.com/rmichaelthomas/prosecode-prompt-compiler.git ~/.gemini/skills/prosecode-prompt-compiler

# Any SKILL.md-compatible agent
git clone https://github.com/rmichaelthomas/prosecode-prompt-compiler.git .agents/skills/prosecode-prompt-compiler
```

Before installing, run:

```bash
python3 scripts/install-check.py
```

The skill uses only portable Agent Skills frontmatter fields: `name`, `description`, `license`, and `metadata`.

## How it works

### Intent verbs

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

Compounds (`analyze` + `transform` in the example above) are first-class — the IR carries a `secondary-verb` alongside the primary one when both are clearly present.

### Compiler passes

A prompt flows through a small sequence of passes:

1. **Phrase markers** — bounded lowercase token matching against `references/phrase-markers.json` to detect verb cues, slot fillers, and posture signals.
2. **Slot filling** — populate the verb's required and optional slots from matched phrases.
3. **Contradiction detection** — check `references/contradiction-rules.json` for incompatible constraint pairs.
4. **Gap detection** — flag required slots that no phrase filled.
5. **Posture calibration** — set the response posture (investigative, directive, collaborative) from contextual cues.

### Validate and benchmark

```bash
python3 scripts/validate-skill.py        # frontmatter + JSON + table consistency
python3 scripts/benchmark-prompts.py --verbose
```

Two benchmark suites ship in `assets/`:

- `test-prompts.json` — canonical coverage for the seven verbs, compounds, contradictions, and pass-through prompts.
- `adversarial-test-prompts.json` — messy human prompts with uncertainty, typos, vague asks, false-positive substring traps, high-stakes contexts, and reversed priorities.

The benchmark is a reference-table smoke test, not a live model evaluation. It reports verb classification accuracy, contradiction and human-flag recall, expected slot-key recall, and required-gap recall.

### Provenance

The compiler adapts patterns from three earlier codebases:

- **Liminate** — bounded verb-slot vocabulary and narrow reorderer acceptance rules.
- **Loom MVP** — lowercase bounded phrase matching and contradiction detection.
- **Narratia MVP** — fallback scaffolding for vague input.

See [`references/DESIGN_PROVENANCE.md`](references/DESIGN_PROVENANCE.md) for the full source map.

## License

MIT
