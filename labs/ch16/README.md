# Chapter 16: Polyglot persistence

Equivalent enrollment queries in three real engines; merged fraud investigation, pooled clients, independent breakers, mock and integration checks.

```bash
./scripts/lab.sh ch16 --mode quick
./scripts/lab.sh ch16 --mode full
```

Expected observable behavior: labeled JSON events containing actual database results, counts and measurements. Failed assertions produce a failed result. Missing optional credentials are reported as partial, never successful external verification. Evidence: `results/ch16/<UTC-run-id>/result.json`, plus chapter-specific plots/explains/logs when applicable.

See [lab instructions](../README.md) for topology stop commands and supplementary activities. See `activity_*` folders for Python entrypoints. Full mode is required for the rubric's graded dataset sizes. This implementation has not yet been executed against live database services in the restricted development session.
