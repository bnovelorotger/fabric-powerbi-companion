# CLAUDE.md - Analytics AI Core

This repository is the public core of a Codex workflow for Fabric, Power BI semantic models, and governed dictionaries.

## Mission

- Help users bootstrap new semantic-model projects safely.
- Prefer governed dictionary context before changing a model.
- Support offline TMDL workflows first.
- Support live Fabric and Power BI Desktop inspection when MCP tooling is available.

## Rules

- Do not assume private workspace names, tenants, or business rules.
- Do not commit secrets, auth state, or local caches.
- Treat `catalog/` as technical evidence and `dictionary/` as governed meaning.
- Keep demo content generic and sanitized.

## Suggested skill order

1. `/comensemos`
2. `BI_ENGINEER`
3. `BI_GOVERNANCE`

## Important folders

- `catalog/`: starter technical catalog
- `dictionary/`: governed reusable dictionary
- `projects/`: per-model working area
- `skills/`: packaged Codex skills
- `scripts/model_factory/`: reusable workflow scripts
