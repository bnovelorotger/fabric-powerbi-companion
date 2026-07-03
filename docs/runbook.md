# Runbook

This runbook captures the main operational workarounds and known limitations for `analytics_ai_core`.

## 1. `git` is not installed or not in `PATH`

Symptom:

- `git` commands fail
- `bootstrap_public_repo.ps1` reports that Git is not available

Likely cause:

- Git is not installed
- terminal was opened before Git installation

Recommended fix:

1. Install Git for Windows.
2. Reopen the terminal.
3. Run:

```powershell
git --version
```

Fallback:

- You can still run the audit, demo, and bootstrap checks before Git is available.
- Publish only after Git is correctly installed.

## 2. `python` exists but dependencies are missing

Symptom:

- workflow CLI fails on import
- `PyYAML` or other modules are missing

Likely cause:

- dependencies were not installed in the current Python environment

Recommended fix:

```powershell
python -m pip install -r requirements.txt
```

Fallback:

- Use a clean virtual environment and reinstall dependencies there.

## 3. Skills do not appear after installation

Symptom:

- Codex does not seem to pick up `bi-engineer`, `bi-governance`, or `comensemos`

Likely cause:

- skills were copied to the wrong folder
- Codex session needs refresh
- `CODEX_HOME` differs from the expected location

Recommended fix:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_skills.ps1
```

Then confirm the target folder shown by the script and restart the Codex session if needed.

Fallback:

- Run the installer with an explicit target root that matches your Codex skills directory.

## 4. No local Power BI Desktop instance is detected

Symptom:

- `python .\scripts\workflow_cli.py detect-pbi` returns zero instances

Likely cause:

- Power BI Desktop is not open
- the local Analysis Services workspace has not been created yet
- the installed Desktop variant stores the workspace differently

Recommended fix:

1. Open Power BI Desktop.
2. Open or create a PBIX.
3. Re-run:

```powershell
python .\scripts\workflow_cli.py detect-pbi
```

Fallback:

- Use the offline TMDL workflow instead.
- The demo and starter flow do not require a live PBIX.

## 5. MCP live tooling is not available in the current Codex session

Symptom:

- the session cannot connect live to Fabric or a local PBIX even though the docs mention that path

Likely cause:

- the active Codex environment does not expose the Power BI / Fabric MCP tools

Recommended fix:

- Use the repository in offline / TMDL-first mode.
- If you control the Codex environment, enable the Power BI MCP tooling for that session.

Fallback:

- Keep working with exported TMDL folders and local snapshots.

## 6. `connect-fabric` prepares the payload but does not connect

Symptom:

- `python .\scripts\workflow_cli.py connect-fabric --config .\config\workflow.example.yaml` prints JSON instead of opening a live connection

Likely cause:

- this command is intentionally a safe planning helper in v1

Recommended fix:

- Use the generated payload with the available Codex MCP Power BI/Fabric tooling.

Fallback:

- Stay in offline mode and work with local TMDL exports.

## 7. The offline demo works but the live workflow does not

Symptom:

- demo commands pass
- live PBIX or Fabric workflow is blocked

Likely cause:

- missing Desktop instance
- missing Fabric access
- missing MCP live support

Recommended fix:

- Treat the offline demo as the baseline health check.
- Solve the live dependency separately without changing the public core.

Fallback:

- Continue validating logic with starter catalog, dictionary, and TMDL snapshots.

## 8. Private workspace layering is unclear

Symptom:

- someone tries to put client artifacts, workspace exports, or private dictionaries inside `analytics_ai_core`

Likely cause:

- confusion between the public core and the private operational workspace

Recommended fix:

- Keep private artifacts in a separate private repo or folder.
- Use `docs/private-workspace.md` as the reference pattern.

Fallback:

- If in doubt, do not copy anything from the private workspace into the public core until it passes the publication audit and manual review.

## Known v1 limitations

- Live Power BI / Fabric connectivity depends on the active Codex environment exposing MCP support.
- The v1 bootstrap does not create the GitHub repository automatically.
- The v1 public core does not package the private domain pack.
- The v1 public core does not rotate or verify rotation of credentials from the private workspace.
- The `connect-fabric` command prepares a safe payload but does not perform the live connection by itself.
