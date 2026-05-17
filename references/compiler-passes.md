# Compiler Passes

The skill treats prompt handling as a small compiler pipeline.

| Pass | Purpose |
|---|---|
| Marker pass | Detect bounded phrases and human-context signals. |
| Intent pass | Choose the primary verb. |
| Reorderer pass | Canonicalize target-first, question-form, and compound prompts. |
| Slot-fill pass | Extract or infer named slot values. |
| Gap pass | Identify missing required slots. |
| Amber pass | Preserve contradictions without flattening them. |
| Calibration pass | Adjust response posture for uncertainty, expertise, overwhelm, delegation, or high stakes. |
| Compaction pass | Keep Intent IR small. |
| Generation pass | Answer from the IR. |
| Validation pass | Check that the response honored the IR. |

These passes are conceptual. The skill does not require runtime code.
