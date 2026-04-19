variable "environment" {
  type = string
}

variable "alb_arn_suffix" {
  description = "ARN suffix of the ALB (aws_lb.this.arn_suffix)."
  type        = string
}

variable "api_tg_arn_suffix" {
  description = "ARN suffix of the API blue target group."
  type        = string
}

variable "alarm_sns_arn" {
  description = "Optional SNS topic ARN for alarm notifications. Leave empty to skip."
  type        = string
  default     = ""
}
