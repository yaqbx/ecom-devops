# Python Scripts for YOUR E-Commerce Project

## Project Structure:
```
/home/ljakubowski/Nauka-ecom-devops/ecom-devops/
├── apps/
│   ├── checkout-service/
│   ├── frontend/
│   ├── payment-mock/
│   ├── product-catalog/
│   └── user-management/
├── .github/workflows/
│   ├── build.yml
│   ├── terraform.yml
│   └── terraform-destroy.yml
├── infra/terraform/
├── k8s/
└── charts/
```

## Services:
1. product-catalog
2. user-management
3. checkout-service
4. frontend
5. payment-mock

---

## Script 1: Docker Builder (10 min)
**File**: `scripts/docker_builder.py`

```python
#!/usr/bin/env python3
"""Build and push Docker images for e-commerce microservices"""

import subprocess
import os
from pathlib import Path

# Your project configuration
ECR_REGISTRY = "163841615263.dkr.ecr.eu-north-1.amazonaws.com"
SERVICES = [
    "product-catalog",
    "user-management",
    "checkout-service",
    "frontend",
    "payment-mock"
]

class DockerBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
    
    def build_service(self, service: str, tag: str) -> bool:
        """Build Docker image for a service"""
        app_path = self.project_root / "apps" / service
        
        if not app_path.exists():
            print(f"❌ Service directory not found: {app_path}")
            return False
        
        print(f"🔨 Building {service}:{tag}...")
        
        # Build image
        cmd = f"docker build -t {service}:{tag} {app_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Build failed: {result.stderr}")
            return False
        
        # Tag for ECR
        ecr_image = f"{ECR_REGISTRY}/{service}:{tag}"
        cmd = f"docker tag {service}:{tag} {ecr_image}"
        subprocess.run(cmd, shell=True, check=True)
        
        print(f"✅ Built: {ecr_image}")
        return True
    
    def push_service(self, service: str, tag: str) -> bool:
        """Push image to ECR"""
        ecr_image = f"{ECR_REGISTRY}/{service}:{tag}"
        
        print(f"📤 Pushing {ecr_image}...")
        
        # Login to ECR
        login_cmd = "aws ecr get-login-password | docker login --username AWS --password-stdin"
        subprocess.run(f"{login_cmd} {ECR_REGISTRY}", shell=True, check=True)
        
        # Push
        cmd = f"docker push {ecr_image}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Push failed: {result.stderr}")
            return False
        
        print(f"✅ Pushed: {ecr_image}")
        return True
    
    def build_all(self, tag: str, push: bool = False):
        """Build all services"""
        print(f"🚀 Building all services with tag: {tag}\n")
        
        success_count = 0
        
        for service in SERVICES:
            if self.build_service(service, tag):
                success_count += 1
                if push:
                    self.push_service(service, tag)
        
        print(f"\n{'='*50}")
        print(f"✅ Built: {success_count}/{len(SERVICES)} services")
        
        return success_count == len(SERVICES)
    
    def build_from_apps(self, app_dir: str, tag: str):
        """Build from apps directory structure"""
        apps_path = self.project_root / "apps"
        
        for service in SERVICES:
            service_path = apps_path / service
            if service_path.exists():
                self.build_service(service, tag)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Docker Builder for E-Commerce')
    parser.add_argument('--tag', default='latest', help='Image tag')
    parser.add_argument('--push', action='store_true', help='Push to ECR')
    parser.add_argument('--service', help='Build specific service')
    
    args = parser.parse_args()
    
    builder = DockerBuilder()
    
    if args.service:
        builder.build_service(args.service, args.tag)
        if args.push:
            builder.push_service(args.service, args.tag)
    else:
        builder.build_all(args.tag, args.push)
```

**Usage:**
```bash
# Build all services
python scripts/docker_builder.py --tag v1.0.0

# Build and push
python scripts/docker_builder.py --tag v1.0.0 --push

# Build specific service
python scripts/docker_builder.py --service product-catalog --tag v1.0.0
```

---

## Script 2: Terraform Plan Parser (10 min)
**File**: `scripts/terraform_parser.py`

