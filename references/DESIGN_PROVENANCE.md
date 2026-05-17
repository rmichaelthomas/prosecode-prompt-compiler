# Design Provenance

This skill adapts four existing structural patterns into a portable Agent Skills package. It does not add a runtime parser or tool hook; it gives the agent an instruction-only method for internally canonicalizing prompts before response generation.

## Source Pattern Map

| Skill decision | Source | Hash | Adaptation |
|---|---|---:|---|
| Verb-slot architecture | `liminate/vocabulary.py` `VERB_SIGNATURES` + `PackVerbSlot` | `e002482` | Seven prompt-intent verbs each declare required and optional named slots with type constraints. |
| Slot-filling dispatch | `liminate/parser.py` pack verb parsing | `a8a3f20` | Each verb owns its own slots; required gaps are flagged with narrow, role-specific messages. |
| Reorderer acceptance table | `liminate/reorderer.py` `reorder()` | `04c55ef` | Natural-language prompt forms are accepted only through a compact table: verb-first, target-first, question form, compound intent, missing slot, contradiction, or reclassification. |
| Amber outcome model | `liminate/parser.py` `_contains_mixed_precedence()` | `a8a3f20` | Tensions do not silently fail. The agent flags them as amber and surfaces the tradeoff without pretending it disappeared. |
| Phrase-set matching | `loom-mvp/server/rules.js` `hasAny()` | `527450e` | Slot markers and contradiction rules use lowercase substring matching against bounded phrase lists. |
| Contradiction detection | `loom-mvp/server/rules.js` `runGrantFit()` | `527450e` | Known value tensions compare marker set A against marker set B, then emit named flags and reasons. |
| Post-generation validation | `loom-mvp/server/rules.js` `runIntegrity()` | `527450e` | The scaffold can be checked after generation to ensure the answer did not contradict the original constraints. |
| Fallback scaffolding | `narratia-mvp/utils.py` `naive_outline()` | `4425e83` | When prompt content is vague, impose a minimal default scaffold while preserving the user's original phrasing. |
| Two-tier architecture | `narratia-mvp/utils.py` `naive_*` / `llm_*_safe` | `4425e83` | Prefer deterministic, bounded heuristics first; use broader reasoning only after the scaffold exists. |

## Architectural Reasoning

Liminate contributes the core idea that language can be made safer by constraining it to verbs with explicit slots. This skill uses the same shape, but the verbs describe user intent rather than program operations.

Loom contributes the bounded phrase-set matcher. The skill keeps matching deliberately simple: lowercase input and check for known phrases. This keeps the behavior portable across agents and avoids relying on a specific parser implementation.

Loom also contributes the contradiction detector. The skill uses named amber flags instead of hard failures because prompt constraints often contain productive tension, such as "brief but comprehensive." The agent should preserve the tension and make a visible tradeoff in the response.

Narratia contributes fallback scaffolding. When the input is too vague to decompose cleanly, the skill still creates a minimal scaffold from the user's own wording, unless a required slot is too important to infer.

The final package is instruction-only. `SKILL.md` describes the operational method, `references/` stores the bounded tables, `assets/test-prompts.json` provides pressure cases, and `scripts/validate-skill.py` validates the package during development.
