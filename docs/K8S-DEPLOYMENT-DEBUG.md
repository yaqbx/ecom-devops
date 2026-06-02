# K8s Deployment & Debugging Guide

## Node Sizing: Pod Limits per Instance Type

Amazon EKS enforces a maximum pod count per node based on the instance type's ENI limits.

### Formula
```
max_pods = (number_of_network_interfaces × (number_of_IPv4_addresses_per_interface - 1)) + 2
```

### Common Limits

| Instance | vCPU | RAM (GiB) | Max Pods |
|----------|------|-----------|----------|
| t3.micro | 2 | 1 | 4 |
| t3.small | 2 | 2 | 8 |
| t3.medium | 2 | 4 | 17 |
| t3.large | 2 | 8 | 35 |
| t2.micro | 1 | 1 | 4 |

### Our Setup (t3.micro)

9 pods on a single t3.micro → impossible (limit 4). Solutions:
1. **Scale replicas down** → 1 replica per service = 6 pods + overlaps with node limit
2. **Add more nodes** → increase `desired_size` in node group scaling config
3. **Upgrade instance type** → t3.small supports 8 pods (still tight), t3.medium supports 17

## Common Deployment Issues & Fixes

### 1. Image Name — ECR vs Docker Hub

**Problem**: Deployments reference short image names (`product-catalog:latest`) which K8s tries to pull from Docker Hub instead of ECR.

**Error**:
```
Failed to pull image "checkout-service:latest": pull access denied, repository does not exist
```

**Fix**: Use full ECR URI with specific tag:
```yaml
# ❌ Wrong
image: checkout-service:latest

# ✅ Correct
image: 163841615263.dkr.ecr.eu-north-1.amazonaws.com/checkout-service:v1.0.0-xxxxxx
```

### 2. ImagePullBackOff / ErrImagePull

**Diagnosis**:
```bash
kubectl describe pod -n ecommerce <pod-name> | grep -A 10 Events
```

**Common causes**:
- Wrong image name (see above)
- Tag doesn't exist in ECR
- Node doesn't have ECR pull permissions (should work with EKS managed node IAM role)
- `imagePullPolicy: Always` when image tag is `latest` (uses cache miss logic)

**Verify image exists in ECR**:
```bash
aws ecr list-images --repository-name checkout-service --region eu-north-1
```

### 3. Pod Scheduling — Pending

**Diagnosis**:
```bash
kubectl describe pod -n ecommerce <pod-name> | grep -A 5 "Events:"
```

**Common cause**: `0/1 nodes are available: 1 Too many pods. preemption: 0/1 nodes are available: 1 No preemption victims found for incoming pod.`

**Resolution**: Scale out nodes or down replicas.

### 4. Nodes Not Ready

```bash
# Check node status
kubectl get nodes

# Describe problematic node
kubectl describe node <node-name>
```

### 5. PVC Pending / Storage Issues

```bash
# Check PVC status
kubectl get pvc -n ecommerce

# Check StorageClass
kubectl get storageclass
```

## Session Debugging Walkthrough

### Problem: All 9 pods stuck in Pending

1. Checked node count:
   ```bash
   kubectl get nodes
   # → 1 node (t3.micro)
   ```

2. Checked pod events:
   ```bash
   kubectl describe pod -n ecommerce product-catalog-<hash>
   # → "0/1 nodes are available: 1 Too many pods"
   ```

3. Identified root cause: t3.micro supports max 4 pods → 9 pods won't fit

4. Scaled node group from 1 to 2 nodes via Terraform:
   ```
   eks_desired_size = 2  # was 1
   ```

5. After 2nd node joined, pods started scheduling but one hit `ImagePullBackOff`

6. Identified root cause #2: deployments used short image names (`checkout-service:latest`) → K8s tried Docker Hub, not ECR

7. Fixed all 3 deployment files with full ECR URIs:
   ```
   163841615263.dkr.ecr.eu-north-1.amazonaws.com/<service>:v1.0.0-abca63e
   ```

8. Applied changes and pods began pulling from ECR successfully.

### Quick Diagnostic Checklist

```bash
# 1. Nodes available
kubectl get nodes

# 2. Pod status
kubectl get pods -n ecommerce -o wide

# 3. Pod events (scheduling errors)
kubectl describe pod -n ecommerce <pending-pod> | grep -A 10 Events

# 4. Image pull errors
kubectl describe pod -n ecommerce <imagepullbackoff-pod> | grep -E "Events:|Failed|Error"

# 5. Node pod capacity
kubectl describe node <node-name> | grep -E "pods|Capacity"

# 6. ECR image tags
aws ecr list-images --repository-name <service> --region eu-north-1

# 7. Node group scaling config
aws eks describe-nodegroup --cluster-name ecom-devops-eks --nodegroup-name ecom-devops-ng --region eu-north-1 --query "nodegroup.scalingConfig"

# 8. Live pod/node watch
kubectl get pods -n ecommerce -w
kubectl get nodes -w
```

### Useful Alias

```bash
alias kp='kubectl get pods -n ecommerce -o wide'
alias kd='kubectl describe pod -n ecommerce'
alias kn='kubectl get nodes -o wide'
alias kl='kubectl logs -n ecommerce'
```
