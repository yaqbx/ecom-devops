# GitOps with Helm & ArgoCD

## What GitOps Is

Git is the **single source of truth**. Cluster state always matches what's in Git. No manual `kubectl apply`. No SSH into servers.

**Flow**: Push to Git → ArgoCD sees change → syncs to cluster automatically.

---

## Helm — Package Kubernetes

Raw YAML manifests are hard to manage. Helm bundles them into reusable **charts** with templates and configurable values.

### Instead of this (current):

```
k8s/
├── microservices/
│   ├── product-catalog-deployment.yaml
│   ├── checkout-service-deployment.yaml
│   └── user-management-deployment.yaml
├── databases/
│   ├── mongodb-statefulset.yaml
│   ├── postgres-statefulset.yaml
│   └── redis-statefulset.yaml
├── configmaps/
├── secrets/
└── namespace/
```

### You have this (Helm):

```
charts/
├── microservice/          # Reusable chart template
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── templates/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   └── _helpers.tpl
├── database/              # Reusable chart for DBs
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── statefulset.yaml
│       ├── pvc.yaml
│       └── service.yaml

helmfiles/                 # Values per service
├── product-catalog.yaml   # image tag, replicas, resources
├── checkout-service.yaml
├── user-management.yaml
├── mongodb.yaml
├── postgres.yaml
└── redis.yaml
```

Now changing replica count = edit a values file → commit → ArgoCD picks it up.

---

## ArgoCD — Auto Sync

ArgoCD runs in the cluster and watches a Git repo. When Git changes, it syncs.

```
┌─────────────┐     push      ┌──────────┐
│   Developer  │ ──────────→  │   Git    │
│   (Git push) │              │  (main)  │
└─────────────┘              └────┬─────┘
                                  │ poll / webhook
                                  ▼
                           ┌──────────┐
                           │  ArgoCD  │
                           │ (in EKS) │
                           └────┬─────┘
                                │ sync
                                ▼
                           ┌──────────┐
                           │  EKS     │
                           │ cluster  │
                           └──────────┘
```

### Key ArgoCD concepts

| Concept | Meaning |
|---------|---------|
| **Application** | A deployed service (maps to one Helm chart + values) |
| **Project** | Group of apps with RBAC rules |
| **Sync** | Make cluster match Git |
| **Auto-sync** | Syncs automatically when Git changes |
| **Prune** | Deletes resources removed from Git |
| **Rollback** | Revert sync to a previous Git commit |

---

## For This Project

### Repository structure

```
ecom-devops/
├── infra/
│   └── terraform/         # VPC, EKS, ECR, IAM
├── apps/                   # Source code
│   ├── product-catalog/
│   ├── checkout-service/
│   └── user-management/
├── charts/                 # Helm charts
│   ├── microservice/
│   └── database/
├── argocd/                 # ArgoCD config
│   ├── projects/
│   └── applications/
└── helmfiles/              # Per-service values
    ├── product-catalog.yaml
    ├── checkout-service.yaml
    ├── user-management.yaml
    ├── mongodb.yaml
    ├── postgres.yaml
    └── redis.yaml
```

### Typical workflow

1. Dev changes code → pushes to Git
2. CI builds Docker image → pushes to ECR
3. CI updates image tag in `helmfiles/product-catalog.yaml`
4. Dev commits and pushes that change
5. ArgoCD detects drift → syncs new image to cluster
6. Rollout happens (Helm upgrade, rolling update)

### Changing replicas

```
# Edit helmfiles/product-catalog.yaml
replicas: 3

# Commit and push
git add helmfiles/product-catalog.yaml
git commit -m "scale product-catalog to 3 replicas"
git push

# ArgoCD syncs automatically (or manually via UI)
```

No `kubectl scale`, no `helm upgrade` on CLI. Just Git.

---

## When to Add This

| Now | Later | When Ready |
|-----|-------|------------|
| Raw YAML + kubectl | Helm charts | ArgoCD |
| Manual apply | Template-ize configs | Auto-sync, rollbacks |
| Fine for dev | Cleaner, reusable | Production-grade |

## Example Files in This Repo

### Helm chart — `charts/microservice/`
```
charts/microservice/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default values
└── templates/
    ├── _helpers.tpl         # Helper templates (labels, names)
    ├── deployment.yaml      # Deployment resource
    ├── service.yaml         # ClusterIP Service
    ├── configmap.yaml       # Optional ConfigMap
    └── secret.yaml          # Optional Secret
```

Deploy with Helm directly (for testing):
```bash
helm install product-catalog charts/microservice \
  --values helmfiles/product-catalog.yaml \
  --namespace ecommerce
```

### Helm chart — `charts/database/`
Same pattern, but includes **StatefulSet** with `volumeClaimTemplates` for persistent storage.

### Values files — `helmfiles/`
Each microservice and database has its own values file:
```
helmfiles/product-catalog.yaml    # image: 163841615263.dkr.ecr.../product-catalog:v1.0.0-abca63e
helmfiles/checkout-service.yaml   # replicas: 2
helmfiles/user-management.yaml    # resources, env vars
helmfiles/mongodb.yaml            # mongo:7.0, 1Gi storage
helmfiles/postgres.yaml           # postgres:16, 1Gi storage
helmfiles/redis.yaml              # redis:7-alpine, 512Mi storage
```

### ArgoCD config — `argocd/`
```
argocd/
├── project.yaml                          # AppProject definition
└── applications/
    ├── product-catalog.yaml              # Points to charts/microservice + values
    ├── checkout-service.yaml
    ├── user-management.yaml
    ├── mongodb.yaml                      # Points to charts/database + values
    ├── postgres.yaml
    └── redis.yaml
```

Each Application YAML:
```yaml
source:
  path: charts/microservice          # or charts/database
  helm:
    valueFiles:
      - ../../helmfiles/product-catalog.yaml
syncPolicy:
  automated:
    prune: true        # Delete resources removed from Git
    selfHeal: true     # Revert manual changes to match Git
```

---

## One-line Summary

**Helm** = package K8s configs. **ArgoCD** = deploy automatically from Git. **No more kubectl apply**.
