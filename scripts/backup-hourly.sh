#!/bin/bash
set -euo pipefail
mkdir -p /work/backups/ch14
while true; do
 mongodump --uri "$MONGO_URI" --db college_ch14 --archive="/work/backups/ch14/snapshot-$(date -u +%Y%m%dT%H%M%SZ).archive"
 find /work/backups/ch14 -maxdepth 1 -type f -name 'snapshot-*.archive' -mtime +7 -delete
 sleep 3600
done
