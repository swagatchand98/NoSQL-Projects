# Prepared publishing commands — not executed

Keep the consolidated source repository private. Supply the actual GitHub repository and Docker Hub namespace in submission-metadata.json before generating final submission documents. Obtain explicit authorization before publishing or inviting faculty.

```bash
docker build -f Dockerfile.labs -t YOUR_NAMESPACE/college-mongo-labs:1.0.0 .
docker login
docker push YOUR_NAMESPACE/college-mongo-labs:1.0.0
LAB_IMAGE=YOUR_NAMESPACE/college-mongo-labs:1.0.0 docker compose -p college-basic -f infra/standalone.yaml -f infra/grading.yaml pull lab
LAB_IMAGE=YOUR_NAMESPACE/college-mongo-labs:1.0.0 docker compose -p college-basic -f infra/standalone.yaml -f infra/grading.yaml run --rm lab ch02 --mode quick
```

The image allowlist copies runnable labs, application code, seed data, dependency specifications and license/attribution only. It excludes the reference repository, private metadata, reports, credentials and outputs. Adapted GPL source remains in the runnable image with its license. Inspect image layers before public publication; no publication is authorized by these instructions alone.

Only after a clean pull-and-run should a submission say “published and tested.” Record image digest, actual Docker Hub URL, command and run evidence. Grading commands for other chapters use the corresponding topology plus infra/grading.yaml.
