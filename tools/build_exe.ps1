param(
    [string]$Name = "poe_AutoFlask",
    [string]$Entry = "main.py",
    [switch]$NoOneFile,
    [switch]$Console,
    [switch]$NoClean
)

$ErrorActionPreference = "Stop"

# Resolve repo root from script location.
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
Set-Location $RepoRoot

if (-not (Test-Path $Entry)) {
    throw "Entry file not found: $Entry"
}

if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    throw "PyInstaller is not installed. Run: pip install pyinstaller"
}

$argsList = @("--noconfirm")

if (-not $NoClean) {
    $argsList += "--clean"
}

if (-not $NoOneFile) {
    $argsList += "--onefile"
}

if (-not $Console) {
    $argsList += "--windowed"
}

$argsList += @(
    "--name", $Name,
    $Entry
)

Write-Host "Building EXE..." -ForegroundColor Cyan
Write-Host ("Command: pyinstaller " + ($argsList -join " "))

& pyinstaller @argsList
if ($LASTEXITCODE -ne 0) {
    throw "Build failed with exit code $LASTEXITCODE"
}

$distExe = Join-Path $RepoRoot ("dist\" + $Name + ".exe")
if (Test-Path $distExe) {
    $item = Get-Item $distExe
    Write-Host ""
    Write-Host "Build success." -ForegroundColor Green
    Write-Host ("EXE: " + $item.FullName)
    Write-Host ("Size: " + [math]::Round($item.Length / 1MB, 2) + " MB")
    Write-Host ("Time: " + $item.LastWriteTime)
} else {
    Write-Host ""
    Write-Host "Build finished, but EXE not found at expected path:" -ForegroundColor Yellow
    Write-Host $distExe
}
