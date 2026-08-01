# Build LiteratureReviewInstaller.exe on Windows
$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Dist = Join-Path $Root "dist"
$Build = Join-Path $Root "build\pyi-build"
$AppName = "LiteratureReviewInstaller"
$OutName = "${AppName}-windows.exe"

Set-Location $Root

Write-Host "==> Vendoring offline skills into bundled/"
if (Test-Path (Join-Path $Root "build\vendor_skills.sh")) {
  # Prefer committed bundled/; refresh via bash when Git Bash / WSL available.
  $bash = Get-Command bash -ErrorAction SilentlyContinue
  if ($bash) {
    & bash (Join-Path $Root "build\vendor_skills.sh")
  } elseif (-not (Test-Path (Join-Path $Root "bundled\skills\academic-search\SKILL.md"))) {
    throw "bundled/skills missing. Commit vendored skills or run build/vendor_skills.sh"
  } else {
    Write-Host "Using committed bundled/ skills (bash not found)"
  }
}

Write-Host "==> Installing build dependency (pyinstaller)"
python -m pip install -q -r requirements-gui.txt

Write-Host "==> Cleaning previous build outputs"
if (Test-Path $Dist) {
  Remove-Item -Recurse -Force (Join-Path $Dist $AppName) -ErrorAction SilentlyContinue
  Remove-Item -Force (Join-Path $Dist "$AppName.exe") -ErrorAction SilentlyContinue
  Remove-Item -Force (Join-Path $Dist $OutName) -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Force -Path $Dist | Out-Null
New-Item -ItemType Directory -Force -Path $Build | Out-Null

Write-Host "==> Running PyInstaller"
python -m PyInstaller `
  --noconfirm `
  --clean `
  --distpath $Dist `
  --workpath $Build `
  (Join-Path $Root "build\installer.spec")

$ExePath = Join-Path $Dist "$AppName.exe"
if (-not (Test-Path $ExePath)) {
  throw "Expected exe at $ExePath"
}

Copy-Item -Force $ExePath (Join-Path $Dist $OutName)

Write-Host "[OK] Windows installer ready:"
Write-Host "  $(Join-Path $Dist $OutName)"
