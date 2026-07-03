# Skills

This repository packages the workflow skills directly under `skills/`.

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
