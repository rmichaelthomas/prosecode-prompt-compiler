# Handoff Packets

A handoff packet is Intent IR prepared for another agent, skill, or tool. This is a future protocol surface, not required runtime behavior.

## Minimal Packet

```json
{
  "schema": "prosecode.intent.v0",
  "verb": "fix",
  "slots": {
    "target": "React component",
    "symptoms": "not loading with empty data"
  },
  "gaps": [],
  "amber_flags": [],
  "human_context": ["UNCERTAIN_USER"],
  "assumptions": [],
  "confidence": "medium"
}
```

## Rules

- Keep packets small.
- Include only task-relevant context.
- Do not include private conversation history unless necessary.
- Handoff packets should reduce reinterpretation, not replace judgment.
