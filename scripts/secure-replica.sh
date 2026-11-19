#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
./scripts/secrets.sh
args=(-p college-secure -f infra/secure.yaml)
docker compose "${args[@]}" up -d mongo1 mongo2 mongo3
sleep 8
docker compose "${args[@]}" exec -T mongo1 mongosh --host localhost --tls --tlsCAFile /input/ca.crt --quiet --eval 'try {rs.initiate({_id:"secure",members:[{_id:0,host:"mongo1:27017",priority:2},{_id:1,host:"mongo2:27017"},{_id:2,host:"mongo3:27017"}]})}catch(e){print(e.codeName)}'
sleep 15
primary=$(docker compose "${args[@]}" exec -T mongo1 mongosh --host localhost --tls --tlsCAFile /input/ca.crt --quiet --eval 'print(db.hello().primary.split(":")[0])' | tail -n 1)
docker compose "${args[@]}" exec -T "$primary" mongosh --host localhost --tls --tlsCAFile /input/ca.crt --quiet --eval 'try {db.getSiblingDB("admin").createUser({user:"admin",pwd:require("fs").readFileSync("/input/password","utf8").trim(),roles:["root"]})}catch(e){print(e.codeName)}'
