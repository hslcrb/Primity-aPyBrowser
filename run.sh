#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
if [[ ! -x .venv/bin/python ]]; then
    echo "먼저 가상환경과 requirements.txt를 설치하세요. See README.md."
    exit 1
fi
exec .venv/bin/python main.py "$@"

