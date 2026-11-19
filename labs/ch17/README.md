# Chapter 17: Vector retrieval

Real 384-dimensional embeddings and Atlas top-three RAG; local FAISS 5,000-vector/100-query HNSW/IVF measurements and plot.

```bash
./scripts/lab.sh ch17 --mode quick
./scripts/lab.sh ch17 --mode full
```

Expected observable behavior: labeled JSON events containing actual database results, counts and measurements. Failed assertions produce a failed result. Missing optional credentials are reported as partial, never successful external verification. Evidence: `results/ch17/<UTC-run-id>/result.json`, plus chapter-specific plots/explains/logs when applicable.

See [lab instructions](../README.md) for topology stop commands and supplementary activities. See `activity_*` folders for Python entrypoints. Full mode is required for the rubric's graded dataset sizes. This implementation has not yet been executed against live database services in the restricted development session.
