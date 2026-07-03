# Quickstart

## 1. Install requirements

```powershell
python -m pip install -r requirements.txt
```

## 2. Install skills

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_skills.ps1
```

## 3. Check environment

```powershell
python .\scripts\workflow_cli.py validate-environment
```

## 4. Try the demo

```powershell
python .\scripts\workflow_cli.py validate-brief .\projects\demo-enrollment-sandbox\brief.yaml
python .\scripts\workflow_cli.py build-semantic-spec .\projects\demo-enrollment-sandbox\brief.yaml .\projects\demo-enrollment-sandbox\semantic_spec.yaml
python .\scripts\workflow_cli.py snapshot-from-tmdl .\projects\demo-enrollment-sandbox\artifacts\pbix_snapshot_tmdl .\projects\demo-enrollment-sandbox\artifacts\model_snapshot.json
python .\scripts\workflow_cli.py compare-dictionary .\dictionary .\projects\demo-enrollment-sandbox\artifacts\model_snapshot.json --output .\projects\demo-enrollment-sandbox\logs\dictionary_compare.yaml
```

## 5. Prepare the local public repo

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_public_repo.ps1
```

## 6. Publish manually to GitHub

Follow [github-bootstrap.md](github-bootstrap.md) to:

- create the empty GitHub repo manually
- initialize Git locally if needed
- create the first commit
- add `origin`
- push the public core

Never publish the private workspace root. Publish only `analytics_ai_core`.

## 7. Publish checklist

```powershell
python .\scripts\workflow_cli.py audit-public-repo
```

See also:

- [publish-checklist.md](publish-checklist.md)
- [runbook.md](runbook.md)
