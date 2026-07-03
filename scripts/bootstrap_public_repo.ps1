param(
    [string]$RepoRoot = "",
    [string]$DefaultBranch = "main"
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = Split-Path -Parent $PSScriptRoot
}

$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$RepoName = Split-Path -Leaf $RepoRoot

if ($RepoName -ne "analytics_ai_core") {
    throw "This bootstrap must be run inside analytics_ai_core. Current root: $RepoRoot"
}

$requiredPaths = @(
    "README.md",
    ".gitignore",
    "requirements.txt",
    "skills",
    "scripts",
    "dictionary",
    "projects\demo-enrollment-sandbox"
)

$missing = @()
foreach ($relativePath in $requiredPaths) {
    $fullPath = Join-Path $RepoRoot $relativePath
    if (-not (Test-Path -LiteralPath $fullPath)) {
        $missing += $relativePath
    }
}

if ($missing.Count -gt 0) {
    throw "Missing required bootstrap paths: $($missing -join ', ')"
}

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCommand) {
    throw "Python is not available in PATH. Install Python 3.10+ before publishing this repo."
}

Push-Location $RepoRoot
try {
    Write-Host "[1/4] Running publication audit..."
    & python ".\scripts\workflow_cli.py" audit-public-repo
    if ($LASTEXITCODE -ne 0) {
        throw "audit-public-repo reported risks. Resolve them before publishing."
    }

    Write-Host "[2/4] Checking Git availability..."
    $gitCommand = Get-Command git -ErrorAction SilentlyContinue
    $gitAvailable = $null -ne $gitCommand
    $gitRepoInitialized = $false
    $currentBranch = ""
    $originUrl = ""

    if ($gitAvailable) {
        & git rev-parse --is-inside-work-tree *> $null
        $gitRepoInitialized = ($LASTEXITCODE -eq 0)
        if ($gitRepoInitialized) {
            $branchCandidate = (& git branch --show-current 2>$null)
            if ($LASTEXITCODE -eq 0) {
                $currentBranch = ($branchCandidate | Out-String).Trim()
            }
            $originCandidate = (& git remote get-url origin 2>$null)
            if ($LASTEXITCODE -eq 0) {
                $originUrl = ($originCandidate | Out-String).Trim()
            }
        }
    }

    Write-Host "[3/4] Publication readiness summary"
    Write-Host "Repo root: $RepoRoot"
    Write-Host "Git available: $gitAvailable"
    Write-Host "Git repo initialized: $gitRepoInitialized"
    if ($currentBranch) {
        Write-Host "Current branch: $currentBranch"
    }
    if ($originUrl) {
        Write-Host "Origin remote: $originUrl"
    }

    Write-Host "[4/4] Next local commands"
    if (-not $gitAvailable) {
        Write-Host "Git is not installed or not available in PATH."
        Write-Host "Install Git, reopen the terminal, and then run:"
        Write-Host "  git init"
        Write-Host "  git checkout -b $DefaultBranch"
        Write-Host '  git add .'
        Write-Host '  git commit -m "Initial public core release"'
    }
    elseif (-not $gitRepoInitialized) {
        Write-Host "Run the following commands from this folder:"
        Write-Host "  git init"
        Write-Host "  git checkout -b $DefaultBranch"
        Write-Host '  git add .'
        Write-Host '  git commit -m "Initial public core release"'
    }
    else {
        Write-Host "Local Git repository already detected."
        if (-not $currentBranch) {
            Write-Host "Recommended branch: $DefaultBranch"
        }
        if (-not $originUrl) {
            Write-Host "No origin remote detected. After creating the empty GitHub repo, run:"
            Write-Host "  git remote add origin <YOUR_GITHUB_REMOTE_URL>"
            Write-Host "  git push -u origin $DefaultBranch"
        }
        else {
            Write-Host "Origin is already configured. Review it carefully before any push."
        }
    }

    Write-Host ""
    Write-Host "[OK] analytics_ai_core is ready to publish locally."
    Write-Host "This bootstrap does not create a GitHub repository, does not add remotes, and does not push."
    Write-Host "Never publish the private workspace root. Publish only analytics_ai_core."
}
finally {
    Pop-Location
}
