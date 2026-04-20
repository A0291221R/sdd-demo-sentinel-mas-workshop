variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "alb_sg_id" {
  type = string
}

variable "domain_name" {
  type = string
}

variable "certificate_arn" {
  description = "ARN of a pre-existing ACM certificate to use for the HTTPS listener. When set, no new ACM certificate is created. Leave empty to create one (requires manual DNS validation before HTTPS works)."
  type        = string
  default     = ""
}