```python
#!/usr/bin/env python3
"""Parse terraform plan output for e-commerce infrastructure"""

import subprocess
import json
import re
from typing import Dict, List

class TerraformParser:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.terraform_dir = self.project_root / "infra" / "terraform"
    
    def run_plan(self) -> str:
        """Run terraform plan and capture output"""
        cmd = f"terraform -chdir={self.terraform_dir} plan -no-color"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout
    
    def parse_plan(self, plan_output: str) -> Dict:
        """Parse terraform plan output"""
        changes = {
            'add': [],
            'change': [],
            'destroy': []
        }
        
        lines = plan_output.split('\n')
        
        for line in lines:
            # Parse resource additions
            if 'will be created' in line:
                resource = self._extract_resource(line)
                if resource:
                    changes['add'].append(resource)
            
            # Parse resource changes
            elif 'will be updated' in line or 'will be updated in-place' in line:
                resource = self._extract_resource(line)
                if resource:
                    changes['change'].append(resource)
            
            # Parse resource destruction
            elif 'will be destroyed' in line:
                resource = self._extract_resource(line)
                if resource:
                    changes['destroy'].append(resource)
        
        return changes
    
    def _extract_resource(self, line: str) -> Dict:
        """Extract resource information from plan line"""
        # Try to extract resource address
        match = re.search(r'# (\S+)', line)
        if match:
            address = match.group(1)
            parts = address.split('.')
            return {
                'address': address,
                'type': parts[0] if len(parts) > 0 else 'unknown',
                'name': parts[1] if len(parts) > 1 else 'unknown'
            }
        return None
    
    def summary(self, changes: Dict) -> str:
        """Generate summary of terraform changes"""
        total = len(changes['add']) + len(changes['change']) + len(changes['destroy'])
        
        summary = f"📊 Terraform Plan Summary\n"
        summary += f"{'='*50}\n"
        summary += f"Total changes: {total}\n\n"
        
        if changes['add']:
            summary += f"✅ Resources to add: {len(changes['add'])}\n"
            for r in changes['add']:
                summary += f"  + {r['address']}\n"
        
        if changes['change']:
            summary += f"\n🔄 Resources to update: {len(changes['change'])}\n"
            for r in changes['change']:
                summary += f"  ~ {r['address']}\n"
        
        if changes['destroy']:
            summary += f"\n❌ Resources to destroy: {len(changes['destroy'])}\n"
            for r in changes['destroy']:
                summary += f"  - {r['address']}\n"
        
        # Check for EKS resources
        eks_resources = [r for r in changes['add'] + changes['change'] + changes['destroy'] 
                        if 'eks' in r.get('address', '').lower()]
        
        if eks_resources:
            summary += f"\n⚠️  EKS Cluster Changes: {len(eks_resources)}\n"
            for r in eks_resources:
                summary += f"  ! {r['address']}\n"
        
        return summary
    
    def has_destructive_changes(self, changes: Dict) -> bool:
        """Check if plan has destructive changes"""
        return len(changes['destroy']) > 0
    
    def analyze(self) -> str:
        """Run full analysis"""
        print("🔍 Running terraform plan...")
        plan_output = self.run_plan()
        
        print("📝 Parsing plan output...")
        changes = self.parse_plan(plan_output)
        
        return self.summary(changes)

if __name__ == "__main__":
    from pathlib import Path
    
    parser = TerraformParser()
    summary = parser.analyze()
    print(summary)
    
    if parser.has_destructive_changes(parser.parse_plan(parser.run_plan())):
        print("\n⚠️  WARNING: Destructive changes detected!")
        print("Consider reviewing before applying.")
```

**Usage:**
```bash
# Analyze terraform plan
python scripts/terraform_parser.py

# In GitHub Actions
- name: Parse terraform plan
  run: python scripts/terraform_parser.py
```

---

## Script 3: Deployment Checker (10 min)
**File**: `scripts/deployment_checker.py`

