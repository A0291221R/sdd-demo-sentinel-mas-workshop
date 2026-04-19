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

variable "db_url_secret_arn" {
  description = "ARN of the Secrets Manager secret holding the DATABASE_URL value."
  type        = string
}
