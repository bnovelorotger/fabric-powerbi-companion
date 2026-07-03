# Publish Checklist

Before the first public push:

1. Rotate any credentials that were ever stored in the private workspace.
2. Confirm no `.env`, auth cache, or temporary export folders are present.
3. Confirm that the folder you are about to publish is `analytics_ai_core` and not the private workspace root.
4. Run:

```powershell
python .\scripts\workflow_cli.py audit-public-repo
```

5. Review findings for:
   - secrets
   - local absolute paths
   - real emails
   - real workspace names
   - Fabric endpoints
   - oversized files

6. Verify the demo still runs offline from TMDL:

```powershell
python .\scripts\workflow_cli.py validate-environment
python .\scripts\workflow_cli.py validate-brief .\projects\demo-enrollment-sandbox\brief.yaml
python .\scripts\workflow_cli.py snapshot-from-tmdl .\projects\demo-enrollment-sandbox\artifacts\pbix_snapshot_tmdl .\projects\demo-enrollment-sandbox\artifacts\model_snapshot.json
python .\scripts\workflow_cli.py compare-dictionary .\dictionary .\projects\demo-enrollment-sandbox\artifacts\model_snapshot.json --output .\projects\demo-enrollment-sandbox\logs\dictionary_compare.yaml
```

7. Verify skill installation:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_skills.ps1
```

8. Review `config/workflow.example.yaml` manually and confirm it still contains only placeholders.
9. Run the local bootstrap:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_public_repo.ps1
```

## Red flags

Stop and fix the repo before any push if you find:

- real emails
- real Fabric endpoints
- paths like `C:\Users\...`
- names of real workspaces or tenants
- private snapshots, catalogs, or TMDL exports
- `.env`, `auth.json`, `cache.bin`, or similar auth artifacts
- files copied from the private workspace that are not needed for the public core
