variable "environment" {
  type = string
}

variable "codedeploy_role_arn" {
  type = string
}

variable "cluster_name" {
  type = string
}

variable "api_service_name" {
  type = string
}

variable "alb_listener_arn" {
  type = string
}

variable "api_tg_name_blue" {
  type = string
}

variable "api_tg_name_green" {
  type = string
}

variable "api_5xx_alarm_arn" {
  description = "ARN of the CloudWatch alarm that triggers CodeDeploy rollback."
  type        = string
}
