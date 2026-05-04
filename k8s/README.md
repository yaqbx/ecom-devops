# Kubernetes Deployment Manifests - E-Commerce Platform

## 📚 Overview

This directory contains all Kubernetes manifests needed to deploy the e-commerce microservices platform to Kubernetes (EKS).

### Architecture

```
Namespace: ecommerce
├── Databases
│   ├── MongoDB (Product Catalog)
│   ├── PostgreSQL (User Management)
│   └── Redis (Checkout Cache)
├── Microservices
│   ├── Product Catalog (Node.js) - 2 replicas
│   ├── User Management (Django) - 2 replicas
│   └── Checkout Service (FastAPI) - 2 replicas
└── Configuration
    ├── ConfigMaps (non-sensitive config)
    └── Secrets (sensitive data)
```

## 📁 Directory Structure

```
k8s/
├── namespace/           # Namespace definition
├── databases/          # Database deployments and services
│   ├── mongodb-*.yaml
│   ├── postgres-*.yaml
│   └── redis-*.yaml
├── microservices/      # Microservice deployments
│   ├── product-catalog-*
│   ├── user-management-*
│   └── checkout-service-*
├── configmaps/         # Configuration files
├── secrets/           # Sensitive configuration
├── deploy.sh          # Deployment script
└── README.md          # This file
```

## 🚀 Quick Start

### Prerequisites

1. Kubernetes cluster (EKS, minikube, kind, etc.)
2. kubectl configured with cluster access
3. Docker images built and available

### Deploy Everything

```bash
# Navigate to k8s directory
cd k8s

# Run deployment script
./deploy.sh
```

### Manual Deployment

```bash
# 1. Create namespace
kubectl apply -f namespace/namespace.yaml

# 2. Create secrets
kubectl apply -f secrets/ -n ecommerce

# 3. Create configmaps
kubectl apply -f configmaps/ -n ecommerce

# 4. Deploy databases
kubectl apply -f databases/ -n ecommerce

# 5. Deploy microservices
kubectl apply -f microservices/ -n ecommerce
```

## 🔍 Verify Deployment

```bash
# Check all pods
kubectl get pods -n ecommerce

# Check all services
kubectl get services -n ecommerce

# Check deployments
kubectl get deployments -n ecommerce

# View logs
kubectl logs -f deployment/product-catalog -n ecommerce
```

## 🔗 Access Services

### Using Port-Forward (Recommended for Testing)

```bash
# Product Catalog (Node.js)
kubectl port-forward svc/product-catalog 3000:3000 -n ecommerce
# Access: http://localhost:3000

# User Management (Django)
kubectl port-forward svc/user-management 8000:8000 -n ecommerce
# Access: http://localhost:8000

# Checkout Service (FastAPI)
kubectl port-forward svc/checkout-service 8001:8000 -n ecommerce
# Access: http://localhost:8001
```

### Using Cluster DNS (Internal)

```bash
# From within the cluster:
# - Product Catalog: product-catalog.ecommerce.svc.cluster.local:3000
# - User Management: user-management.ecommerce.svc.cluster.local:8000
# - Checkout: checkout-service.ecommerce.svc.cluster.local:8000
```

## 🗑️ Cleanup

### Delete Everything

```bash
kubectl delete namespace ecommerce
```

### Delete Individual Components

```bash
# Delete microservices
kubectl delete -f microservices/ -n ecommerce

# Delete databases
kubectl delete -f databases/ -n ecommerce

# Delete namespace (removes everything)
kubectl delete namespace ecommerce
```

## 📊 Resource Allocation

| Component | Replicas | CPU Request | Memory Request | Total Memory |
|-----------|----------|-------------|----------------|--------------|
| Product Catalog | 2 | 0.1 | 128Mi | 256Mi |
| User Management | 2 | 0.2 | 256Mi | 512Mi |
| Checkout Service | 2 | 0.1 | 128Mi | 256Mi |
| MongoDB | 1 | 0.25 | 256Mi | 256Mi |
| PostgreSQL | 1 | 0.25 | 256Mi | 256Mi |
| Redis | 1 | 0.1 | 128Mi | 128Mi |
| **TOTAL** | **9** | **1.1** | **1152Mi** | **~1.6GB** |

## 🔐 Security Notes

### Secrets

- Secrets are Base64 encoded (NOT encrypted by default!)
- For production:
  - Enable encryption at rest
  - Use external secret manager (AWS Secrets Manager, Vault)
  - Apply RBAC to limit access

### Network Policies

- By default, pods can communicate freely within namespace
- For production: apply NetworkPolicies to restrict traffic
- Example: Only microservices can access databases

## 📝 Configuration

### Environment Variables

Each microservice has its own ConfigMap:

- `product-catalog-config`: MongoDB URI
- `user-management-config`: Database URL, Redis URL
- `checkout-service-config`: Redis configuration

### Updating Configuration

```bash
# Edit ConfigMap
kubectl edit configmap product-catalog-config -n ecommerce

# Restart deployment to apply changes
kubectl rollout restart deployment/product-catalog -n ecommerce
```

## 🐛 Troubleshooting

### Pod Won't Start

```bash
# Check pod status
kubectl get pods -n ecommerce

# View pod details
kubectl describe pod <pod-name> -n ecommerce

# View logs
kubectl logs <pod-name> -n ecommerce
```

### Database Connection Issues

```bash
# Check database pods
kubectl get pods -l app=mongodb -n ecommerce

# Test connection from another pod
kubectl run test --rm -it --image=busybox --namespace=ecommerce -- sh
# Then: wget product-catalog:3000/health
```

### Resource Issues

```bash
# Check node resources
kubectl top nodes

# Check pod resources
kubectl top pods -n ecommerce
```

## 📚 Learning Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Kubernetes Concepts](https://kubernetes.io/docs/concepts/)

## 🎯 Next Steps

1. **Test locally**: Use minikube or kind for local testing
2. **Add monitoring**: Deploy Prometheus + Grafana
3. **Add logging**: Deploy Loki + Promtail
4. **Add ingress**: Expose services externally
5. **Add HPA**: Auto-scale based on CPU/memory
6. **Production readiness**: Add PodDisruptionBudget, PDB, etc.
