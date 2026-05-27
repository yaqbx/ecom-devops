# Security Scanning in GitOps Pipeline

## Where Scanning Happens

All scanning runs in **GitHub Actions** during CI — before the image is pushed to ECR. ArgoCD does not scan. It only deploys what's already been verified.

```
Push → CI (GH Actions)
  ├── 1. Code & dependency scan
  ├── 2. Docker image scan
  ├── 3. Build & push to ECR (only if scans pass)
  └── 4. Update helmfile with new tag → push to Git
                           ↓
                    ArgoCD syncs to cluster
```

## Scanners

### Dependency scanning
**Python**: `pip-audit` or `safety` — checks `requirements.txt` against known CVE databases. Fails if a library has a known vulnerability.

**Node.js**: `npm audit` — checks `package.json` lockfile for vulnerable packages. Built into npm, no extra install needed.

### Docker image scanning
**Trivy** (Aqua Security) — scans the built image for OS-level CVEs (Ubuntu packages, system libraries). One tool, covers both file system deps and container layers. Free and open-source.

### Code security analysis
**Bandit** (Python) — finds common security issues in Python code: hardcoded passwords, SQL injection patterns, unsafe `eval()` calls.

**Semgrep** — generic rule-based scanner. Works for Python, Node.js, any language. Catches logic-level bugs that dependency scanners miss.

### Secret leak detection
**Gitleaks** or **trufflehog** — scans the entire Git history for accidentally committed secrets (API keys, passwords, tokens). Runs on every push to prevent secrets from ever reaching the repo.

## Pipeline Flow Per Service

```yaml
# Simplified CI steps
steps:
  - checkout code
  - install dependencies
  - run npm audit / pip-audit     # → fail if CVEs found
  - build Docker image
  - run trivy on image             # → fail if CRITICAL/HIGH
  - push image to ECR
  - update helmfile with new tag
  - commit and push to Git
```

## What Does NOT Change

- **No scanners in ArgoCD** — ArgoCD deploys, it does not scan
- **No scanners in the cluster** — scanning happens before anything reaches production
- **No secrets in Git** — all secrets stay in AWS Secrets Manager, fetched by External Secrets Operator
- **No extra infra** — Trivy, npm audit, pip-audit all run as part of GH Actions, no servers needed

## Key Takeaway

Every push gets scanned before it reaches ECR, and nothing gets deployed to the cluster without passing all checks. ArgoCD only ever sees images that have already been verified clean.
