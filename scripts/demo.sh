#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -n "${OLLAMA_BASE_URL:-}" ]; then
  docker compose up -d --build
else
  docker compose --profile model up -d --build
  docker compose exec ollama ollama pull qwen2.5:1.5b || echo "Model download failed; search still works."
fi
printf 'Open http://localhost:8000
'
