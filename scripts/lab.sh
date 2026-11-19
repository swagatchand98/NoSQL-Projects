#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
chapter=${1:?Usage: ./scripts/lab.sh chNN --mode quick};shift
case "$chapter" in
 ch01|ch02|ch03|ch04|ch05|ch06|ch07|ch15|ch17) topology=standalone;project=college-basic;;
 ch08|ch09|ch10|ch14) topology=replica;project=college-replica;;
 ch11) topology=shards;project=college-shards;;
 ch12) ./scripts/secrets.sh;topology=auth;project=college-auth;;
 ch13) ./scripts/secure-replica.sh;topology=secure;project=college-secure;;
 ch16|ch18) topology=polyglot;project=college-polyglot;;
 *) echo 'Unknown chapter' >&2;exit 2;;
esac
args=(-p "$project" -f "infra/$topology.yaml")
mkdir -p "results/$chapter"
log="results/$chapter/launcher-$(date -u +%Y%m%dT%H%M%SZ).log"
exec > >(tee "$log") 2>&1
printf 'Chapter %s; options %s\n' "$chapter" "$*"
docker compose "${args[@]}" build lab
docker compose "${args[@]}" run --rm lab "$chapter" "$@"
if [ "$chapter" = ch09 ]; then ./scripts/partition.sh; fi
if [ "$chapter" = ch08 ]; then ./scripts/arbiter.sh; fi
printf 'Stop this topology: docker compose -p %s -f infra/%s.yaml down\n' "$project" "$topology"
