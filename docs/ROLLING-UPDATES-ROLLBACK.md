# Rolling Updates & Rollback

## Rolling Update

When you update a Deployment (new image, env vars, config), Kubernetes replaces pods **gradually**, not all at once.

```
Before:  [v1] [v1] [v1] [v1]    ← all on old version
Step 1:  [v1] [v1] [v1] [v2]    ← 1 new pod created
Step 2:  [v1] [v1] [v2] [v2]    ← another old killed, new created
Step 3:  [v1] [v2] [v2] [v2]
After:   [v2] [v2] [v2] [v2]    ← all on new version
```

Controlled by two settings:

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1         # max extra pods above desired count
      maxUnavailable: 0   # never go below desired count
```

**Safety check**: a new pod must pass its **readiness probe** before the rollout continues to the next pod. If the new pod fails, the rollout pauses.

## If Update Fails

### Rollout pauses automatically

New pod fails readiness check → Kubernetes stops rolling:

```
[pod-v1] [pod-v1] [pod-v1] [pod-v2-FAILING]
                                   ↑
                    Rollout paused, v1 keeps serving traffic
```

Old pods keep running and handling requests. No downtime.

### Check status

```bash
kubectl rollout status deployment/product-catalog -n ecommerce
kubectl rollout history deployment/product-catalog -n ecommerce
```

### Rollback manually

```bash
kubectl rollout undo deployment/product-catalog -n ecommerce
```

This reverts to the **previous ReplicaSet** (old version). Traffic goes back to old pods immediately.

### Rollback to specific revision

```bash
kubectl rollout undo deployment/product-catalog -n ecommerce --to-revision=1
```

## Real Scenario for Your Stack

```
1. You push buggy code → CI builds image → pushes to ECR
2. CI updates helmfiles/product-catalog.yaml with new tag → pushes to Git
3. ArgoCD detects change → syncs → starts rolling update
4. New pod starts → crashes or fails /health endpoint
5. Rollout pauses automatically → old pods still serve traffic
6. You check logs to diagnose
7. Fix code → push again → new rolling update replaces the bad pods
   Or: kubectl rollout undo → revert immediately
```

**No downtime** throughout the entire process. Old pods handle traffic until new ones prove healthy.

## ArgoCD Rollback

- **Sync**: deploys whatever is currently in Git
- **Rollback**: ArgoCD UI lets you select a previous sync and redeploy it
- ArgoCD does not auto-rollback on failure — it reports the sync as "OutOfSync" and waits for you to fix Git or press rollback

## Key Commands

```bash
# Watch rollout
kubectl rollout status deployment/product-catalog -n ecommerce

# History
kubectl rollout history deployment/product-catalog -n ecommerce

# Undo (rollback to previous)
kubectl rollout undo deployment/product-catalog -n ecommerce

# Pause/resume
kubectl rollout pause deployment/product-catalog -n ecommerce
kubectl rollout resume deployment/product-catalog -n ecommerce

# Restart (no change, just re-deploy same spec)
kubectl rollout restart deployment/product-catalog -n ecommerce
```

## Summary

- Rolling update = gradual replacement, pod by pod
- Failed probe = rollout pauses, not aborts
- Old pods stay up → no downtime
- `k rollout undo` to go back