```python
#!/usr/bin/env python3
"""Check deployment status for e-commerce microservices"""

import subprocess
import json
from typing import Dict, List

# Your services
SERVICES = [
    "product-catalog",
    "user-management",
    "checkout-service",
    "frontend",
    "payment-mock"
]

class DeploymentChecker:
    def __init__(self, namespace: str = "ecommerce"):
        self.namespace = namespace
    
    def get_pod_status(self) -> List[Dict]:
        """Get status of all pods"""
        cmd = f"kubectl get pods -n {self.namespace} -o json"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to get pods: {result.stderr}")
            return []
        
        pods = json.loads(result.stdout)
        
        status_list = []
        for pod in pods['items']:
            status_list.append({
                'name': pod['metadata']['name'],
                'status': pod['status']['phase'],
                'ready': self._is_pod_ready(pod)
            })
        
        return status_list
    
    def _is_pod_ready(self, pod: Dict) -> bool:
        """Check if pod is ready"""
        conditions = pod['status'].get('conditions', [])
        for condition in conditions:
            if condition['type'] == 'Ready' and condition['status'] == 'True':
                return True
        return False
    
    def get_deployment_status(self) -> Dict:
        """Get deployment status for all services"""
        statuses = {}
        
        for service in SERVICES:
            cmd = f"kubectl get deployment {service} -n {self.namespace} -o json"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                deployment = json.loads(result.stdout)
                statuses[service] = {
                    'replicas': deployment['status'].get('replicas', 0),
                    'ready': deployment['status'].get('readyReplicas', 0),
                    'available': deployment['status'].get('availableReplicas', 0)
                }
            else:
                statuses[service] = {'error': 'not found'}
        
        return statuses
    
    def check_health(self) -> str:
        """Check overall health of deployment"""
        statuses = self.get_deployment_status()
        
        report = f"🏥 Health Check: {self.namespace}\n"
        report += f"{'='*50}\n"
        
        all_healthy = True
        
        for service in SERVICES:
            status = statuses.get(service, {'error': 'not found'})
            
            if 'error' in status:
                report += f"❌ {service}: {status['error']}\n"
                all_healthy = False
            elif status['ready'] == status['replicas']:
                report += f"✅ {service}: {status['ready']}/{status['replicas']} ready\n"
            else:
                report += f"⚠️  {service}: {status['ready']}/{status['replicas']} ready\n"
                all_healthy = False
        
        report += f"\nOverall: {'✅ Healthy' if all_healthy else '❌ Issues detected'}"
        
        return report
    
    def wait_for_deployment(self, timeout: int = 300) -> bool:
        """Wait for all deployments to be ready"""
        import time
        
        start = time.time()
        
        while time.time() - start < timeout:
            statuses = self.get_deployment_status()
            
            all_ready = all(
                status.get('ready', 0) == status.get('replicas', 0)
                for status in statuses.values()
                if 'error' not in status
            )
            
            if all_ready:
                print(f"✅ All deployments ready in {self.namespace}")
                return True
            
            elapsed = int(time.time() - start)
            print(f"⏳ Waiting for deployments... ({elapsed}s)")
            time.sleep(10)
        
        print(f"❌ Timeout waiting for deployments")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Deployment Checker')
    parser.add_argument('--namespace', default='ecommerce', help='Kubernetes namespace')
    parser.add_argument('--wait', action='store_true', help='Wait for deployment')
    parser.add_argument('--timeout', type=int, default=300, help='Timeout in seconds')
    
    args = parser.parse_args()
    
    checker = DeploymentChecker(args.namespace)
    
    if args.wait:
        checker.wait_for_deployment(args.timeout)
    else:
        print(checker.check_health())
```

**Usage:**
```bash
# Check deployment status
python scripts/deployment_checker.py

# Wait for deployment
python scripts/deployment_checker.py --wait --timeout 300

# Check specific namespace
python scripts/deployment_checker.py --namespace staging
```

---

## Script 4: Rollback Manager (10 min)
**File**: `scripts/rollback_manager.py`

