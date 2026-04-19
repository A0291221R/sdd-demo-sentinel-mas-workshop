variable "environment" {
  type = string
}

variable "sqs_queue_arn" {
  description = "ARN of the SQS task queue (used in task role policies)."
  type        = string
}
