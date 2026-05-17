# CHECKPOINT
## Prosecode Intent IR and Agent Protocol
### v1 - A Working Session on Intent Compilation, Liminate-Derived Agent Skills, and the Protocol Surface Beneath Human Prompts

**Status:** LOCKED
**Date:** May 17, 2026
**Author:** Rob Thomas / R. Michael Thomas (architect), Codex (analytical and implementation partner)
**Document type:** Checkpoint - captures a working session in which a universal Agent Skill originally named `prompt-reformatter` revealed a larger Prosecode pattern: user prompts can be compiled into a compact Intent IR using Liminate's bounded verb-slot architecture, then used for response generation, skill routing, prompt diffing, response validation, and possible cross-agent handoff. The session terminated in a decision to rename and reposition the skill as a Prosecode intent compiler, while logging the broader protocol idea for further ideation.
**Relationship to prior checkpoints:** Extends the Prosecode category work captured in `inscript_checkpoint_v1_prosecode_and_domain_strategy.md`, with one historical correction: Inscript is now Liminate. This checkpoint treats Inscript as the prior name and Liminate as the current language name. It does not alter any locked Liminate language decisions; it applies Liminate's architecture to an agent-skill and protocol surface.

---

## Part I - The Generative Question

### §1 - HOW WE GOT HERE

The session began as a practical build: create a portable Agent Skill called `prompt-reformatter`. The skill would classify and restructure user prompts before response generation using a bounded verb-and-slot vocabulary. The user would never see the restructuring; they would simply receive better responses.

The source patterns came from three codebases:

- **Liminate** - bounded vocabulary, verb signatures, slot filling, reorderer acceptance tables, UNKNOWN fallback, amber parse states.
- **Narratia** - fallback scaffolding for vague input.
- **Loom MVP** - bounded phrase matching and contradiction detection.

The skill was built, validated, benchmarked, hardened with adversarial human-prompt tests, and prepared for installation. During the final ideation pass, the working insight shifted: the skill was not merely reformatting prompts. It was compiling messy human language into an intermediate representation of intent.

That recognition moved the work from "prompt helper" into Prosecode territory.

### §2 - THE QUESTION UNDERNEATH THE QUESTION

The immediate question was whether to rename and expand the skill. The deeper question was whether an agent-facing Intent IR belongs under the Prosecode lineage.

The answer is yes.

Prosecode names a form of authoring in which human-readable prose retains operational continuity with behavior. Liminate demonstrates this at the language level: bounded verbs, named slots, canonical reorderings, and explicit amber states turn ordinary-ish prose into executable or inspectable behavior.

The intent compiler applies the same move at the agent boundary. It does not execute a user prompt as a Liminate program. Instead, it compiles a user's imperfect natural-language prompt into a compact, inspectable scaffold that guides agent behavior.

This is a Prosecode move because the human's prose remains legible while becoming operationally meaningful.

---

## Part II - What Was Built

### §3 - THE INITIAL SKILL

The original skill, `prompt-reformatter`, shipped with:

- `SKILL.md` - portable Agent Skills frontmatter and operating methodology.
- `references/verb-signatures.json` - seven intent verbs and their named slots.
- `references/phrase-markers.json` - bounded phrase sets for slot detection.
- `references/contradiction-rules.json` - amber tension rules.
- `references/human-prompt-patterns.json` - uncertainty, overwhelm, expertise, delegation, high-stakes, and imperfect-text markers.
- `assets/test-prompts.json` - canonical benchmark cases.
- `assets/adversarial-test-prompts.json` - messy human-prompt cases.
- `assets/live-eval-results.json` - pre-install behavior review.
- `scripts/validate-skill.py` - structural validation.
- `scripts/benchmark-prompts.py` - deterministic prompt benchmark.
- `scripts/install-check.py` - pre-install readiness check.
- `scripts/token-discipline-check.py` - internal token-discipline check.

The latest pre-rename verification state:

| Check | Result |
|---|---|
| Structural validation | Pass |
| Prompt benchmark | 56/56 cases, 100% combined |
| Install check | Pass |
| Token discipline check | Pass |

### §4 - THE LIMIT OF THE ORIGINAL NAME

`prompt-reformatter` became inaccurate.

The phrase suggests a cosmetic transformation of text. The actual architecture performs:

1. intent classification,
2. slot filling,
3. gap detection,
4. contradiction detection,
5. human-context calibration,
6. compact scaffold construction,
7. response generation from the scaffold,
8. optional validation against the scaffold.

This is not reformatting. It is compilation.

The name also underclaims the provenance. The structural power comes from Liminate and belongs under the Prosecode lineage. The renamed skill should make that relationship explicit without overloading the runtime instructions.

### §5 - DECISION: RENAME TO PROSECODE INTENT COMPILER

**Decision: Rename the skill from `prompt-reformatter` to `prosecode-intent-compiler`. LOCKED.**

The new name is chosen because:

