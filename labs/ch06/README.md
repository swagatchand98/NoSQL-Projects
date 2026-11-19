# Chapter 6: Indexes

50,000 products and five query plans; actual index usage; 10,000-insert comparison; retained critical index and covered explain.

```bash
./scripts/lab.sh ch06 --mode quick
./scripts/lab.sh ch06 --mode full
```

Expected observable behavior: labeled JSON events containing actual database results, counts and measurements. Failed assertions produce a failed result. Missing optional credentials are reported as partial, never successful external verification. Evidence: `results/ch06/<UTC-run-id>/result.json`, plus chapter-specific plots/explains/logs when applicable.

See [lab instructions](../README.md) for topology stop commands and supplementary activities. See `activity_*` folders for Python entrypoints. Full mode is required for the rubric's graded dataset sizes. This implementation has not yet been executed against live database services in the restricted development session.
