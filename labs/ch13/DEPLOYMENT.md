# Compose and Kubernetes comparison

Compose uses service DNS and named volumes on one Docker host. The secure topology has three data-bearing members, one generated shared keyfile, and TLS certificates signed for its actual service names. The exporter uses a separate clusterMonitor/read-local account.

Kubernetes uses a headless Service for stable member names, a three-pod StatefulSet, and one PVC per member. An init container copies the same generated Secret keyfile into an emptyDir and sets ownership 999:999 and mode 400. Initialization uses the localhost exception before creating the admin account. The verification script writes with w=3, recreates mongo-2, checks its changed pod UID, reads its persisted value, and prints replica membership. The Kubernetes exercise uses keyfile authentication; TLS is demonstrated in the separate Compose security exercise.

A working cluster and storage class are external prerequisites. No Kubernetes persistence result is inferred from YAML validation. Terraform is reference-only because the chapter's assigned activities are Compose and StatefulSet deployment.
