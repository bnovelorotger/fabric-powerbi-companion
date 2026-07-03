# Fabric Power BI Companion

Codex-assisted companion for Microsoft Fabric and Power BI projects, with TMDL-first workflows, semantic-model inspection, governed dictionaries, and safe public/private repo separation.

This repository is the shareable layer of the workflow. It is designed to be cloned by another engineer without inheriting private workspaces, client projects, auth caches, or local machine paths.

## What is included

- Reusable model-factory scripts under `scripts/model_factory/`
- Packaged Codex skills under `skills/`
- A starter governed dictionary under `dictionary/`
- A sample technical catalog under `catalog/`
- A sanitized demo project under `projects/demo-enrollment-sandbox/`
- Setup, connection, and publication docs under `docs/`

## What is intentionally excluded

- Real Fabric workspace exports
- Real tenant, workspace, or semantic-model names
- Local auth state
- Private project histories
- Client-specific dictionaries and business rules
- Large temporary folders and one-off repair scripts

## Quickstart

1. Install Python 3.10+.
2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Install the packaged skills:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_skills.ps1
```

4. Validate the local environment:

```powershell
python .\scripts\workflow_cli.py validate-environment
```

5. Run the demo workflow:

```powershell
python .\scripts\workflow_cli.py validate-brief .\projects\demo-enrollment-sandbox\brief.yaml
python .\scripts\workflow_cli.py build-semantic-spec .\projects\demo-enrollment-sandbox\brief.yaml .\projects\demo-enrollment-sandbox\semantic_spec.yaml
python .\scripts\workflow_cli.py snapshot-from-tmdl .\projects\demo-enrollment-sandbox\artifacts\pbix_snapshot_tmdl .\projects\demo-enrollment-sandbox\artifacts\model_snapshot.json
python .\scripts\workflow_cli.py sync-dictionary .\projects\demo-enrollment-sandbox\artifacts\model_snapshot.json .\dictionary demo_enrollment_sandbox_model --domain DemoEnrollment --owner analytics_team
```

6. Run the local publication bootstrap:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_public_repo.ps1
```

7. Create the empty GitHub repository manually and follow [docs/github-bootstrap.md](docs/github-bootstrap.md).

## Supported workflow modes

- Offline / TMDL-first: fully supported from this repository alone
- Power BI Desktop live inspection: supported when the user has Power BI Desktop open and Codex Power BI MCP tooling available
- Fabric live inspection: supported when the user has Fabric access and Codex Power BI MCP tooling available

## Main entry points

- `python .\scripts\workflow_cli.py validate-environment`
- `python .\scripts\workflow_cli.py bootstrap-project <project-name>`
- `python .\scripts\workflow_cli.py validate-brief <brief-path>`
- `python .\scripts\workflow_cli.py build-semantic-spec <brief-path> <output-path>`
- `python .\scripts\workflow_cli.py detect-pbi`
- `python .\scripts\workflow_cli.py connect-fabric --config .\config\workflow.example.yaml`
- `python .\scripts\workflow_cli.py snapshot-from-tmdl <tmdl-folder> <snapshot-path>`
- `python .\scripts\workflow_cli.py sync-dictionary <snapshot-path> <dictionary-dir> <model-name>`
- `python .\scripts\workflow_cli.py audit-public-repo`
- `powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_public_repo.ps1`

## Repository layout

```text
analytics_ai_core/
|-- catalog/
|-- config/
|-- dictionary/
|-- docs/
|-- projects/
|-- scripts/
`-- skills/
```

## Notes

- This repo is the public core, not the private workspace.
- Keep private domain packs, real Fabric exports, and client projects in a separate private repository layered on top of this core.
- Use [docs/runbook.md](docs/runbook.md) for operational workarounds and known v1 limitations.
- Use [docs/github-bootstrap.md](docs/github-bootstrap.md) for the first safe publication flow.
- Before any first public push, run:

```powershell
python .\scripts\workflow_cli.py audit-public-repo
```

## License

MIT. See [LICENSE](LICENSE).
