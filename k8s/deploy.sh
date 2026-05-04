#!/bin/bash
# ============================================
# SCRIPT: deploy.sh
# PURPOSE: Deploy all e-commerce microservices to Kubernetes
# ============================================
# This script deploys resources in correct order:
# 1. Namespace
# 2. Secrets
# 3. ConfigMaps
# 4. Databases (with PVCs)
# 5. Microservices
# ============================================

set -e  # Exit on error

NAMESPACE="ecommerce"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Starting deployment of e-commerce microservices..."
echo "📁 Working directory: $SCRIPT_DIR"

# Step 1: Create namespace
echo "📦 Step 1/5: Creating namespace..."
kubectl apply -f namespace/namespace.yaml

# Wait for namespace to be ready
echo "⏳ Waiting for namespace to be ready..."
kubectl wait --for=condition=Active namespace/$NAMESPACE --timeout=60s

# Step 2: Create secrets
echo "🔐 Step 2/5: Creating secrets..."
kubectl apply -f secrets/ -n $NAMESPACE

# Step 3: Create configmaps
echo "⚙️  Step 3/5: Creating configmaps..."
kubectl apply -f configmaps/ -n $NAMESPACE

# Step 4: Deploy databases
echo "🗄️  Step 4/5: Deploying databases..."
kubectl apply -f databases/mongodb-pvc.yaml -n $NAMESPACE
kubectl apply -f databases/mongodb-deployment.yaml -n $NAMESPACE
kubectl apply -f databases/mongodb-service.yaml -n $NAMESPACE

kubectl apply -f databases/postgres-pvc.yaml -n $NAMESPACE
kubectl apply -f databases/postgres-deployment.yaml -n $NAMESPACE
kubectl apply -f databases/postgres-service.yaml -n $NAMESPACE

kubectl apply -f databases/redis-pvc.yaml -n $NAMESPACE
kubectl apply -f databases/redis-deployment.yaml -n $NAMESPACE
kubectl apply -f databases/redis-service.yaml -n $NAMESPACE

# Wait for database pods to be ready
echo "⏳ Waiting for databases to be ready..."
kubectl wait --for=condition=ready pod -l app=mongodb -n $NAMESPACE --timeout=120s
kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=120s
kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=60s

# Step 5: Deploy microservices
echo "🚀 Step 5/5: Deploying microservices..."
kubectl apply -f microservices/ -n $NAMESPACE

# Wait for microservices to be ready
echo "⏳ Waiting for microservices to be ready..."
kubectl wait --for=condition=ready pod -l app=product-catalog -n $NAMESPACE --timeout=120s
kubectl wait --for=condition=ready pod -l app=user-management -n $NAMESPACE --timeout=120s
kubectl wait --for=condition=ready pod -l app=checkout-service -n $NAMESPACE --timeout=120s

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Status:"
kubectl get pods -n $NAMESPACE
echo ""
echo "🔗 Services:"
kubectl get services -n $NAMESPACE
echo ""
echo "📝 To access services:"
echo "  kubectl port-forward svc/product-catalog 3000:3000 -n $NAMESPACE"
echo "  kubectl port-forward svc/user-management 8000:8000 -n $NAMESPACE"
echo "  kubectl port-forward svc/checkout-service 8001:8000 -n $NAMESPACE"
