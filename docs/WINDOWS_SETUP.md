# Windows setup and presentation guide

This guide takes you from a Windows computer to the web app and the chapter labs. You do not need to install Python packages, MongoDB, Cassandra, Neo4j, or Ollama directly on Windows. Docker runs those dependencies for you.

The supported workflow described here is **Windows → Ubuntu in WSL 2 → Docker Desktop (Linux containers)**. The project uses Bash scripts; run them in the Ubuntu terminal, not directly in PowerShell, Command Prompt, or Git Bash. Windows execution still needs a rehearsal on the presentation computer; successful Linux runs do not certify that machine.

## Contents

1. [What you need](#1-what-you-need)
2. [Install Ubuntu and Docker](#2-install-ubuntu-and-docker)
3. [Download the repository](#3-download-the-repository)
4. [Start the web application](#4-start-the-web-application)
5. [Present the project](#5-present-the-project)
6. [Run the chapter labs](#6-run-the-chapter-labs)
7. [Configure optional services](#7-configure-optional-services)
8. [Find results and take screenshots](#8-find-results-and-take-screenshots)
9. [Stop, restart, and update](#9-stop-restart-and-update)
10. [Troubleshooting](#10-troubleshooting)
11. [Final rehearsal checklist](#11-final-rehearsal-checklist)

## 1. What you need

- A Windows computer supported by the current Docker Desktop release. Windows 11 on an Intel/AMD 64-bit laptop is the intended presentation setup; other architectures have not been verified here. Check Docker's current [Windows requirements](https://docs.docker.com/desktop/setup/install/windows-install/) before installing.
- Permission to install WSL and Docker Desktop, and hardware virtualization enabled. If this is a college-managed machine, ask its administrator to complete installation beforehand.
- A reliable internet connection for the first build, database images, and model download.
- As a project planning allowance, aim for **16 GB RAM and 30 GB free disk**, with more space for full datasets, images, and backups. These are practical allowances, not measured minimums. Run one lab topology at a time.
- Access to [the GitHub repository](https://github.com/swagatchand98/NoSQL-Projects). A private repository requires access granted to the account cloning it.

**Terms used below:** an image is a downloaded application template; a container is a running instance; Compose starts a group of containers; a volume stores database or model data; a topology is one lab's group of database services. `~` means your Ubuntu home directory.

Only copy commands inside code blocks. Do not copy terminal prompts such as `$` or `PS C:\>`.

## 2. Install Ubuntu and Docker

### A. Install WSL 2 — PowerShell as Administrator

Right-click Start, open **Terminal (Admin)** or **Windows PowerShell (Admin)**, and run:

```powershell
wsl --install -d Ubuntu
```

Restart Windows if requested. Open **Ubuntu** from the Start menu and finish its first-time setup. Choose a Linux username and password. When entering a password, no characters appear; this is normal.

Back in **PowerShell**, check and update WSL:

```powershell
wsl --update
wsl --list --verbose
```

The Ubuntu row should show `VERSION 2`. If it shows `1`, run:

```powershell
wsl --set-version Ubuntu 2
```

If your distribution has another name, such as `Ubuntu-24.04`, use that exact name. Microsoft's [WSL installation guide](https://learn.microsoft.com/en-us/windows/wsl/install) covers installation failures and alternatives.

### B. Install Docker Desktop — Windows application

1. Download and install [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/).
2. Start Docker Desktop and complete its setup.
3. Use its **WSL 2 engine** and **Linux containers**. If the Docker menu offers “Switch to Linux containers,” select it.
4. In **Settings → Resources → WSL Integration**, enable integration for Ubuntu and apply the change. The exact layout can vary by Docker Desktop version.
5. Keep Docker Desktop running while using this project.

This follows Docker's [WSL development workflow](https://docs.docker.com/desktop/features/wsl/use-wsl/). Use Docker Desktop's engine; installing a separate Docker daemon inside Ubuntu can cause conflicting configurations.

### C. Prepare the Ubuntu terminal

From this point, commands marked `bash` run in **Ubuntu**. Open Ubuntu from Start and run:

```bash
sudo apt update
sudo apt install -y git curl openssl python3 ca-certificates

docker version
docker compose version
docker run --rm hello-world
```

`docker version` must display both Client and Server information. `hello-world` should print a success message. If Docker is not found, return to WSL Integration settings and reopen Ubuntu. Python here is for small maintenance scripts and tests; application dependencies are installed inside the Docker images.

## 3. Download the repository

Run in **Ubuntu**:

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/swagatchand98/NoSQL-Projects.git
cd NoSQL-Projects
git config core.autocrlf false
chmod +x scripts/*.sh infra/*.sh
```

Keep the project under `~/projects`, rather than a OneDrive folder or `/mnt/c/...`. This keeps Linux file permissions and bind mounts predictable. Docker also recommends storing code in the Linux distribution.

If cloning a private repository asks for authentication, use an authorized GitHub account and GitHub's token or SSH authentication. A GitHub account password is not an HTTPS Git credential. Do not put tokens in clone URLs, screenshots, or committed files.

Check your current directory:

```bash
pwd
ls
```

You should see `README.md`, `compose.yaml`, `scripts`, `labs`, and `infra`. Run all remaining project commands from this directory. To return later:

```bash
cd ~/projects/NoSQL-Projects
```

## 4. Start the web application

The web application is the **Linux Threat Intelligence Assistant**. It runs on Windows through Docker; “Linux” describes the advisory subject matter.

### First start

Default local setup needs no `.env` file and no cloud account:

```bash
./scripts/demo.sh
```

The script builds the app, starts MongoDB and Ollama, and downloads `qwen2.5:1.5b`. The model download is about 1 GB; the complete images need additional space. The first run may take several minutes or longer depending on the connection and CPU. Do not wait until the presentation to download it.

When the script finishes, open this address in **your Windows browser**:

**http://localhost:8000**

Check the services in Ubuntu:

```bash
docker compose --profile model ps
curl --fail http://localhost:8000/api/health
docker compose exec ollama ollama list
```

Expect the containers to be running, a JSON health response, and `qwen2.5:1.5b` in the model list. Read the health response: an HTTP response alone does not prove the model is ready. Ask a question in the page to verify actual generation. Search may work even when the model is unavailable.

If the script reports a model-download failure, retry:

```bash
docker compose exec ollama ollama pull qwen2.5:1.5b
```

### Optional app configuration

For the standard demonstration, leave defaults unchanged. To customize settings:

```bash
cp .env.example .env
nano .env
```

In nano, press **Ctrl+O**, Enter to save, then **Ctrl+X** to exit. `.env` is ignored by Git. Docker Compose reads it; it does not automatically export its entries into your Bash shell.

| Setting | Default / meaning |
|---|---|
| `OLLAMA_BASE_URL` | `http://ollama:11434`; app-to-model address inside the Compose network. Keep this for the normal setup. |
| `OLLAMA_MODEL` | `qwen2.5:1.5b`; the model requested by the app. |
| `MONGO_URI` | The app Compose file explicitly sets `mongodb://mongo:27017`; changing this key in `.env` alone does not override that file. |

Apply app configuration changes with:

```bash
docker compose --profile model up -d --build
```

If you change the model, also pull that exact model in the Ollama container. `demo.sh` always pre-downloads `qwen2.5:1.5b`; it does not automatically download a different model named in `.env`.

## 5. Present the project

Use this short sequence after confirming the model works:

1. Open the app and search for `openssh`.
2. Clear the search and show the lifecycle filters.
3. Open a record and explain its package, source date, mitigation, and source link.
4. Ask: **“Which active Linux threats in this dataset need attention?”** Wait for the generated answer.
5. Ask: **“What should I do about the first one?”** Show conversation context and source links.
6. Ask an unrelated question, such as **“What is the weather in Tokyo?”**, to demonstrate the limited evidence scope.

The seed contains **12 classroom records based on three distinct historical advisories**. Lifecycle observations are fictional classroom scenarios. Do not describe it as live threat monitoring or twelve distinct vulnerabilities. Generated citations identify retrieved context; they do not prove every model sentence is correct. CPU generation may take time.

The app stores up to five exchanges per conversation. Do not issue simultaneous chat requests in the same conversation during the demonstration.

## 6. Run the chapter labs

The web app and chapter labs are separate Compose projects. Stop the app before memory-heavy labs:

```bash
docker compose --profile model down
./scripts/lab.sh ch02 --mode quick
```

The first lab image build downloads CPU PyTorch and other packages, so it is larger than the web-app image. Later runs reuse cached layers. `CACHED` in build output is normal.

Use `ch01` through `ch18`. `quick` is for rehearsal; `full` uses larger workloads and may need substantial resources and internet. Run only the chapters needed for the presentation. Exercises reset their own classroom data; use dedicated lab databases and accounts.

| Chapters | Subject | Compose project | Configuration |
|---|---|---|---|
| 01–07 | Basics, CRUD, modeling, aggregation, indexes, reports | `college-basic` | `infra/standalone.yaml` |
| 08–10 | Replication, write concerns, transactions | `college-replica` | `infra/replica.yaml` |
| 11 | Sharding | `college-shards` | `infra/shards.yaml` |
| 12 | Roles and TLS | `college-auth` | `infra/auth.yaml` |
| 13 | Authenticated replica set | `college-secure` | `infra/secure.yaml` |
| 14 | Monitoring and backup/restore | `college-replica` | `infra/replica.yaml` |
| 15 | Tenant isolation | `college-basic` | `infra/standalone.yaml` |
| 16 | MongoDB, Cassandra, Neo4j integration | `college-polyglot` | `infra/polyglot.yaml` |
| 17 | Atlas RAG and local vector benchmarks | `college-basic` | `infra/standalone.yaml` |
| 18 | Comparative threat-data workloads | `college-polyglot` | `infra/polyglot.yaml` |

For example, move from Chapter 2 to Chapter 16:

```bash
docker compose -p college-basic -f infra/standalone.yaml down
./scripts/lab.sh ch16 --mode quick
```

A successful Chapter 16 run includes `enrollment_query` and `real_integration` events and an `Evidence:` path. The first startup of Cassandra/Neo4j can take time. Stop it afterward:

```bash
docker compose -p college-polyglot -f infra/polyglot.yaml down
```

For a full run, replace the mode:

```bash
./scripts/lab.sh ch06 --mode full
```

Some chapters support selecting activities; see their README before using `--activity`. For example, local vector measurements without the Atlas activity:

```bash
./scripts/lab.sh ch17 --activity 2 --mode quick
```

Chapter 8 also runs the separate arbiter experiment. Chapter 9 also runs the network-partition script: temporary disconnection and write failures are part of that experiment. Let its cleanup complete. Closing Ubuntu does not stop the database containers.

## 7. Configure optional services

These steps are **not needed for the local web-app demonstration**. An `external_check_blocked` event means an external part was skipped, even when local work completed.

### Atlas: Chapters 2 and 17

Create a dedicated MongoDB Atlas lab deployment and database user, allow your current client IP in Atlas Network Access, and obtain its driver connection string. Chapter 17 also needs a deployment supporting vector search and permissions to create the search index. Follow the current [Atlas connection instructions](https://www.mongodb.com/docs/atlas/connect-to-database-deployment/). Do not use a production database.

In Ubuntu, read the URI without putting it in shell history or displaying it:

```bash
read -rsp 'Atlas connection URI: ' MONGO_URI_ATLAS
printf '\n'
export MONGO_URI_ATLAS
./scripts/lab.sh ch02 --mode quick
```

Use the real URI with the database username and password substituted, including URL encoding for reserved password characters. Chapter 17 writes `college_ch17.chunks`, downloads the embedding model, creates a vector index, and also needs reachable Ollama for answer generation. FAISS-only results do not demonstrate Atlas retrieval.

The default app's Ollama service is internal to its own network. To share it with Chapter 17 locally, create an optional override:

```bash
cat > compose.local.yaml <<'YAML'
services:
  ollama:
    ports:
      - "127.0.0.1:11434:11434"
YAML
docker compose -f compose.yaml -f compose.local.yaml --profile model up -d --build
docker compose exec ollama ollama pull qwen2.5:1.5b
export OLLAMA_BASE_URL=http://host.docker.internal:11434
./scripts/lab.sh ch17 --activity 1 --mode quick
```

The `host.docker.internal` address is for containers reaching the Windows Docker host. This optional simultaneous setup needs more memory. Keep the override when restarting this service, and remove the temporary shell settings when finished:

```bash
unset MONGO_URI_ATLAS OLLAMA_BASE_URL
docker compose -f compose.yaml -f compose.local.yaml --profile model down
```

### Chapter 7 annual-report source

Set `ANNUAL_REPORTS_URL` to the instructor-confirmed source URL before launching Chapter 7. Do not substitute a guessed source and claim the requirement is complete. `REPORT_MIN_YEAR` defaults to 2025 in the Python code; to override it, explicitly pass it into the lab container:

```bash
read -rp 'Confirmed annual-report URL: ' ANNUAL_REPORTS_URL
export ANNUAL_REPORTS_URL
export REPORT_MIN_YEAR=2025
docker compose -p college-basic -f infra/standalone.yaml build lab
docker compose -p college-basic -f infra/standalone.yaml run --rm -e REPORT_MIN_YEAR lab ch07 --mode quick
```

### Chapters 12 and 13 secrets

Their launchers automatically generate local certificates, a password, and a replica-set key in `.secrets/`. Keep these files on the Linux filesystem. Keep them when restarting the associated database volumes; changing the password file without changing the database user causes authentication failures. Do not commit or share this directory.

For Chapter 13 exporter metrics, first complete the chapter, then run:

```bash
./scripts/exporter.sh
```

For Kubernetes, a separate configured cluster is required. Enable/configure a local cluster using [Docker Desktop's Kubernetes instructions](https://docs.docker.com/desktop/features/kubernetes/), and ensure `kubectl` works **inside Ubuntu**. A Windows-only installation or context is not sufficient for the Bash script. Follow the official [Linux kubectl installation instructions](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) if needed. Then check:

```bash
kubectl config current-context
kubectl cluster-info
kubectl get storageclass
```

Proceed only when the context is your intended local lab cluster and a default storage class is available:

```bash
./scripts/kubernetes.sh
```

This creates namespace `college-mongo`, three database pods and persistent storage, and deletes/recreates a pod to check persistence. It is a separate experiment; Compose success does not verify it. Delete only this lab namespace when finished and when its stored data is no longer needed:

```bash
kubectl delete namespace college-mongo
```

### Chapter 14 backup experiments

Run Chapter 14 first, then:

```bash
./scripts/pitr.sh
```

PITR means point-in-time recovery. The normal Chapter 14 snapshot test does not run this separate timestamp-recovery experiment.

To start the hourly backup service:

```bash
docker compose -p college-replica -f infra/replica.yaml -f infra/backup.yaml up -d backup
```

Leave Docker and Windows running for scheduled backups. Sleeping or shutting down the laptop interrupts the schedule. The service writes under `backups/ch14` and removes its snapshots older than seven days. Stop the full setup with both files:

```bash
docker compose -p college-replica -f infra/replica.yaml -f infra/backup.yaml --profile pitr down
```

### Chapter 18 public data

Quick mode uses three distinct bundled historical advisories. Full mode fetches public feeds and caches them at `data/public-threats.json`; it can be slow and requires internet on the first collection. Read [Chapter 18](../labs/ch18/README.md) before running it. The number actually collected is recorded; do not assume that every requested target size was achieved.

## 8. Find results and take screenshots

After a lab run, the printed container path `/work/results/ch16/<run-id>` corresponds to `results/ch16/<run-id>` in your repository. Files stay on the computer after the temporary lab container exits.

To open the results in Windows File Explorer, run in Ubuntu:

```bash
explorer.exe results
```

Each `result.json` records status, mode, elapsed time, and events. For example, inspect all Chapter 16 run files:

```bash
ls -lt results/ch16
```

Open the newest timestamp directory, then `result.json`. `passed` means the checks in that run completed; `partial` means an external part or known gap remains; `blocked` means a prerequisite was missing; `failed` means an exception or assertion stopped execution. Check launcher logs too: a supplemental script can fail after the chapter's JSON was written.

Take real screenshots with **Win+Shift+S**. Capture the browser demonstration, chapter command and outcome, and relevant results. Keep credentials and local secret files out of screenshots. Logs, database backups, and generated submission ZIPs are local artifacts ignored by Git; copying source to another machine does not copy its runtime evidence.

Optional local unit checks:

```bash
python3 -m unittest discover -s tests -v
```

These checks do not replace running the database services. Generate source submission archives separately with:

```bash
python3 scripts/package-chapters.py
```

The resulting `submissions/chapters` ZIPs are draft source packages; real screenshot documents and final reports must still be prepared.

## 9. Stop, restart, and update

Stop the web app while keeping its data and downloaded model:

```bash
docker compose --profile model down
```

Start it again after opening Docker Desktop:

```bash
cd ~/projects/NoSQL-Projects
docker compose --profile model up -d
```

If you changed source files, add `--build`. If you used `compose.local.yaml`, include both `-f` arguments when starting and stopping that setup.

Stop the lab topology you used with the matching command:

```bash
docker compose -p college-basic -f infra/standalone.yaml down
docker compose -p college-replica -f infra/replica.yaml --profile pitr down
docker compose -p college-shards -f infra/shards.yaml down
docker compose -p college-auth -f infra/auth.yaml down
docker compose -p college-secure -f infra/secure.yaml --profile exporter down
docker compose -p college-polyglot -f infra/polyglot.yaml down
```

If the backup service was started, use its two-file stop command from section 7. To see what remains running:

```bash
docker ps
```

Ordinary `down` keeps named volumes. **Adding `-v` deletes the named volumes**, including stored databases or the app's downloaded model, so avoid it during normal presentation cleanup. Services without named volumes, including the current polyglot fixtures, are recreated by the next lab run. The files in `results/` remain on disk.

To obtain repository updates, preserve your edits first, then run:

```bash
git status
git pull --ff-only
```

Rebuild the app with `./scripts/demo.sh`, or rerun the desired lab launcher. If Git reports conflicting local changes or diverging branches, resolve them before updating; do not discard your work blindly.

## 10. Troubleshooting

| Symptom | What to do |
|---|---|
| `./scripts/...` is not recognized | Open Ubuntu, then `cd ~/projects/NoSQL-Projects`. PowerShell does not run these Bash scripts directly. |
| `docker: command not found` | Start Docker Desktop, enable Ubuntu under WSL Integration, then reopen Ubuntu. |
| Cannot connect to Docker / socket permission denied | Check Docker Desktop is running and `docker version` shows Server. Check WSL integration before trying Linux service commands or installing another daemon. |
| WSL installation mentions virtualization | Enable virtualization in firmware or ask the machine administrator; use Microsoft's WSL troubleshooting guidance. |
| `Permission denied` running a script | Run `chmod +x scripts/*.sh infra/*.sh` from the repository root. Keep the checkout inside Ubuntu's home folder. |
| `bash\r`, `^M`, or “bad interpreter” | Files have Windows line endings. Run `sed -i 's/\r$//' scripts/*.sh infra/*.sh`. The repository's `.gitattributes` requests LF endings for text files. |
| Port 8000 already allocated | Close the program using it, or change the app mapping in `compose.yaml` to `127.0.0.1:8002:8000`, recreate the app, then browse `http://localhost:8002`. |
| Browser cannot reach the app | Check `docker compose --profile model ps`, then `docker compose logs --tail=100 app mongo`. Try `http://127.0.0.1:8000`. |
| Search works but chat fails | Check `/api/health`, `docker compose exec ollama ollama list`, and `docker compose logs --tail=100 ollama`. Retry the model pull. Verify that you have not changed `OLLAMA_BASE_URL` to an unreachable address. |
| Slow build / image pull failure | Check internet and free disk; rerun the same command. Docker reuses completed layers. Do not disable certificate verification to bypass a corporate proxy problem. |
| Cassandra/Neo4j timeout or container exit | Stop other topologies and the model, free memory, and inspect `docker compose -p college-polyglot -f infra/polyglot.yaml logs --tail=100 cassandra neo4j`. Then rerun Chapter 16. |
| Atlas blocked / connection failure | Verify the URI, database credentials, current IP access list, internet, and vector-search support for Chapter 17. Local success does not verify Atlas. |
| Chapter 17 FAISS training warning | Quick mode trains IVF on a small sample. A completed run still records its measurements; full mode uses more data. Do not treat quick recall measurements as production estimates. |
| Partition experiment interrupted | Run `docker compose -p college-replica -f infra/replica.yaml down`, then rerun Chapter 9. Do not add `-v`; the restart restores the Compose network. |
| Root-owned results cannot be edited | From the repository root run `sudo chown -R "$(id -u):$(id -g)" results` to take ownership of local evidence files. |

If the WSL/Docker integration remains stuck, save work, quit Docker Desktop, run `wsl --shutdown` in **PowerShell**, then start Docker Desktop and Ubuntu again. This stops all running WSL distributions, so use it only after saving other WSL work.

## 11. Final rehearsal checklist

- [ ] Install and build on the actual Windows presentation laptop.
- [ ] Confirm `docker version`, Compose, and `hello-world` work from Ubuntu.
- [ ] Start the app and open it from the Windows browser.
- [ ] Confirm search, filters, details, one generated answer, and its follow-up work.
- [ ] Confirm the model is downloaded before disconnecting internet.
- [ ] Run each chapter you intend to show, and inspect its saved result and launcher log.
- [ ] Prepare screenshots from real runs as a fallback.
- [ ] Stop unused topologies to free memory.
- [ ] Explain historical/classroom data and any skipped external activities accurately.
- [ ] Keep Docker Desktop running and prevent laptop sleep during the demonstration.

For activity details, see [labs/README.md](../labs/README.md). For verification limits, see [STATUS.md](../STATUS.md).
