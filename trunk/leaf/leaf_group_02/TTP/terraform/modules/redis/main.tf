resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-redis-subnet-group"
  subnet_ids = var.subnet_ids

  tags = {
    Name = "${var.project_name}-${var.environment}-redis-subnet-group"
  }
}

resource "aws_security_group" "redis" {
  name        = "${var.project_name}-${var.environment}-redis-sg"
  description = "Security group for ElastiCache Redis"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "Redis from private subnets"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-redis-sg"
  }
}

resource "aws_elasticache_cluster" "main" {
  cluster_id           = "${var.project_name}-${var.environment}-redis"
  engine               = "redis"
  engine_version       = "7.1"
  node_type            = var.node_type
  num_cache_nodes      = var.num_cache_nodes
  parameter_group_name = aws_elasticache_parameter_group.main.name
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]

  port = 6379

  snapshot_retention_limit = 5
  snapshot_window          = "03:00-05:00"
  maintenance_window       = "sun:05:00-sun:07:00"

  tags = {
    Name = "${var.project_name}-${var.environment}-redis"
  }
}

resource "aws_elasticache_parameter_group" "main" {
  name   = "${var.project_name}-${var.environment}-redis-params"
  family = "redis7"

  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }

  parameter {
    name  = "timeout"
    value = "300"
  }
}
