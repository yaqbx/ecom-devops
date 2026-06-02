# EKS Access Entries Debugging Guide

## Scenario: kubectl returns Forbidden after associating AdminPolicy

### Step 1: Check EKS cluster auth mode
```bash
aws eks describe-cluster --name ecom-devops-eks --region eu-north-1 \
  --query "cluster.accessConfig.authenticationMode" --output text
```
**Expected**: `API_AND_CONFIG_MAP` or `API`

### Step 2: Create access entry for your IAM principal
```bash
IAM_ARN=$(aws sts get-caller-identity --query 'Arn' --output text)

aws eks create-access-entry \
  --cluster-name ecom-devops-eks \
  --principal-arn $IAM_ARN \
  --region eu-north-1 \
  --type STANDARD
```
Creates an access entry — without this, `associate-access-policy` fails with `ResourceNotFoundException`.

### Step 3: Associate an access policy
```bash
aws eks associate-access-policy \
  --cluster-name ecom-devops-eks \
  --principal-arn $IAM_ARN \
  --access-scope type=cluster \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy \
  --region eu-north-1
```

**⚠️ Important**: `--access-scope` requires `type=` prefix (e.g., `type=cluster`, not bare `cluster`).  
**⚠️ Policy choice matters**:

| Policy | Scope | Can list nodes? |
|--------|-------|-----------------|
| `AmazonEKSAdminPolicy` | cluster | ❌ Forbidden |
| `AmazonEKSClusterAdminPolicy` | cluster | ✅ Yes |

### Step 4: Verify access
```bash
kubectl get nodes -o wide
```

### Step 5 (if still failing): Debug access entries
```bash
# List all access entries
aws eks list-access-entries --cluster-name ecom-devops-eks --region eu-north-1

# List associated policies for your principal
aws eks list-associated-access-policies \
  --cluster-name ecom-devops-eks \
  --principal-arn $IAM_ARN \
  --region eu-north-1

# Describe the access entry details
aws eks describe-access-entry \
  --cluster-name ecom-devops-eks \
  --principal-arn $IAM_ARN \
  --region eu-north-1
```

### Step 6 (if policy is wrong): Swap policies
```bash
# Disassociate wrong policy
aws eks disassociate-access-policy \
  --cluster-name ecom-devops-eks \
  --principal-arn $IAM_ARN \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSAdminPolicy \
  --region eu-north-1

# Associate correct policy
aws eks associate-access-policy \
  --cluster-name ecom-devops-eks \
  --principal-arn $IAM_ARN \
  --access-scope type=cluster \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy \
  --region eu-north-1
```

### Step 7 (full reset): Delete and recreate access entry
```bash
aws eks delete-access-entry \
  --cluster-name ecom-devops-eks \
  --principal-arn $IAM_ARN \
  --region eu-north-1

# Recreate
aws eks create-access-entry \
  --cluster-name ecom-devops-eks \
  --principal-arn $IAM_ARN \
  --region eu-north-1 \
  --type STANDARD

# Associate cluster-admin
aws eks associate-access-policy \
  --cluster-name ecom-devops-eks \
  --principal-arn $IAM_ARN \
  --access-scope type=cluster \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy \
  --region eu-north-1
```

### Key takeaways
1. Always use `type=cluster` syntax for `--access-scope`
2. `AmazonEKSClusterAdminPolicy` is required for cluster-wide admin (list nodes, etc.)
3. `AmazonEKSAdminPolicy` is namespace-scoped even with `type=cluster` — insufficient for `kubectl get nodes`
4. Access entry must exist before associating a policy
