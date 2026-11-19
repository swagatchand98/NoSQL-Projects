# Snapshot recovery and timestamp replay

Hourly `mongodump` archives retain seven days in `backups/ch14`. A successful hourly schedule implies an assumed snapshot RPO of up to one hour, plus scheduling/failure delays; it does not imply continuous recovery. Measured restore time is only the tool/data-validation part of RTO. Detection, provisioning, credential recovery, and application restart add time.

The snapshot exercise modifies original values and restores to `college_ch14_restored`, checking counts and a canonical content checksum at 1k/10k/100k records in full mode.

The separate PITR script uses a matching-version replica-set target on `restore:27017`, a complete `mongodump --oplog`, and a controlled subsequent oplog interval. It restores with `--oplogReplay --oplogLimit`, using an exclusive timestamp cutoff before an unwanted update, then asserts the wanted value. There must be no unrelated concurrent writers during this controlled demonstration. This is an oplog timestamp exercise, not a production continuous-backup system. RPO beyond the snapshot depends on retained contiguous oplog coverage.

Source and destination versions are compared at runtime. Full oplog replay cannot be combined with collection-scoped or namespace-remapping restore options. Never point the restore URI at a production deployment.

https://www.mongodb.com/docs/database-tools/mongorestore/
