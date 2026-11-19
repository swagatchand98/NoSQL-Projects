#!/bin/bash
set -eu
for spec in config:cfg shard1:s1 shard2:s2; do
 host=${spec%:*}; rs=${spec#*:}
 until mongosh --host "$host" --quiet --eval 'db.adminCommand({ping:1})'; do sleep 2; done
 extra=''
 if [ "$host" = config ]; then extra='configsvr:true,'; fi
 mongosh --host "$host" --quiet --eval "try { rs.status() } catch(e) { rs.initiate({_id:'$rs',${extra}members:[{_id:0,host:'$host:27017'}]}) }"
done
until mongosh --host router --quiet --eval 'sh.addShard("s1/shard1:27017"); sh.addShard("s2/shard2:27017")'; do sleep 2; done
