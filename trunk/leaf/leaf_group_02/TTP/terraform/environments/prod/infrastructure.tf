module "vpc" {
  source = "../../modules/vpc"

  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
}

module "eks" {
  source = "../../modules/eks"

  project_name         = var.project_name
  environment          = var.environment
  cluster_version      = var.eks_cluster_version
  vpc_id               = module.vpc.vpc_id
  private_subnet_ids   = module.vpc.private_subnet_ids
  node_instance_types  = var.eks_node_instance_types
  node_desired_size    = var.eks_node_desired_size
  node_min_size        = var.eks_node_min_size
  node_max_size        = var.eks_node_max_size
}

module "rds" {
  source = "../../modules/rds"

  project_name        = var.project_name
  environment         = var.environment
  vpc_id              = module.vpc.vpc_id
  subnet_ids          = module.vpc.database_subnet_ids
  instance_class      = var.rds_instance_class
  allocated_storage   = var.rds_allocated_storage
  multi_az            = var.rds_multi_az
  allowed_cidr_blocks = module.vpc.private_subnet_cidrs
}

module "redis" {
  source = "../../modules/redis"

  project_name        = var.project_name
  environment         = var.environment
  vpc_id              = module.vpc.vpc_id
  subnet_ids          = module.vpc.private_subnet_ids
  node_type           = var.redis_node_type
  num_cache_nodes     = var.redis_num_cache_nodes
  allowed_cidr_blocks = module.vpc.private_subnet_cidrs
}

module "s3" {
  source = "../../modules/s3"

  project_name = var.project_name
  environment  = var.environment
  domain_name  = var.domain_name
}

module "monitoring" {
  source = "../../modules/monitoring"

  project_name       = var.project_name
  environment        = var.environment
  eks_cluster_name   = module.eks.cluster_name
  rds_instance_id    = module.rds.instance_id
  redis_cluster_id   = module.redis.cluster_id
}
