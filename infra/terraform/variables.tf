variable "aws_region" {
  description = "AWS region where the VPC will be created"
  type        = string
  default     = "eu-north-1" # change if you work in a different region
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets (one per AZ)"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets (one per AZ)"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}


# EKS Cluster Configuration
variable "eks_cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "ecom-devops-eks"
}
variable "eks_cluster_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.35"
}
variable "eks_node_group_name" {
  description = "Name of the managed node group"
  type        = string
  default     = "ecom-devops-ng"
}
variable "eks_instance_types" {
  description = "Instance types for the node group"
  type        = list(string)
  default     = ["t3.small"]
}
variable "eks_desired_size" {
  description = "Desired number of nodes"
  type        = number
  default     = 3
}
variable "eks_min_size" {
  description = "Minimum number of nodes"
  type        = number
  default     = 1
}
variable "eks_max_size" {
  description = "Maximum number of nodes"
  type        = number
  default     = 3
}
variable "eks_enable_logging" {
  description = "Enable control plane logging (Costs extra)"
  type        = bool
  default     = false
}
variable "eks_tags" {
  description = "Tags for EKS resources"
  type        = map(string)
  default     = {}
}