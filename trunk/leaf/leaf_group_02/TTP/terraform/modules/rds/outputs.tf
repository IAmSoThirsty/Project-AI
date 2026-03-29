output "endpoint" {
  description = "RDS endpoint"
  value       = aws_db_instance.main.endpoint
}

output "instance_id" {
  description = "RDS instance ID"
  value       = aws_db_instance.main.id
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}

output "master_username" {
  description = "Master username"
  value       = aws_db_instance.main.username
  sensitive   = true
}
