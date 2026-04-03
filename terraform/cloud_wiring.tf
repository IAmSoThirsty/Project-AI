# Project-AI Sovereign Infrastructure
# Terraform Manifest for Enterprise Maturity (Phase 1)
# Features: Cryptographic Audit Triggers & Sovereign Lifecycle Governance

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
  
  default_tags {
    tags = {
      Project     = "Project-AI"
      Sovereignty = "100%"
      Governance  = "Thirsty-Lang-Family"
    }
  }
}

variable "region" {
  type    = string
  default = "us-east-1"
}

# 2. Sovereign Audit Log Storage (S3 with Object Lock)
resource "aws_s3_bucket" "sovereign_audit_logs" {
  bucket = "project-ai-sovereign-audit-logs-${data.aws_caller_identity.current.account_id}"

  force_destroy = false
}

resource "aws_s3_bucket_versioning" "audit_versioning" {
  bucket = aws_s3_bucket.sovereign_audit_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Cryptographically enforce immutability at the infrastructure layer
resource "aws_s3_bucket_object_lock_configuration" "audit_lock" {
  bucket = aws_s3_bucket.sovereign_audit_logs.id

  rule {
    default_retention {
      mode = "COMPLIANCE"
      days = 2555 # 7 Years (Enterprise Standard)
    }
  }
}

# 3. Enterprise Event Stream (CloudTrail)
resource "aws_cloudtrail" "sovereign_trail" {
  name                          = "project-ai-sovereign-trail"
  s3_bucket_name                = aws_s3_bucket.sovereign_audit_logs.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true # Integrity checks
  
  kms_key_id = aws_kms_key.sovereign_master_key.arn
}

# 4. Threat Detection (GuardDuty)
resource "aws_guardduty_detector" "sovereign_detector" {
  enable = true
}

# 5. IAM Boundary (Sovereign Rails)
resource "aws_iam_policy" "sovereign_boundary" {
  name        = "ProjectAISovereignBoundary"
  description = "IAM Boundary for Project-AI agents"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:*", "kms:*", "logs:*"]
        Resource = "*"
      },
      {
        Effect   = "Deny"
        Action   = ["iam:DeletePolicy", "iam:DeleteRole"]
        Resource = "*"
      }
    ]
  })
}

# 6. Key Management with Sovereign Control
resource "aws_kms_key" "sovereign_master_key" {
  description             = "Project-AI Sovereign Master Key for Thirsty-Lang Family"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow Thirsty Runtime Access"
        Effect = "Allow"
        Principal = {
          Service = ["lambda.amazonaws.com", "cloudtrail.amazonaws.com"]
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:GenerateDataKey",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })
}

data "aws_caller_identity" "current" {}

output "audit_bucket_arn" {
  value = aws_s3_bucket.sovereign_audit_logs.arn
}

output "kms_key_arn" {
  value = aws_kms_key.sovereign_master_key.arn
}

output "cloudtrail_arn" {
  value = aws_cloudtrail.sovereign_trail.arn
}
