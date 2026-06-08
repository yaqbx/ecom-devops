module "vpc" {
  source               = "./modules/aws_vpc"
  region               = var.aws_region
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  enable_nat_gateway   = true
}

module "eks" {
  source             = "./modules/eks"
  aws_region         = var.aws_region
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids

  cluster_name                 = var.eks_cluster_name
  cluster_version              = var.eks_cluster_version
  node_group_name              = var.eks_node_group_name
  instance_types               = var.eks_instance_types
  desired_size                 = var.eks_desired_size
  min_size                     = var.eks_min_size
  max_size                     = var.eks_max_size
  enable_control_plane_logging = var.eks_enable_logging
  tags                         = var.eks_tags
}

module "ecr" {
  source = "./modules/ecr"
  tags = {
    Project     = "ecom-devops"
    Environment = "dev"
  }
}