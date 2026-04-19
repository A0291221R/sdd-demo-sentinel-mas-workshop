variable "environment" {
  description = "Deployment environment name (e.g. dev, prod)."
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region for all resources."
  type        = string
  default     = "ap-southeast-1"
}

variable "db_password" {
  description = "Master password for the RDS PostgreSQL instance."
  type        = string
  sensitive   = true
}

variable "domain_name" {
  description = "Domain name for the ACM certificate and ALB HTTPS listener (e.g. sentinel-dev.example.com)."
  type        = string
}

variable "github_repo" {
  description = "GitHub repository for OIDC trust (owner/name format, e.g. A0291221R/sdd-demo-sentinel-mas-workshop)."
  type        = string
  default     = "A0291221R/sdd-demo-sentinel-mas-workshop"
}
