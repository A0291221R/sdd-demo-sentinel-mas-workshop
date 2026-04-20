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

variable "create_oidc_provider" {
  description = "Set false if the GitHub OIDC provider already exists in this AWS account."
  type        = bool
  default     = false
}

variable "oidc_provider_arn" {
  description = "ARN of the existing OIDC provider when create_oidc_provider is false."
  type        = string
  default     = ""
}

variable "certificate_arn" {
  description = "ARN of a pre-existing validated ACM certificate. When set, no new ACM cert is created."
  type        = string
  default     = ""
}
