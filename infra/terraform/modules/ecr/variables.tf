variable "tags" {
  description = "Tags to apply to ECR repositories"
  type        = map(string)
  default     = {
    Project    = "ecom-devops"
    ManagedBy  = "terraform"
  }
}
variable "region" {
  description = "AWS region"
  type        = string
  default     = "eu-north-1"
}