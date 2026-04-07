variable "use_oidc" {
  description = "When true, use OIDC assume role"
  type        = bool
  default     = false
}

provider "aws" {
  region = var.aws_region

  dynamic "assume_role_with_web_identity" {
    for_each = var.use_oidc ? [1] : []
    content {
      role_arn = "arn:aws:iam::163841615263:role/terraform-github-role"
    }
  }
}
