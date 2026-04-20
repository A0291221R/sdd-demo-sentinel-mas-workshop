variable "environment" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "app_sg_id" {
  type = string
}

variable "execution_role_arn" {
  type = string
}

variable "api_task_role_arn" {
  type = string
}

variable "central_task_role_arn" {
  type = string
}

variable "queue_url" {
  type = string
}

variable "api_tg_arn_blue" {
  description = "ARN of the blue API target group — required by CODE_DEPLOY controller on first service creation."
  type        = string
}

variable "ui_target_group_arn" {
  description = "ARN of the UI target group for ALB routing."
  type        = string
}

variable "db_url_secret_arn" {
  description = "ARN of the Secrets Manager secret holding the DATABASE_URL value."
  type        = string
}

variable "anthropic_api_key_secret_arn" {
  description = "ARN of the Secrets Manager secret holding the ANTHROPIC_API_KEY value."
  type        = string
  default     = ""
}

variable "sqs_queue_url_secret_arn" {
  description = "ARN of the Secrets Manager secret holding the SQS queue URL. When set, QUEUE_URL is injected as a secret instead of a plaintext env var."
  type        = string
  default     = ""
}

variable "desired_count" {
  description = "Initial desired task count for api and central services."
  type        = number
  default     = 1
}

variable "enable_autoscaling" {
  description = "Whether to register Application Auto Scaling for ECS services. Set true in prod."
  type        = bool
  default     = false
}

variable "autoscaling_min_capacity" {
  description = "Minimum ECS task count for autoscaling."
  type        = number
  default     = 1
}

variable "autoscaling_max_capacity" {
  description = "Maximum ECS task count for autoscaling."
  type        = number
  default     = 2
}
