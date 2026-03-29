output "endpoint" {
  description = "Redis endpoint"
  value       = aws_elasticache_cluster.main.cache_nodes[0].address
}

output "cluster_id" {
  description = "ElastiCache cluster ID"
  value       = aws_elasticache_cluster.main.id
}

output "port" {
  description = "Redis port"
  value       = aws_elasticache_cluster.main.cache_nodes[0].port
}
