param(
    [string]$SourceRoot = "",
    [string]$TargetRoot = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($SourceRoot)) {
    $SourceRoot = Split-Path -Parent $PSScriptRoot
}

if ([string]::IsNullOrWhiteSpace($TargetRoot)) {
    if ($env:CODEX_HOME) {
        $TargetRoot = Join-Path $env:CODEX_HOME "skills"
    }
    else {
        $TargetRoot = Join-Path $HOME ".codex\\skills"
    }
}

$SkillsSource = Join-Path $SourceRoot "skills"
if (-not (Test-Path $SkillsSource)) {
    throw "Skills source folder not found: $SkillsSource"
}

New-Item -ItemType Directory -Force -Path $TargetRoot | Out-Null

$installed = @()
Get-ChildItem -Path $SkillsSource -Directory | ForEach-Object {
    $destination = Join-Path $TargetRoot $_.Name
    if (Test-Path $destination) {
        Remove-Item -LiteralPath $destination -Recurse -Force
    }
    Copy-Item -Path $_.FullName -Destination $destination -Recurse -Force
    $installed += $_.Name
}

Write-Host "[OK] Installed skills:"
$installed | Sort-Object | ForEach-Object { Write-Host " - $_" }
Write-Host "Target: $TargetRoot"
