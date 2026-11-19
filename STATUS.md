# Implementation and verification status

Updated from saved local Linux results on 2026-11-19. Quick-mode success covers the checks actually executed, not the full rubric or a Windows certification. Runtime evidence stays in the local `results/` directory and is not committed.

For Windows installation, configuration, and presentation steps, see [the Windows guide](docs/WINDOWS_SETUP.md).

| Chapter | Latest local quick run | Remaining scope / limitation |
|---|---|---|
| 01 | partial | Two extension definitions missing. |
| 02 | partial | Atlas check skipped without credentials. |
| 03 | passed | Faculty submission format unspecified. |
| 04 | passed | Fifth bulk operation is provisional. |
| 05 | passed | Full-scale / final submission verification still required. |
| 06 | passed | Full-scale / final submission verification still required. |
| 07 | partial | Annual-report source missing; CTI metadata requirement remains unverified. |
| 08 | passed | Arbiter output also supplied by user. |
| 09 | passed | Latency run passed; separate partition rerun is not yet confirmed. |
| 10 | passed | Full-scale / final submission verification still required. |
| 11 | passed | Full-scale / final submission verification still required. |
| 12 | passed | Full-scale / final submission verification still required. |
| 13 | partial | Kubernetes and separate exporter experiment not verified. |
| 14 | passed | Snapshot restore passed; separate PITR and hourly scheduling not verified. |
| 15 | passed | Full-scale / final submission verification still required. |
| 16 | passed | Successful rerun after startup and Neo4j parameter fixes; enrollment queries remain provisional. |
| 17 | partial | Local FAISS completed; Atlas RAG skipped. |
| 18 | passed | Three distinct bundled reports in quick mode; full public dataset not verified. |

## Other deliverables

- Web app and real model demonstration: implemented; complete browser/model verification still required on the presentation machine.
- Windows/WSL 2: setup documented, execution on Windows not yet verified.
- Unit tests: 12 passed after the Chapter 16 fixes. Unit tests do not verify live services.
- Submission archives: generated drafts; recreate with `python3 scripts/package-chapters.py`. Screenshot documents and final reports remain separate deliverables.
- Docker Hub publication is not part of the current setup. Images build locally from the repository.

## Exact faculty-reference gaps

Pinned reference: `7898bc8907937941a0e2af152654e28f5860bcb4`.

- Chapter 1 has two base activities; the two requested extensions are not identified.
- Chapter 3 has no submission format in its README.
- Chapter 4 says five bulk operations but contains four; the fifth reviewed-flag update is labeled provisional.
- Chapter 7 does not identify an exact annual-security-reports URL. Its CTI Digest page was only a client-rendered shell during inspection; the supplied dump uses attributed Ubuntu metadata instead and labels this gap.
- Chapter 16 uses fraud examples, not the three requested university enrollment queries. The student/course/instructor queries are provisional.
- Chapter 17 native IVF is not documented in the inspected Atlas API; the local FAISS substitution is explicitly labeled.
