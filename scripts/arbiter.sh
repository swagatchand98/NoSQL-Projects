#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
args=(-p college-arbiter -f infra/arbiter.yaml)
mkdir -p results/ch08
exec > >(tee "results/ch08/arbiter-$(date -u +%Y%m%dT%H%M%SZ).log") 2>&1
trap 'docker compose "${args[@]}" down' EXIT INT TERM
docker compose "${args[@]}" up -d
sleep 8
docker compose "${args[@]}" exec -T data1 mongosh --quiet --eval 'rs.initiate({_id:"arb",members:[{_id:0,host:"data1:27017"},{_id:1,host:"data2:27017"},{_id:2,host:"arbiter:27017",arbiterOnly:true}]})'
sleep 15
docker compose "${args[@]}" exec -T data1 mongosh --quiet --eval 'printjson(rs.status())'
