#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Tools run inside the lab image. Dedicated target ensures full oplog restore cannot overwrite the demo.
docker compose -p college-replica -f infra/replica.yaml --profile pitr up -d restore
sleep 5
docker compose -p college-replica -f infra/replica.yaml exec -T restore mongosh --quiet --eval 'try{rs.status()}catch(e){rs.initiate({_id:"restore",members:[{_id:0,host:"restore:27017"}]})}'
sleep 5
docker compose -p college-replica -f infra/replica.yaml run --rm --entrypoint python lab -m labs.shared.pitr
