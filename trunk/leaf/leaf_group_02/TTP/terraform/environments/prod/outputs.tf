output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = module.rds.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = module.redis.endpoint
  sensitive   = true
}

output "s3_bucket_name" {
  description = "S3 bucket for texture assets"
  value       = module.s3.bucket_name
}

output "cloudfront_distribution_domain" {
  description = "CloudFront distribution domain"
  value       = module.s3.cloudfront_domain_name
}

output "load_balancer_dns" {
  description = "Application Load Balancer DNS name"
  value       = module.eks.load_balancer_dns
}