1. **Prosecode** names the form paradigm: human-readable prose made operationally meaningful.
2. **Intent** names the semantic object being compiled.
3. **Compiler** names the actual mechanism: parse, reorder, fill, flag, validate.

`liminate-intent-compiler` was considered and remains technically accurate, but it places the emphasis on the source language rather than the broader category. `prosecode-intent-compiler` better captures the product-shaped skill while preserving Liminate provenance inside the references.

The skill should describe itself as:

> A Liminate-derived Prosecode skill that compiles user prompts into compact Intent IR before response generation.

---

## Part III - The Intent IR

### §6 - INTENT IR AS THE LOAD-BEARING IDEA

**Decision: The hidden scaffold is formalized as Intent IR. LOCKED.**

Intent IR is the compact intermediate representation created from a user's prompt before response generation. It is not shown to the user by default. It exists so the agent can reason from a stable semantic object rather than from raw prose alone.

Minimal v0 shape:

```json
{
  "schema": "prosecode.intent.v0",
  "verb": "explain | create | transform | analyze | decide | plan | fix",
  "slots": {},
  "gaps": [],
  "amber_flags": [],
  "human_context": [],
  "assumptions": [],
  "secondary_intents": [],
  "confidence": "low | medium | high"
}
```

The IR is intentionally small. It should preserve the information needed for good agent behavior without becoming a second prompt hidden inside the first.

### §7 - WHY THIS IS PROSECODE

Prompt engineering treats prompts as text to improve.

Intent compilation treats prompts as prose to parse into operational meaning.

That distinction is the Prosecode move. The human writes ordinary language. The system preserves the human-readable surface while deriving a bounded, inspectable behavioral representation underneath.

Liminate supplies the necessary architecture:

- bounded verbs,
- named slots,
- narrow acceptance rules,
- UNKNOWN fallback,
- amber states,
- canonical reorderings,
- explicit parse gaps.

Intent IR transposes that architecture from language execution into agent cognition.

### §8 - THE COMPILER PASSES

The skill's internal method is now understood as compiler passes:

| Pass | Purpose |
|---|---|
| Lexical marker pass | Detect bounded phrase markers and human-context signals. |
| Intent classification pass | Choose the primary verb. |
| Reorderer pass | Canonicalize target-first, question-form, and compound prompts. |
| Slot-fill pass | Extract or infer named slot values. |
| Gap pass | Identify missing required slots. |
| Amber pass | Preserve contradictions and tensions without flattening them. |
| Human calibration pass | Adjust response posture for uncertainty, expertise, overwhelm, delegation, or high stakes. |
| Scaffold compaction pass | Keep Intent IR small enough to reduce wasted generation. |
| Generation pass | Answer from the scaffold, not from raw prose alone. |
| Validation pass | Check whether the answer honored verb, slots, gaps, amber flags, and posture. |

---

## Part IV - Protocol Surface

### §9 - SKILL VS. PROTOCOL

**Decision: The renamed skill is a skill today; the protocol surface is logged for further ideation. LOCKED.**

A skill tells one agent how to think.

A protocol lets multiple agents, tools, skills, sessions, or products exchange interpreted intent.

The current build should not overclaim protocol status. It should include protocol-shaped references so the path is visible, but it should remain installable as a portable Agent Skill.

The protocol idea becomes real only if Intent IR is used outside the local response-generation loop: handoff, routing, storage, replay, diffing, validation, or cross-agent coordination.

### §10 - WHAT A BROADER PROTOCOL WOULD ENABLE

The logged protocol possibilities:

1. **Cross-agent handoff.** One agent can classify intent; another can execute; another can validate. All share the same Intent IR.
2. **Skill routing.** Skills can be selected by typed intent rather than fuzzy prompt matching.
3. **Prompt diffing.** Multi-turn changes can be tracked structurally: verb changed, slot changed, audience changed, amber flag added.
4. **Response validation.** The agent can check whether its answer satisfied the compiled intent.
5. **Replayable evaluations.** Prompt suites can be replayed through different agents or model versions and compared through the same IR.
6. **Tool-independent memory.** Long summaries can be supplemented by compact recurring intent shapes.
7. **Token discipline.** Waste can be reduced at the meaning layer by preventing wrong continuations, not merely by shortening answers.

These are logged as protocol directions, not implemented protocol guarantees.

### §11 - RELATIONSHIP TO PTAH

Ptah Protocol remains a sibling expression of the authorship-of-behavior thesis, not a child of Prosecode.

The Intent IR protocol surface is closer to Prosecode because it preserves operational continuity between prose and agent behavior. Ptah concerns authorship, attribution, lineage, and rights across media objects. The two may eventually meet: Intent IR could carry provenance fields, or Ptah records could point to Prosecode-derived intent packets. That integration is out of scope for this checkpoint.

---

## Part V - Implementation Direction

### §12 - THE TWO BUILDS

**Decision: Proceed with two builds. LOCKED.**

1. **Finish and rename the skill.** `prompt-reformatter` becomes `prosecode-intent-compiler`.
2. **Capture the larger idea in a checkpoint.** This document records the protocol insight so the skill rename does not silently decide the philosophy.

