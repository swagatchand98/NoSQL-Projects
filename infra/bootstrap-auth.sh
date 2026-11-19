#!/bin/bash
set -eu
mkdir -p /run/mongo
cp /input/server.pem /input/ca.crt /input/keyfile /run/mongo/
chmod 400 /run/mongo/*
# This isolated lab image starts as root so the copied secrets never need host permission changes.
args=(--bind_ip_all --auth --tlsMode requireTLS --tlsCertificateKeyFile /run/mongo/server.pem --tlsCAFile /run/mongo/ca.crt --tlsAllowConnectionsWithoutCertificates --logpath /tmp/mongo.log --fork)
if [ -n "${RS_MEMBER:-}" ]; then args+=(--replSet secure --keyFile /run/mongo/keyfile); fi
mongod "${args[@]}"
if [ -z "${RS_MEMBER:-}" ]; then
 mongosh --host localhost --tls --tlsCAFile /input/ca.crt --quiet --eval 'try { db.getSiblingDB("admin").createUser({user:"admin",pwd:require("fs").readFileSync("/input/password","utf8").trim(),roles:["root"]}) } catch(e) { print(e.codeName) }'
fi
trap 'mongod --shutdown --dbpath /data/db || true' TERM INT
while kill -0 "$(cat /data/db/mongod.lock)" 2>/dev/null; do sleep 2; done
