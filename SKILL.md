---
name: prompt-reformatter
description: >
  Classify and restructure user prompts using a bounded verb-and-slot
  vocabulary before generating a response. Activates on every user prompt
  invisibly. The agent decomposes natural language into one of seven intent
  verbs (explain, create, transform, analyze, decide, plan, fix), fills
  named slots from the prompt content, flags missing required information
  and contradictory constraints, then generates from the structured scaffold
  instead of the raw input. Use on all conversational prompts. Do not use
  on system messages, tool outputs, or automated pipeline inputs.
license: MIT
metadata:
  author: rmichaelthomas
  version: "0.1.0"
  provenance: "Liminate bounded-vocabulary architecture + Narratia meaning-ordering + Loom contradiction-detection"
---

# Prompt Reformatter

## How This Skill Works

This skill operates invisibly before the agent responds. On every eligible user prompt, the agent classifies intent against the verb table, fills slots from the prompt content, checks for missing required slots, checks for contradictions between slot values, produces an internal scaffold, and generates from that scaffold rather than from the raw prompt alone. The user sees only the final response, not the reformatting.

## Intent Verbs

| Verb | User wants to... | Required slots |
|---|---|---|
| `explain` | Understand something. Output serves the user's comprehension. | `target` |
| `create` | Have an artifact produced. Output serves an external purpose. | `artifact` |
| `transform` | Have existing material changed into a different form. | `source`, `target-form` |
| `analyze` | Have something examined and findings reported. | `target` |
| `decide` | Get help choosing between options. | `options` |
| `plan` | Get a strategy or approach designed. | `goal` |
| `fix` | Get something corrected or debugged. | `target` |

For full slot definitions with phrase markers and type constraints, see [verb-signatures.json](references/verb-signatures.json) and [phrase-markers.json](references/phrase-markers.json).

## Slot Filling

Each slot has phrase markers: natural-language patterns that signal the slot is being filled. The agent matches the user's prompt against these markers to identify which information fills which slot. Markers follow bounded-phrase-set matching: lowercase the prompt, then check whether any known marker phrase appears as a substring. When a required slot has no match, the agent either infers a reasonable default from nearby prompt content or asks one focused clarifying question.

## Reorderer Rules

1. **Verb-first** - Explicit intent word present -> pass through, fill slots from surrounding phrases.
2. **Target-first, verb implicit** - Identify verb from context, canonicalize. Example: "Quantum computing - what is it?" -> explain, target = quantum computing.
3. **Question form** - Map question word to verb: "what is" -> explain, "should I" -> decide, "how do I" -> plan or fix depending on slot content.
4. **Compound intent** - Split into primary and secondary. Scaffold primary first, note secondary as follow-up. Example: "Explain React hooks and write me an example component" -> primary explain, secondary create.
5. **Missing required slot** - Flag gap, note what's needed. Analogous to parser error messages such as "I expected a target after 'filter'."
6. **Contradictory slots** - Flag as amber. Surface the tension without guessing. See [contradiction-rules.json](references/contradiction-rules.json). Example: "brief comprehensive report" -> BREVITY_DEPTH_TENSION.
7. **Slot values imply different verb** - Reclassify. Example: "Explain what's wrong with my code" -> apparent verb explain, but symptoms slot filled -> reclassify as fix or analyze.

## Scaffold Output

The internal scaffold contains the identified verb, filled slots with extracted values, empty optional slots with defaults or omissions, gap flags for missing required slots, amber flags for contradictions, and assumptions for inferred slot values with reasoning. The scaffold is never shown to the user.

When input is too vague to decompose, use the fallback scaffold pattern: choose the nearest eligible verb, preserve the user's original phrasing as the broad target or goal, apply minimal defaults, and proceed only if doing so is more helpful than asking a clarifying question.

## When NOT to Apply

Do not apply this skill to greetings, meta-questions about the agent itself, continuation prompts such as "go on" or "keep going", tool-output processing, system-level instructions, or automated pipeline inputs. These pass through without reformatting.
