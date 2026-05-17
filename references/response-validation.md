# Response Validation

After drafting a response, the agent may silently check it against Intent IR.

## Minimal Rubric

- Did the response satisfy the primary `verb`?
- Did it address filled required slots?
- If `gaps` were present, did it ask one focused clarifying question or state a safe assumption?
- If `amber_flags` were present, did it preserve the tradeoff?
- If `human_context` was present, did the response posture match it?
- Did the answer avoid exposing the scaffold unless asked?

This is a quality check, not extra output.
