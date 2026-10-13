$ErrorActionPreference = "Stop"

Write-Host "Running postprovision hook..."

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "Creating Python virtual environment..."
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 -m venv (Join-Path $repoRoot ".venv")
    }
    elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python -m venv (Join-Path $repoRoot ".venv")
    }
    else {
        throw "Python 3.10 or later is required but was not found on PATH."
    }

    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $venvPython)) {
        throw "Failed to create the Python virtual environment."
    }
}

$python = $venvPython

& $python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 'Python 3.10 or later is required.')"
if ($LASTEXITCODE -ne 0) {
    throw "The Python virtual environment must use Python 3.10 or later."
}

function Invoke-Python {
    & $python @args
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code $LASTEXITCODE`: $($args -join ' ')"
    }
}

Push-Location $repoRoot
try {
# Install Python dependencies first (needed for key fetching below)
Invoke-Python -m pip install -r notebooks\requirements.txt --quiet

# Write .env and fetch API keys using azure-identity (no az CLI needed)
Invoke-Python infra\setup-env.py

# Create indexes and upload data
Write-Host "Running knowledge setup..."
Invoke-Python infra\create-knowledge.py

# Set up Fabric Lakehouse (if capacity was deployed)
if ($env:FABRIC_CAPACITY_ID) {
    Write-Host "Setting up Fabric Lakehouse..."
    Invoke-Python infra\create-lakehouse.py
}

Write-Host "Postprovision complete. Open notebooks/ to prepare the live demo."
}
finally {
    Pop-Location
}
