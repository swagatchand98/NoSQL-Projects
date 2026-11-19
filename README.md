# Linux Threat Intelligence Assistant

A local threat-intelligence web app and 18 NoSQL laboratory chapters using MongoDB, with Cassandra and Neo4j integration exercises.

**Presenting on Windows? Start with the [beginner-friendly Windows setup guide](docs/WINDOWS_SETUP.md).** It covers WSL 2, Docker Desktop, configuration, the web demo, all lab topologies, results, and troubleshooting. Run the Bash commands below inside Ubuntu on WSL 2.

Local Linux quick runs have been exercised; Windows and the complete web/model demonstration still need verification on the presentation computer. See [verification status](STATUS.md).

## Start

```bash
./scripts/demo.sh
```
Open http://localhost:8000. Stop with `docker compose down` (preserves data).
The script starts MongoDB, FastAPI and Ollama, then downloads `qwen2.5:1.5b`.
The model download is approximately 986 MB; allow 2 GB for model storage plus Docker images and database storage. Initial setup requires internet. Later searches and model inference run locally.

Reuse host Ollama:
```bash
ollama serve
ollama pull qwen2.5:1.5b
OLLAMA_BASE_URL=http://host.docker.internal:11434 ./scripts/demo.sh
```
Host Ollama must listen on an interface reachable from the Docker bridge; loopback-only listening will not work. Containerized Ollama is the simpler default.

Repeat seed:
```bash
docker compose exec app python -c 'from app.main import seed; print(seed())'
```
Expected count: 12 classroom records describing three distinct advisories. Repeating seeding must keep 12 records. This is not twelve distinct vulnerabilities.

## Five-minute demonstration

1. 0:00–1:00: open the page, search `openssh`, clear search, select each lifecycle filter.
2. 1:00–2:00: open a record; show package, date, source and mitigation. Explain that lifecycle observations are fictional classroom scenarios.
3. 2:00–3:00: ask “Which active Linux threats in this dataset need attention?”
4. 3:00–4:00: ask “What should I do about the first one?” Show the retained conversation and retrieved source links.
5. 4:00–5:00: ask “What is the weather in Tokyo?” Show insufficient evidence. Explain model status and that search works independently.

The answer text is real Ollama output, never prerecorded. Source links beneath it identify retrieved context, not independently validated claims. The shared chat module rejects bracketed references outside the retrieved record IDs. This checks identifiers, not the factual entailment of every model sentence. Conversation storage retains five exchanges. Concurrent requests to the same conversation are not serialized in this checkpoint.

## Evidence and limitations

The user has run local Linux quick-mode labs for Chapters 2–18, including a successful Chapter 16 rerun after fixes. External Atlas/Kubernetes checks, the separate Chapter 9 partition rerun, exporter/PITR experiments, full-scale workloads, and the web/model demonstration are not all verified by those runs. Windows execution remains unverified. Local evidence is written under `results/` and is excluded from Git.

The dataset uses advisory publication dates, not a claim of current threat intelligence. Facts are paraphrased from Ubuntu's CVE-2024-6387, CVE-2023-4911 and CVE-2024-3094 pages, linked in each record. Mitigation text is defensive classroom guidance; consult the release-specific advisory.

## Faculty reference

https://github.com/sujeetjagtap/NoSQL-Databases-using-MongoDB
Inspected reference revision: `7898bc8907937941a0e2af152654e28f5860bcb4`.
The app is newly written; the reference informed activity mapping and RAG organization. The inspected faculty reference is preserved under `reference/faculty`; see [ATTRIBUTION.md](ATTRIBUTION.md) and [LICENSE](LICENSE).

## Remaining deliverables

Chapters 1–18 have implementations, shared helpers, activity folders, and isolated Compose topologies. Start with `./scripts/lab.sh ch01 --mode quick`; see [lab instructions](labs/README.md) for chapter details and supplemental experiments. Generate draft source ZIPs with `python3 scripts/package-chapters.py`. They are written to `submissions/chapters/` and are excluded from Git. Real screenshot documents and final verified reports remain separate deliverables. See [STATUS.md](STATUS.md) for known gaps.
