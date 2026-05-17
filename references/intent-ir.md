# Intent IR

Intent IR is the compact intermediate representation produced from a user prompt before response generation. It is internal by default.

## v0 Shape

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

## Rules

- Keep the IR compact. It is a scaffold, not a hidden essay.
- Preserve the user's intent, not their exact phrasing, unless wording itself matters.
- Use `gaps` only for missing required slots.
- Use `amber_flags` for tensions that should influence the response.
- Use `human_context` for response posture signals, not labels of user ability.
- Show Intent IR only when the user explicitly asks for debugging or transparency.
