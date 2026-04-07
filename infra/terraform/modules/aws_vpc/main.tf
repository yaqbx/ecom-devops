# --------------------------------------------------------------
# Discover AZs in the target region (required by subnets)
# --------------------------------------------------------------
data "aws_availability_zones" "available" {
  state = "available"
}

provider "aws" {
  region = var.region
}

# --------------------------------------------------------------
# --------------------------------------------------------------
# VPC
# --------------------------------------------------------------
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name        = "ecom-devops-vpc"
    Environment = "dev"
  }
}
# --------------------------------------------------------------
# Internet Gateway
# --------------------------------------------------------------
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "ecom-devops-igw"
  }
}
# --------------------------------------------------------------
# Public Subnets (one per AZ)
# --------------------------------------------------------------
resource "aws_subnet" "public" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  tags = {
    Name        = "ecom-devops-public-${count.index}"
    Tier        = "public"
    Environment = "dev"
  }
}
# --------------------------------------------------------------
# Private Subnets (one per AZ)
# --------------------------------------------------------------
resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags = {
    Name        = "ecom-devops-private-${count.index}"
    Tier        = "private"
    Environment = "dev"
  }
}
# --------------------------------------------------------------
# Elastic IPs for NAT Gateways (if enabled)
# --------------------------------------------------------------
resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? length(var.private_subnet_cidrs) : 0
  domain = "vpc"
  tags = {
    Name        = "ecom-devops-nat-eip-${count.index}"
    Environment = "dev"
  }
}
# --------------------------------------------------------------
# NAT Gateways (optional)
# --------------------------------------------------------------
resource "aws_nat_gateway" "nat" {
  count         = var.enable_nat_gateway ? length(var.private_subnet_cidrs) : 0
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  tags = {
    Name        = "ecom-devops-nat-${count.index}"
    Environment = "dev"
  }
}
# --------------------------------------------------------------
# Public Route Table & Route
# --------------------------------------------------------------
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "ecom-devops-public-rt"
  }
}
resource "aws_route" "public_internet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
}
resource "aws_route_table_association" "public_assoc" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}
# --------------------------------------------------------------
# Private Route Tables (with NAT) – created only if NAT enabled
# --------------------------------------------------------------
resource "aws_route_table" "private" {
  count  = var.enable_nat_gateway ? length(var.private_subnet_cidrs) : 0
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "ecom-devops-private-rt-${count.index}"
  }
}
resource "aws_route" "private_nat" {
  count                  = var.enable_nat_gateway ? length(var.private_subnet_cidrs) : 0
  route_table_id         = aws_route_table.private[count.index].id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.nat[count.index].id
  # Guarantees the NAT gateway exists before the route is created
  depends_on = [aws_nat_gateway.nat]
}
resource "aws_route_table_association" "private_assoc" {
  count          = var.enable_nat_gateway ? length(aws_subnet.private) : 0
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}
# --------------------------------------------------------------
# Default Security Group (deny‑all inbound, allow all outbound)
# --------------------------------------------------------------
resource "aws_security_group" "default" {
  name        = "ecom-devops-sg"
  description = "Default SG – no inbound, all outbound"
  vpc_id      = aws_vpc.main.id
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "ecom-devops-sg"
  }
}