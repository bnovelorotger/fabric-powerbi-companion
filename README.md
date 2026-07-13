# Fabric Power BI Companion

Agentic-first companion for Microsoft Fabric and Power BI projects, with TMDL-first workflows, semantic-model inspection, governed dictionaries, and safe public/private repo separation.

This repository is the shareable layer of the workflow. It is designed to be cloned by another engineer without inheriting private workspaces, client projects, auth caches, or local machine paths.

## At a glance

```text
Fabric / Power BI / TMDL
            |
            v
    Inspect and document
            |
            v
   Govern dictionary context
            |
            v
 Bootstrap safe semantic work
            |
            v
Keep public core separate from private workspace
```

## What it does

- Treats the agent as the primary interface for modeling, governance, and project intake.
- Helps inspect Power BI Desktop, Fabric, and TMDL-based semantic models.
- Provides reusable Codex skills for modeling, governance, and project intake.
- Ships a governed starter dictionary plus a demo project for safe offline validation.
- Encourages a clean split between a public reusable core and a private operational workspace.

## Agentic-first design

```text
Primary interface: agent + packaged skills
Secondary interface: CLI scripts and local docs
Source of truth: governed dictionary + technical catalog
Fallback mode: offline TMDL-first when live tools are unavailable
Safety boundary: public core stays separate from private workspace
```

This repository is designed so that an agent can:

- start from a business request instead of a manual checklist
- inspect local or live model state before proposing changes
- use governed context before inventing semantic definitions
- degrade safely to offline TMDL workflows when live Fabric or PBIX access is unavailable
- keep private operational assets out of the public repo by default

## Typical workflow

```text
1. Clone the public core
2. Install skills and dependencies
3. Validate environment
4. Start from `/comensemos` or the packaged skills
5. Work from TMDL or connect to live PBIX / Fabric
6. Compare model state against the dictionary
7. Sync governed metadata safely
8. Keep private client/workspace artifacts outside the public repo
```

## Public vs private

| Public core | Private workspace |
| --- | --- |
| Reusable scripts | Real Fabric exports |
| Packaged skills | Client projects |
| Starter dictionary | Business-specific rules |
| Demo TMDL and docs | Auth state and caches |
| Safe publication tooling | Sensitive operational data |

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

If you plan to use `executive-report-builder` for HTML/PDF exports, install the bundled browser once:

```powershell
python -m playwright install chromium
```

3. Install the packaged skills:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_skills.ps1
```

4. Validate the local environment:

```powershell
python .\scripts\workflow_cli.py validate-environment
```

5. Use the agent-first entrypoint:

- Start with `/comensemos` for project intake and routing.
- Use `BI_ENGINEER` for technical model work.
- Use `BI_GOVERNANCE` after technical changes or model sync.

6. Run the demo workflow:

```powershell
python .\scripts\workflow_cli.py validate-brief .\projects\demo-enrollment-sandbox\brief.yaml
python .\scripts\workflow_cli.py build-semantic-spec .\projects\demo-enrollment-sandbox\brief.yaml .\projects\demo-enrollment-sandbox\semantic_spec.yaml
python .\scripts\workflow_cli.py snapshot-from-tmdl .\projects\demo-enrollment-sandbox\artifacts\pbix_snapshot_tmdl .\projects\demo-enrollment-sandbox\artifacts\model_snapshot.json
python .\scripts\workflow_cli.py sync-dictionary .\projects\demo-enrollment-sandbox\artifacts\model_snapshot.json .\dictionary demo_enrollment_sandbox_model --domain DemoEnrollment --owner analytics_team
```

7. Run the local publication bootstrap:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_public_repo.ps1
```

8. Create the empty GitHub repository manually and follow [docs/github-bootstrap.md](docs/github-bootstrap.md).

## Supported workflow modes

- Agentic-first: preferred path through packaged skills and governed context
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
- See [CHANGELOG.md](CHANGELOG.md) for release history and compatibility notes.
- Keep private domain packs, real Fabric exports, and client projects in a separate private repository layered on top of this core.
- The repo is intentionally agentic-first: the packaged skills are the primary UX, and the CLI is the supporting execution layer.
- Use [docs/agentic-first.md](docs/agentic-first.md) for the design principles behind that choice.
- Use [docs/runbook.md](docs/runbook.md) for operational workarounds and known v1 limitations.
- Use [docs/github-bootstrap.md](docs/github-bootstrap.md) for the first safe publication flow.
- Before any first public push, run:

```powershell
python .\scripts\workflow_cli.py audit-public-repo
```

## License

MIT. See [LICENSE](LICENSE).