```python
#!/usr/bin/env python3
"""Manage rollbacks for e-commerce microservices"""

import subprocess
import json
from datetime import datetime

# Your services
SERVICES = [
    "product-catalog",
    "user-management",
    "checkout-service",
    "frontend",
    "payment-mock"
]

class RollbackManager:
    def __init__(self, namespace: str = "ecommerce"):
        self.namespace = namespace
    
    def get_revision_history(self, service: str) -> list:
        """Get revision history for a service"""
        cmd = f"kubectl rollout history deployment/{service} -n {self.namespace}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        revisions = []
        for line in result.stdout.split('\n')[1:]:  # Skip header
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    revisions.append({
                        'revision': parts[0],
                        'timestamp': parts[1],
                        'description': ' '.join(parts[2:]) if len(parts) > 2 else ''
                    })
        
        return revisions
    
    def rollback(self, service: str, revision: int = None) -> bool:
        """Rollback a service to previous or specific revision"""
        if revision:
            cmd = f"kubectl rollout undo deployment/{service} --to-revision={revision} -n {self.namespace}"
        else:
            cmd = f"kubectl rollout undo deployment/{service} -n {self.namespace}"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Rolled back {service} to revision {revision or 'previous'}")
            return True
        else:
            print(f"❌ Rollback failed for {service}: {result.stderr}")
            return False
    
    def rollback_all(self, revision: int = None) -> dict:
        """Rollback all services"""
        results = {}
        
        for service in SERVICES:
            results[service] = self.rollback(service, revision)
        
        return results
    
    def create_backup(self) -> str:
        """Create backup of current deployment state"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        backup = {}
        for service in SERVICES:
            cmd = f"kubectl get deployment {service} -n {self.namespace} -o json"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                backup[service] = json.loads(result.stdout)
        
        # Save to file
        filename = f"backup-{self.namespace}-{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(backup, f, indent=2)
        
        print(f"✅ Backup created: {filename}")
        return filename
    
    def show_history(self):
        """Show revision history for all services"""
        print(f"📜 Revision History: {self.namespace}\n")
        
        for service in SERVICES:
            revisions = self.get_revision_history(service)
            print(f"📦 {service}:")
            
            if revisions:
                for rev in revisions[-3:]:  # Show last 3
                    print(f"  Rev {rev['revision']}: {rev['timestamp']}")
            else:
                print("  No history found")
            
            print()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Rollback Manager')
    parser.add_argument('--namespace', default='ecommerce', help='Kubernetes namespace')
    parser.add_argument('--action', choices=['backup', 'history', 'rollback', 'rollback-all'], 
                       required=True, help='Action to perform')
    parser.add_argument('--service', help='Specific service for rollback')
    parser.add_argument('--revision', type=int, help='Specific revision to rollback to')
    
    args = parser.parse_args()
    
    manager = RollbackManager(args.namespace)
    
    if args.action == 'backup':
        manager.create_backup()
    
    elif args.action == 'history':
        manager.show_history()
    
    elif args.action == 'rollback':
        if args.service:
            manager.rollback(args.service, args.revision)
        else:
            print("❌ Please specify --service for rollback")
    
    elif args.action == 'rollback-all':
        manager.rollback_all(args.revision)
```

**Usage:**
```bash
# Create backup
python scripts/rollback_manager.py --action backup

# Show history
python scripts/rollback_manager.py --action history

# Rollback specific service
python scripts/rollback_manager.py --action rollback --service product-catalog

# Rollback all services
python scripts/rollback_manager.py --action rollback-all
```

---

## Script 5: Health Checker (10 min)
**File**: `scripts/health_checker.py`

```python
#!/usr/bin/env python3
"""Check health endpoints for e-commerce services"""

import requests
import time
from typing import Dict, List

# Your service endpoints (after deployment)
SERVICE_ENDPOINTS = {
    'product-catalog': '/health',
    'user-management': '/health',
    'checkout-service': '/health',
    'frontend': '/',
    'payment-mock': '/health'
}

class HealthChecker:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def check_endpoint(self, service: str, path: str, timeout: int = 5) -> Dict:
        """Check a health endpoint"""
        url = f"{self.base_url}{path}"
        
        try:
            response = requests.get(url, timeout=timeout)
            return {
                'service': service,
                'url': url,
                'status': response.status_code,
                'healthy': response.status_code == 200,
                'response_time': response.elapsed.total_seconds()
            }
        except requests.exceptions.RequestException as e:
            return {
                'service': service,
                'url': url,
                'status': 'error',
                'healthy': False,
                'error': str(e)
            }
    
    def check_all(self) -> str:
        """Check all service endpoints"""
        report = "🏥 Health Check Report\n"
        report += f"{'='*50}\n"
        report += f"Base URL: {self.base_url}\n\n"
        
        all_healthy = True
        
        for service, path in SERVICE_ENDPOINTS.items():
            result = self.check_endpoint(service, path)
            
            if result['healthy']:
                report += f"✅ {service}: {result['status']} ({result['response_time']:.2f}s)\n"
            else:
                report += f"❌ {service}: {result.get('error', result['status'])}\n"
                all_healthy = False
        
        report += f"\nOverall: {'✅ All healthy' if all_healthy else '❌ Issues detected'}"
        
        return report
    
    def wait_for_healthy(self, timeout: int = 60) -> bool:
        """Wait for all endpoints to be healthy"""
        start = time.time()
        
        while time.time() - start < timeout:
            all_healthy = True
            
            for service, path in SERVICE_ENDPOINTS.items():
                result = self.check_endpoint(service, path)
                if not result['healthy']:
                    all_healthy = False
                    break
            
            if all_healthy:
                print("✅ All endpoints healthy")
                return True
            
            elapsed = int(time.time() - start)
            print(f"⏳ Waiting for health... ({elapsed}s)")
            time.sleep(5)
        
        print("❌ Timeout waiting for health")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Health Checker')
    parser.add_argument('--url', default='http://localhost', help='Base URL')
    parser.add_argument('--wait', action='store_true', help='Wait for healthy')
    parser.add_argument('--timeout', type=int, default=60, help='Timeout in seconds')
    
    args = parser.parse_args()
    
    checker = HealthChecker(args.url)
    
    if args.wait:
        checker.wait_for_healthy(args.timeout)
    else:
        print(checker.check_all())
```

