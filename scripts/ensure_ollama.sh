#!/usr/bin/env bash
set -euo pipefail

# Wrapper to ensure Ollama server and required models using the backend CLI.
# Honors OLLAMA_HOST, DEFAULT_MODEL, EMBED_MODEL environment variables.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT/backend"

# Use uv to run the packaged console script inside the project venv
if [[ ! -d .venv ]]; then
  uv sync >/dev/null
fi

# shellcheck disable=SC2068
uv run ensure-ollama $@
