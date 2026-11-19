#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
password=$(cat .secrets/password)
export EXPORTER_MONGODB_URI="mongodb://exporter:${password}@mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=secure&authSource=admin&tls=true&tlsCAFile=/input/ca.crt"
docker compose -p college-secure -f infra/secure.yaml --profile exporter up -d exporter
mkdir -p results/ch13
output="results/ch13/exporter-$(date -u +%Y%m%dT%H%M%SZ).txt"
curl --fail --retry 10 --retry-delay 2 http://localhost:9216/metrics > "$output"
grep -Eq '^mongodb_up(\{[^}]*\})? 1(\.0)?$' "$output"
