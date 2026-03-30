terraform {
  required_version = ">= 1.9.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"   # picks the latest 5.x (currently 5.38 at 2026‑03‑26)
    }
  }
}