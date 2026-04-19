variable "environment" {
  type = string
}

variable "sqs_queue_arn" {
  description = "ARN of the SQS task queue (used in task role policies)."
  type        = string
}

variable "github_repo" {
  description = "GitHub repository in 'owner/name' format for OIDC trust (e.g. A0291221R/sdd-demo-sentinel-mas-workshop)."
  type        = string
}

variable "create_oidc_provider" {
  description = "Set to false if the GitHub OIDC provider already exists in this AWS account to avoid EntityAlreadyExists error."
  type        = bool
  default     = true
}

variable "oidc_provider_arn" {
  description = "ARN of an existing GitHub OIDC provider. Only required when create_oidc_provider = false."
  type        = string
  default     = ""
}
