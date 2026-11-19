# Chapter 18: Threat comparison

Attributed public ingestion with honest counts; MongoDB/Cassandra/Neo4j schemas; ten-repeat medians, candidates and comparative report.

```bash
./scripts/lab.sh ch18 --mode quick
./scripts/lab.sh ch18 --mode full
```

Expected observable behavior: labeled JSON events containing actual database results, counts and measurements. Failed assertions produce a failed result. Missing optional credentials are reported as partial, never successful external verification. Evidence: `results/ch18/<UTC-run-id>/result.json`, plus chapter-specific plots/explains/logs when applicable.

See [lab instructions](../README.md) for topology stop commands and supplementary activities. See `activity_*` folders for Python entrypoints. Full mode is required for the rubric's graded dataset sizes. This implementation has not yet been executed against live database services in the restricted development session.