**Usage:**
```bash
# Check health endpoints
python scripts/health_checker.py --url http://localhost

# Wait for healthy
python scripts/health_checker.py --url http://localhost --wait --timeout 60
```

---

## Script 6: Config Generator (10 min)
**File**: `scripts/config_generator.py`

```python
#!/usr/bin/env python3
"""Generate environment-specific configurations"""

import yaml
from pathlib import Path

class ConfigGenerator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
    
    def generate_k8s_config(self, environment: str) -> dict:
        """Generate Kubernetes config for environment"""
        configs = {
            'dev': {
                'replicas': 1,
                'cpu_limit': '100m',
                'memory_limit': '128Mi'
            },
            'staging': {
                'replicas': 2,
                'cpu_limit': '200m',
                'memory_limit': '256Mi'
            },
            'production': {
                'replicas': 3,
                'cpu_limit': '500m',
                'memory_limit': '512Mi'
            }
        }
        
        return configs.get(environment, configs['dev'])
    
    def generate_helm_values(self, environment: str, tag: str) -> dict:
        """Generate Helm values file for environment"""
        config = self.generate_k8s_config(environment)
        
        return {
            'replicaCount': config['replicas'],
            'image': {
                'repository': f"163841615263.dkr.ecr.eu-north-1.amazonaws.com",
                'tag': f"{environment}-{tag}"
            },
            'resources': {
                'limits': {
                    'cpu': config['cpu_limit'],
                    'memory': config['memory_limit']
                }
            }
        }
    
    def save_helm_values(self, environment: str, tag: str):
        """Save Helm values file"""
        values = self.generate_helm_values(environment, tag)
        
        filename = f"values-{environment}.yaml"
        with open(filename, 'w') as f:
            yaml.dump(values, f, default_flow_style=False)
        
        print(f"✅ Generated: {filename}")
        return filename
    
    def generate_all_configs(self, tag: str):
        """Generate configs for all environments"""
        for env in ['dev', 'staging', 'production']:
            self.save_helm_values(env, tag)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Config Generator')
    parser.add_argument('--environment', default='dev', help='Environment')
    parser.add_argument('--tag', default='latest', help='Image tag')
    parser.add_argument('--all', action='store_true', help='Generate all environments')
    
    args = parser.parse_args()
    
    generator = ConfigGenerator()
    
    if args.all:
        generator.generate_all_configs(args.tag)
    else:
        generator.save_helm_values(args.environment, args.tag)
```

**Usage:**
```bash
# Generate dev config
python scripts/config_generator.py --environment dev --tag v1.0.0

# Generate all configs
python scripts/config_generator.py --tag v1.0.0 --all
```

---

## How to Use in Your Pipelines:

### GitHub Actions Integration:
```yaml
# In build.yml
- name: Build using Python script
  run: python scripts/docker_builder.py --tag ${{ steps.sha.outputs.short_sha }} --push

# In terraform.yml
- name: Parse terraform plan
  run: python scripts/terraform_parser.py

# After deployment
- name: Check deployment health
  run: python scripts/deployment_checker.py --wait --timeout 300
```

### Create scripts directory:
```bash
cd /home/ljakubowski/Nauka-ecom-devops/ecom-devops
mkdir scripts
# Add all scripts here
```

---

## Interview Stories:

1. **Docker Builder**: "I created a Python script that automates Docker image building for 5 microservices with ECR integration."

2. **Terraform Parser**: "I built a terraform plan parser that summarizes changes and flags destructive operations."

3. **Deployment Checker**: "I developed a deployment checker that monitors all services and reports health status."

4. **Rollback Manager**: "I created a rollback tool that can quickly revert deployments across all services."

5. **Config Generator**: "I built a config generator that creates environment-specific Helm values."

---

## Summary:

| Script | Time | Purpose |
|--------|------|---------|
| Docker Builder | 10 min | Build/push images |
| Terraform Parser | 10 min | Parse plan output |
| Deployment Checker | 10 min | Check deployment health |
| Rollback Manager | 10 min | Manage rollbacks |
| Health Checker | 10 min | Verify endpoints |
| Config Generator | 10 min | Generate configs |

**Total: ~1 hour to create all scripts**
