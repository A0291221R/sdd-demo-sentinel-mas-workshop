variable "environment" {
  type    = string
  default = "prod"
}

variable "aws_region" {
  type    = string
  default = "ap-southeast-1"
}

variable "db_password" {
  description = "Master password for the RDS PostgreSQL instance."
  type        = string
  sensitive   = true
}

variable "domain_name" {
  description = "Domain name for the ACM certificate and ALB HTTPS listener."
  type        = string
}

variable "github_repo" {
  description = "GitHub repository for OIDC trust (owner/name format)."
  type        = string
  default     = "A0291221R/sdd-demo-sentinel-mas-workshop"
}

variable "create_oidc_provider" {
  description = "Whether to create the GitHub Actions OIDC provider. Set false when already created by dev."
  type        = bool
  default     = false
}

variable "oidc_provider_arn" {
  description = "ARN of existing OIDC provider when create_oidc_provider is false."
  type        = string
  default     = ""
}

variable "certificate_arn" {
  description = "ARN of a pre-existing validated ACM certificate for the HTTPS listener."
  type        = string
  default     = ""
}
