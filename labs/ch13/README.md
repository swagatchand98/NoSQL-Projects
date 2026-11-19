# Chapter 13: Secure deployment

Keyfile replica set and driver failover, exporter, three-pod StatefulSet and explicit Kubernetes persistence/rejoin script.

```bash
./scripts/lab.sh ch13 --mode quick
./scripts/lab.sh ch13 --mode full
```

Expected observable behavior: labeled JSON events containing actual database results, counts and measurements. Failed assertions produce a failed result. Missing optional credentials are reported as partial, never successful external verification. Evidence: `results/ch13/<UTC-run-id>/result.json`, plus chapter-specific plots/explains/logs when applicable.

See [lab instructions](../README.md) for topology stop commands and supplementary activities. See `activity_*` folders for Python entrypoints. Full mode is required for the rubric's graded dataset sizes. This implementation has not yet been executed against live database services in the restricted development session.
