# MongoDB laboratory exercises

**Windows users:** follow the [Windows setup and presentation guide](../docs/WINDOWS_SETUP.md) first. Run these commands in Ubuntu on WSL 2 with Docker Desktop integration enabled.

Run one selected chapter topology:

```bash
./scripts/lab.sh ch01 --mode quick
```
Replace `ch01` with `ch02` through `ch18`. Use `--mode full` for graded counts. Each chapter has its own README and activity entrypoints. Shared setup is intentionally reused; some activity scripts run prerequisite demonstrations too. The original faculty reference is preserved under `reference/faculty`, while the runnable adaptations live here.

## Requirements and modes

Docker Engine access, Compose, internet for initial images/packages/models, and available disk. The complete lab image includes CPU PyTorch, embeddings and three database drivers and is substantially larger than the mini-project image. Build it once; subsequent runs reuse layers. MongoDB 7.0 is used for local labs. Record actual image versions/digests when grading; minor image tags are not immutable pins.

Only one topology should run at a time on this laptop. The launcher prints its exact stop command. Stop preserves named volumes. Reset operations are restricted to `college_*` databases, and exercises reset only their own fixtures unless the chapter explicitly demonstrates migrations or sharding. Sharding and PITR use disposable targets. Never point these exercises at production databases.

Quick mode reduces large workloads; full mode uses the specified sizes. Both record actual counts. No benchmark speed ordering or election result is assumed. Chapter 18 quick mode uses only three distinct historical public advisories, and is not a 100,000-record completion claim.

## Evidence

`results/chNN/<UTC-run-id>/result.json` records mode, events, counts, measurements, assertions, and pass/partial/blocked/fail. The launcher also records its console output, including Docker failures. An activity skipped for missing account/runtime information is not successful evidence. Source code and static checks alone are not a live verification.

## Optional configuration

- `MONGO_URI_ATLAS`: Chapters 2 and 17 only.
- `ANNUAL_REPORTS_URL` and `REPORT_MIN_YEAR`: Chapter 7 read-only annual report check.
- `OLLAMA_BASE_URL`: Chapter 17 model service reachable from its container.
- `JWT_SECRET`: optional for the reproducible Chapter 15 test run (it generates a transient test secret if absent); mandatory for a separately hosted task API.
- Kubernetes context: run `scripts/kubernetes.sh` separately for Chapter 13 persistence/rejoin evidence.

## Supplementary experiments

- Chapter 8: `./scripts/arbiter.sh` starts and removes an independent arbiter topology. The main chapter launcher also runs it.
- Chapter 9: `./scripts/partition.sh` disconnects the observed secondaries and reconnects in a cleanup trap. The main launcher also runs it. After an uncatchable process termination, restore with `docker compose -p college-replica -f infra/replica.yaml down` then start that topology again; volumes are preserved.
- Chapter 13: after the chapter run, `./scripts/exporter.sh` captures real Prometheus metrics. `./scripts/kubernetes.sh` creates its own namespace and verifies recreation of mongo-2 with retained data.
- Chapter 14: `./scripts/pitr.sh` creates an isolated restore member and verifies a timestamp cutoff. Start hourly backups with `docker compose -p college-replica -f infra/replica.yaml -f infra/backup.yaml up -d backup`. Retention is confined to `backups/ch14`.
- Chapter 15 task server: `docker compose -p college-basic -f infra/standalone.yaml run --rm -p 127.0.0.1:8001:8001 -e JWT_SECRET --entrypoint uvicorn lab labs.ch15.api:app --host 0.0.0.0 --port 8001`.
- Chapter 17 local FAISS only: `./scripts/lab.sh ch17 --activity 2 --mode full`. Atlas and FAISS outputs are labeled separately.

## Known rubric ambiguities

Chapter 1 extension definitions, Chapter 3 submission format, Chapter 4's fifth bulk change, Chapter 7's exact annual-report source, and Chapter 16 enrollment queries are absent from the inspected reference. Gap notices and provisional decisions are explicit; they are not presented as confirmed faculty instructions. CTI Digest report metadata export remains unverified because its readable public page supplied only a client-rendered shell.
