#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
args=(-p college-replica -f infra/replica.yaml)
ids=()
network='college-replica_default'
declare -A aliases
cleanup() {
 local failed=0
 for id in "${ids[@]}"; do
  echo "Reconnecting ${aliases[$id]} ($id) to $network"
  docker network connect --alias "${aliases[$id]}" "$network" "$id" || failed=1
 done
 return "$failed"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
mkdir -p results/ch09
log="results/ch09/partition-$(date -u +%Y%m%dT%H%M%SZ).log"
exec > >(tee "$log") 2>&1
echo "Discovering the replica-set primary (30-second timeout)"
primary=$(timeout 30s docker compose "${args[@]}" exec -T mongo1 mongosh "mongodb://localhost:27017/?directConnection=true&serverSelectionTimeoutMS=5000" --quiet --eval 'print(db.hello().primary.split(":")[0])' | tail -n 1)
case "$primary" in
 mongo1|mongo2|mongo3) echo "Primary: $primary" ;;
 *) echo "Could not determine primary: $primary" >&2; exit 1 ;;
esac
for service in mongo1 mongo2 mongo3; do
 [ "$service" = "$primary" ] && continue
 id=$(docker compose "${args[@]}" ps -q "$service")
 aliases["$id"]="$service"
 echo "Disconnecting $service from $network"
 ids+=("$id")
 docker network disconnect "$network" "$id"
 timeout 25s docker compose "${args[@]}" exec -T "$primary" mongosh "mongodb://localhost:27017/?directConnection=true&serverSelectionTimeoutMS=5000" --quiet --eval 'for (const w of [1,"majority",3]) { try { printjson(db.getSiblingDB("college_ch09").probe.insertOne({t:new Date(),w:w}, {writeConcern:{w:w,wtimeout:3000}})) } catch(e) { print(e) } }; printjson(rs.status())' || true
 sleep 12
 timeout 25s docker compose "${args[@]}" exec -T "$primary" mongosh "mongodb://localhost:27017/?directConnection=true&serverSelectionTimeoutMS=5000" --quiet --eval 'printjson(rs.status())' || true
done
cleanup
ids=()
sleep 15
echo "Checking replication after reconnect"
timeout 120s docker compose "${args[@]}" run --rm lab ch08 --mode quick --activity 1
