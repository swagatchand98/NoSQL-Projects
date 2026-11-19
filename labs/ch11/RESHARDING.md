# MongoDB 7.0 resharding reference

The lab pins the server major version to 7.0. Confirm `server_info()` and FCV before applying a real reshard.

1. Inspect workload, candidate-key cardinality, skew, query targeting, and unique-index compatibility.
2. Confirm resource headroom, healthy replica sets, majority journaling, backups, and an acceptable write-blocking interval.
3. From mongos, issue `db.adminCommand({reshardCollection:"college_ch11.hashed",key:{customer_id:1}})` in a disposable copy if demonstrating the operation.
4. Monitor `currentOp`, completion, chunk placement, and client errors; re-run equality/range explain and per-shard counts afterward.
5. Avoid conflicting DDL during resharding and rebuild affected search indexes where required.

MongoDB 7.0 does not support the MongoDB 8.0 `forceRedistribution` same-key feature. Time-series resharding introduced in 8.0.10 must not be assumed for this lab. Only one collection is resharded at a time. This exercise documents resharding; its hotspot script measures explicit chunk placement, not a reshard execution.

Official references checked 2026-11-19:
- https://www.mongodb.com/docs/v7.0/core/sharding-reshard-a-collection/
- https://www.mongodb.com/docs/manual/core/sharding-reshard-a-collection/
