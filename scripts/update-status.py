from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
lines=['# Implementation and verification status','','Implemented means runnable source exists; it does not mean the exercise passed on real services. No database/model/election/benchmark outcome has been fabricated.','','| Activity | Implementation | Command | Evidence | Blocker |','|---|---|---|---|---|']
lines.append('| Mini project | Implemented; static checks only | `./scripts/demo.sh` | `results/project/checkpoint.json` | Docker/model runtime verification |')
for i in range(1,19):
 chapter=f'ch{i:02}'
 results=sorted((root/'results'/chapter).glob('*/result.json'))
 latest=results[-1] if results else None
 result=json.loads(latest.read_text()) if latest else {}
 blocker=result.get('error') or 'Live services not verified'
 if i==1:blocker+='; two extension definitions missing'
 if i==7:blocker+='; CTI Digest metadata and assigned annual-report source unverified'
 if i==16:blocker+='; enrollment queries use explicitly provisional defaults'
 evidence=str(latest.relative_to(root)) if latest else 'No runtime result'
 lines.append(f'| Chapter {i:02}: base activities and extensions where identified | Implemented; runtime {result.get("status","not run")} | `./scripts/lab.sh {chapter} --mode quick` | `{evidence}` | {blocker} |')
lines.extend(['| Unit/static checks | Locally verified | `python3 scripts/verify-labs.py` | `results/verification/checks.json` | No live integration claim |','| Chapter source ZIPs | Generated drafts | `python3 scripts/package-chapters.py` | `submissions/chapters/` | Real screenshots and final listing DOCX pending |','| Private GitHub / Docker Hub | Prepared only | See `scripts/publish-instructions.md` | No publication evidence | Account destination and authorization |','| Kubernetes / Atlas | Source and commands supplied | See chapter READMEs | No successful external evidence | Cluster/credentials/network |','','## Exact faculty-reference gaps','','Pinned reference: `7898bc8907937941a0e2af152654e28f5860bcb4`.','','- Chapter 1 has two base activities; the two requested extensions are not identified.','- Chapter 3 has no submission format in its README.','- Chapter 4 says five bulk operations but contains four; the fifth reviewed-flag update is labeled provisional.','- Chapter 7 does not identify an exact annual-security-reports URL. Its CTI Digest page was only a client-rendered shell during inspection; the supplied dump uses attributed Ubuntu metadata instead and labels this gap.','- Chapter 16 uses fraud examples, not the three requested university enrollment queries. The student/course/instructor queries are provisional.','- Chapter 17 native IVF is not documented in the inspected Atlas API; the local FAISS substitution is explicitly labeled.','','## Checkpoint','','`checkpoints/all-chapters-source.tar.gz` contains runnable source and documentation. Git metadata in this workspace is read-only and is not a valid repository, so a commit could not be made.'])
(root/'STATUS.md').write_text('\n'.join(lines)+'\n')
