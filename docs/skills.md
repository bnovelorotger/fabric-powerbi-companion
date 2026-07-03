# Skills

This repository packages the workflow skills directly under `skills/`.

These skills are the primary interface of the repository. The project is intentionally agentic-first: the expected path is to start from the agent and use the CLI/scripts as supporting execution tools.

## Included skills

- `comensemos`
- `bi-engineer`
- `bi-governance`

## Install

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_skills.ps1
```

## Design notes

- Skills use relative references and do not depend on a specific Windows username.
- The public core stays generic by default.
- Private domain packs should live in a separate private repository.
- The skills are meant to be the first-class UX of the repo, not an optional extra over a script-only workflow.
