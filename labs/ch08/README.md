# Chapter 8: Replica sets

Three data-bearing members, write verification, observed failover, priority prediction versus observation; separate arbiter topology.

```bash
./scripts/lab.sh ch08 --mode quick
./scripts/lab.sh ch08 --mode full
```

Expected observable behavior: labeled JSON events containing actual database results, counts and measurements. Failed assertions produce a failed result. Missing optional credentials are reported as partial, never successful external verification. Evidence: `results/ch08/<UTC-run-id>/result.json`, plus chapter-specific plots/explains/logs when applicable.

See [lab instructions](../README.md) for topology stop commands and supplementary activities. See `activity_*` folders for Python entrypoints. Full mode is required for the rubric's graded dataset sizes. This implementation has not yet been executed against live database services in the restricted development session.