The checkpoint comes first because taxonomy should lead implementation. The repo follows.

### §13 - SKILL STRUCTURE AFTER RENAME

The renamed skill should keep `SKILL.md` concise and move expansion into references:

```text
prosecode-intent-compiler/
├── SKILL.md
├── README.md
├── checkpoints/
│   └── prosecode_checkpoint_v1_intent_ir_and_agent_protocol.md
├── references/
│   ├── intent-ir.md
│   ├── compiler-passes.md
│   ├── response-validation.md
│   ├── prompt-diffing.md
│   ├── skill-routing.md
│   ├── handoff-packets.md
│   ├── verb-signatures.json
│   ├── phrase-markers.json
│   ├── contradiction-rules.json
│   ├── human-prompt-patterns.json
│   └── DESIGN_PROVENANCE.md
├── assets/
└── scripts/
```

The new references should be short. They are navigational and conceptual, not a full public standard.

### §14 - NAMING RULES

The Agent Skill name and folder name must match:

```yaml
name: prosecode-intent-compiler
```

The GitHub repository should also be renamed:

```text
rmichaelthomas/prosecode-intent-compiler
```

The prior name `prompt-reformatter` remains historical and should appear in the checkpoint and README as the seed name, not as the current identity.

---

## WHAT IS LOCKED

This checkpoint locks:

- **Liminate is the current language name.** Inscript is historical context only in this checkpoint.
- **The skill is being renamed from `prompt-reformatter` to `prosecode-intent-compiler`.**
- **Intent IR is the correct name for the hidden scaffold.**
- **The skill remains an Agent Skill today, not a full protocol implementation.**
- **The broader protocol surface is logged as a Prosecode direction for future ideation.**
- **The two-build sequence is checkpoint first, repo rename/refactor second.**

This checkpoint does NOT lock:

- A public Prosecode protocol specification.
- A Ptah integration.
- A deployed `prosecode.org` site architecture.
- Any change to Liminate's language build chain.
- A claim that external agents already exchange Intent IR.

---

## WHAT IS LOGGED

This checkpoint logs:

- The phrase **"compiler front-end for human intention"** as the core explanatory frame.
- The schema name candidate **`prosecode.intent.v0`**.
- The distinction between local skill cognition and broader protocol exchange.
- Prompt diffing, response validation, skill routing, and handoff packets as protocol-adjacent future surfaces.
- Token discipline as a meaning-layer efficiency problem, not merely an output-length problem.

---

## OPEN QUESTIONS

| # | Question | Category | Related |
|---|---|---|---|
| PI-Q1 | Should `prosecode.intent.v0` become a public schema or remain internal to the skill until multiple tools consume it? | Protocol timing | §9, §10 |
| PI-Q2 | Should Intent IR include provenance fields now, or wait for a possible Ptah integration? | Protocol design | §11 |
| PI-Q3 | What is the smallest useful response-validation rubric that does not add token overhead? | Skill behavior | §8 |
| PI-Q4 | Should prompt diffing be implemented as a benchmark artifact, a reference-only idea, or a runtime behavior? | Evaluation | §10 |
| PI-Q5 | When `prosecode.org` eventually launches, does this skill belong under `/intent-ir`, `/agents`, or `/skills`? | Site architecture | Prosecode checkpoint v1 |
| PI-Q6 | Should the skill eventually emit Intent IR on request for debugging, or should it remain fully invisible except during tests? | UX / transparency | §6 |

---

## PROVENANCE NOTE

This checkpoint was produced from a working session on May 17, 2026 with the following inputs:

- The completed `prompt-reformatter` Agent Skill repository, including validation, benchmark, adversarial prompt suite, live eval notes, install check, and token discipline check.
- The Prosecode category and domain checkpoint: `inscript_checkpoint_v1_prosecode_and_domain_strategy.md`, read as historically naming Inscript before the rename to Liminate.
- Liminate source architecture as previously used in the skill build: `vocabulary.py`, `parser.py`, `reorderer.py`, and `lexer.py`.
- User correction: **Liminate is the new name of Inscript.**

### RESUME PROMPT

*We are resuming from the Prosecode Intent IR and Agent Protocol Checkpoint v1 (May 17, 2026). The checkpoint captures the recognition that the original `prompt-reformatter` Agent Skill is better understood as a Prosecode intent compiler: a Liminate-derived compiler front-end for human prompts that produces compact Intent IR before response generation.*

*Locked decisions: Liminate is the current language name; Inscript is historical. The skill is being renamed to `prosecode-intent-compiler`. Intent IR is the correct name for the hidden scaffold. The skill remains an Agent Skill today, while the broader protocol surface is logged for further ideation.*

*The next move is to refactor the repository and Agent Skill package to `prosecode-intent-compiler`, add short references for Intent IR, compiler passes, response validation, prompt diffing, skill routing, and handoff packets, then rerun validation, benchmarks, install checks, and token discipline checks before pushing the renamed repository.*

