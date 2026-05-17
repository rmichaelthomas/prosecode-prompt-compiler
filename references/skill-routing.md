# Skill Routing

Intent IR can guide skill selection without relying only on fuzzy prompt matching.

## Routing Pattern

```text
verb=fix + target=code -> debugging or coding skill
verb=create + artifact=deck -> presentation skill
verb=analyze + target=spreadsheet -> spreadsheet skill
verb=transform + target-form=docx -> document skill
verb=plan + high-stakes context -> careful planning or domain-specific review
```

## Rules

- Treat routing as advisory unless the environment provides explicit routing tools.
- Prefer the most specific safe skill.
- Do not load heavy references unless the routed task needs them.
- Preserve the original Intent IR when handing work to another skill or agent.
