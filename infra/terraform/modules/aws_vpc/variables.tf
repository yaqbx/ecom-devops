variable "region" {
  description = "AWS region"
  type        = string
}
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
}
variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets (one per AZ)"
  type        = list(string)
}
variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets (one per AZ)"
  type        = list(string)
}

variable "enable_nat_gateway" {
  description = "Create NAT gateways for private subnets"
  type        = bool
  default     = true
}