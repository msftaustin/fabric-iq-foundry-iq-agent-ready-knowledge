#!/bin/sh
set -eu

echo "Running postprovision hook..."

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
VENV_PYTHON="$REPO_ROOT/.venv/bin/python"

if [ ! -x "$VENV_PYTHON" ]; then
    echo "Creating Python virtual environment..."
    if ! command -v python3 >/dev/null 2>&1; then
        echo "Python 3.10 or later is required but was not found on PATH." >&2
        exit 1
    fi
    python3 -m venv "$REPO_ROOT/.venv"
fi

cd "$REPO_ROOT"

"$VENV_PYTHON" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 'Python 3.10 or later is required.')"

# Install Python dependencies first (needed for key fetching below)
"$VENV_PYTHON" -m pip install -r notebooks/requirements.txt --quiet

# Write .env and fetch API keys using azure-identity (no az CLI needed)
"$VENV_PYTHON" infra/setup-env.py

# Create indexes and upload data
echo "Running knowledge setup..."
"$VENV_PYTHON" infra/create-knowledge.py

# Set up Fabric Lakehouse (if capacity was deployed)
if [ -n "${FABRIC_CAPACITY_ID:-}" ]; then
    echo "Setting up Fabric Lakehouse..."
    "$VENV_PYTHON" infra/create-lakehouse.py
fi

echo "Postprovision complete. Open notebooks/ to prepare the live demo."