#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
./scripts/secrets.sh
mkdir -p results/ch13
exec > >(tee "results/ch13/kubernetes-$(date -u +%Y%m%dT%H%M%SZ).log") 2>&1
kubectl create namespace college-mongo --dry-run=client -o yaml | kubectl apply -f -
kubectl -n college-mongo create secret generic mongo-auth --from-file=keyfile=.secrets/keyfile --from-file=password=.secrets/password --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f infra/k8s/mongo.yaml
kubectl -n college-mongo rollout status statefulset/mongo --timeout=240s
kubectl -n college-mongo exec mongo-0 -- mongosh --quiet --eval 'try{rs.initiate({_id:"kube",members:[{_id:0,host:"mongo-0.mongo.college-mongo.svc.cluster.local:27017"},{_id:1,host:"mongo-1.mongo.college-mongo.svc.cluster.local:27017"},{_id:2,host:"mongo-2.mongo.college-mongo.svc.cluster.local:27017"}]})}catch(e){print(e.codeName)}'
sleep 15
primary=$(kubectl -n college-mongo exec mongo-0 -- mongosh --quiet --eval 'print(db.hello().primary.split(".")[0])' | tail -n 1)
kubectl -n college-mongo exec "$primary" -- mongosh --quiet --eval 'try{db.getSiblingDB("admin").createUser({user:"admin",pwd:require("fs").readFileSync("/secret/password","utf8").trim(),roles:["root"]})}catch(e){print(e.codeName)}'
check='db.getSiblingDB("admin").auth("admin",require("fs").readFileSync("/secret/password","utf8").trim());'
kubectl -n college-mongo exec "$primary" -- mongosh --quiet --eval "$check db.getSiblingDB('college_ch13').probe.updateOne({_id:1},{\$set:{value:'persistent'}},{upsert:true,writeConcern:{w:3,wtimeout:10000}}); printjson(rs.status());"
old_uid=$(kubectl -n college-mongo get pod mongo-2 -o jsonpath='{.metadata.uid}')
kubectl -n college-mongo delete pod mongo-2
kubectl -n college-mongo wait --for=condition=Ready pod/mongo-2 --timeout=180s
new_uid=$(kubectl -n college-mongo get pod mongo-2 -o jsonpath='{.metadata.uid}')
[ "$old_uid" != "$new_uid" ]
kubectl -n college-mongo exec mongo-2 -- mongosh --quiet --eval "$check db.getMongo().setReadPref('secondaryPreferred'); const d=db.getSiblingDB('college_ch13').probe.findOne({_id:1}); assert.eq(d.value,'persistent'); printjson(d); printjson(rs.status());"
