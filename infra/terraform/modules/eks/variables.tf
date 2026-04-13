variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the cluster will be created"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for the EKS cluster"
  type        = list(string)
}

# Cluster settings
variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "cluster_version" {
  description = "Kubernetes version"
  type        = string
}

variable "enable_control_plane_logging" {
  description = "Enable control plane logging to CloudWatch"
  type        = bool
  default     = false
}

# Node group settings
variable "node_group_name" {
  description = "Managed node group name"
  type        = string
}

variable "instance_types" {
  description = "Instance types for node group"
  type        = list(string)
}

variable "desired_size" {
  description = "Desired number of nodes"
  type        = number
}

variable "min_size" {
  description = "Minimum number of nodes"
  type        = number
}

variable "max_size" {
  description = "Maximum number of nodes"
  type        = number
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}
