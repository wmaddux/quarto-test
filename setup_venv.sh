#!/usr/bin/env bash
# Create and populate venv for Health Maturity Report (macOS/Linux).
# After running, activate in your shell:  source .venv/bin/activate
# Usage: ./setup_venv.sh

set -e
cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  echo "Created .venv"
fi

.venv/bin/pip install --upgrade pip
.venv/bin/pip install pandas plotly jupyter pyyaml

echo "Done. Activate with:  source .venv/bin/activate"
