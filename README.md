# ecom-devops
Demo e‑commerce platform to practice CI/CD, Kubernetes (EKS & EC2), Helm, ArgoCD, and observability.
## Architecture (placeholder)
```mermaid
graph LR
  U[User] --> I[Ingress]
  I --> C[Catalog Service]
  I --> Usvc[User Service]
  I --> Chk[Checkout Service]
  C & Usvc & Chk --> DB[(PostgreSQL – RDS)]
# test change
