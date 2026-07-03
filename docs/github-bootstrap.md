# GitHub Bootstrap

Use this guide to publish `analytics_ai_core` safely as a new public repository.

## Safety rule first

Never publish from the private workspace root.

Only publish the folder:

```text
analytics_ai_core
```

Before any Git commands, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_public_repo.ps1
```

## Official v1 path: GitHub web + local Git

### 1. Create an empty repository in GitHub

From the GitHub web UI:

1. Create a new repository.
2. Choose the final public name you want.
3. Leave it empty:
   - no README
   - no `.gitignore`
   - no license unless you explicitly want to add one here
4. Copy the remote URL that GitHub shows after creation.

### 2. Initialize Git locally if needed

Run these commands inside `analytics_ai_core`:

```powershell
git init
git checkout -b main
git add .
git commit -m "Initial public core release"
```

If the folder is already a Git repo, inspect it first:

```powershell
git status
git branch --show-current
git remote -v
```

### 3. Add the remote and push

Replace `<YOUR_GITHUB_REMOTE_URL>` with the URL from GitHub:

```powershell
git remote add origin <YOUR_GITHUB_REMOTE_URL>
git push -u origin main
```

If `origin` already exists, review it before changing anything:

```powershell
git remote -v
```

Only if the existing remote is wrong and you explicitly want to replace it:

```powershell
git remote remove origin
git remote add origin <YOUR_GITHUB_REMOTE_URL>
git push -u origin main
```

## Optional appendix: if you use GitHub CLI

This is not the official v1 path, but it can be useful if `gh` is already installed and authenticated.

```powershell
gh repo create <repo-name> --public --source . --remote origin --push
```

Use this only after the audit and bootstrap checks pass.

## Final verification after first push

Review the GitHub repo page and confirm:

- only `analytics_ai_core` content was published
- no `.env` or auth artifacts appear
- no private workspace exports appear
- no real workspace names, emails, or endpoints appear in visible files
