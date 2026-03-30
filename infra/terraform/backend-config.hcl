# infra/terraform/backend-config.hcl
bucket       = "ecom-devops-tf-state-240e34a3"
key          = "terraform.tfstate"
region       = "us-east-1"
encrypt      = true
use_lockfile = true