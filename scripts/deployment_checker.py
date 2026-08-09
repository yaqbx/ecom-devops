#!/usr/bin/env python3
"""Check deployment status for e-commerce microservices"""

import subprocess
import json
from typing import Dict, List

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
        cmd = f"kubectl get pods -n {self.namespace} -o json"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Failed to get pods: {result.stderr}")
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
        conditions = pod['status'].get('conditions', [])
        for condition in conditions:
            if condition['type'] == 'Ready' and condition['status'] == 'True':
                return True
        return False

    def get_deployment_status(self) -> Dict:
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
        statuses = self.get_deployment_status()

        report = f"Health Check: {self.namespace}\n"
        report += f"{'='*50}\n"

        all_healthy = True

        for service in SERVICES:
            status = statuses.get(service, {'error': 'not found'})

            if 'error' in status:
                report += f"X {service}: {status['error']}\n"
                all_healthy = False
            elif status['ready'] == status['replicas']:
                report += f"OK {service}: {status['ready']}/{status['replicas']} ready\n"
            else:
                report += f"!! {service}: {status['ready']}/{status['replicas']} ready\n"
                all_healthy = False

        report += f"\nOverall: {'Healthy' if all_healthy else 'Issues detected'}"

        return report

    def wait_for_deployment(self, timeout: int = 300) -> bool:
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
                print(f"All deployments ready in {self.namespace}")
                return True

            elapsed = int(time.time() - start)
            print(f"Waiting for deployments... ({elapsed}s)")
            time.sleep(10)

        print(f"Timeout waiting for deployments")
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
