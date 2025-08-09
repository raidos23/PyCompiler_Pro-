# PowerShell startup script equivalent to run.sh for Windows
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\run.ps1
# Or right-click the file and select "Run with PowerShell"

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Go to the directory containing this script
Set-Location -Path $PSScriptRoot

$VENV_DIR = "venv"

function Invoke-Checked {
    param(
        [Parameter(Mandatory=$true)][string]$Exe,
        [Parameter(Mandatory=$true)][string[]]$Args,
        [Parameter(Mandatory=$true)][string]$FailMessage
    )
    & $Exe @Args
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ $FailMessage (code $LASTEXITCODE)" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

# Detect a Python launcher/command
function Get-PythonCommand {
    if (Get-Command py -ErrorAction SilentlyContinue) { return 'py' }
    elseif (Get-Command python -ErrorAction SilentlyContinue) { return 'python' }
    elseif (Get-Command python3 -ErrorAction SilentlyContinue) { return 'python3' }
    else { return $null }
}

# Ensure virtual environment exists
if (-not (Test-Path -Path $VENV_DIR)) {
    Write-Host "⚙️  Création du venv..."
    $py = Get-PythonCommand
    if (-not $py) {
        Write-Host "❌ Python introuvable dans le PATH." -ForegroundColor Red
        exit 1
    }
    & $py -m venv $VENV_DIR
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Échec de la création du venv." -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

# venv python path (Windows)
$VENV_PY = Join-Path $VENV_DIR 'Scripts/python.exe'
if (-not (Test-Path -Path $VENV_PY)) {
    Write-Host "❌ Python du venv introuvable: $VENV_PY" -ForegroundColor Red
    exit 1
}

# Upgrade pip
Invoke-Checked -Exe $VENV_PY -Args @('-m','pip','install','--upgrade','pip') -FailMessage 'Échec mise à jour de pip'

# Install dependencies
if (Test-Path -Path 'requirements.txt') {
    Write-Host "📦 Installation des dépendances..."
    Invoke-Checked -Exe $VENV_PY -Args @('-m','pip','install','-r','requirements.txt') -FailMessage 'Échec installation des dépendances'
} else {
    Write-Host "⚠️ Aucun fichier requirements.txt trouvé. Dépendances non installées."
}

# Run main.py with the venv Python
Write-Host "🚀 Lancement de main.py..."
& $VENV_PY 'main.py'
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ main.py s'est terminé avec un code d'erreur $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}
