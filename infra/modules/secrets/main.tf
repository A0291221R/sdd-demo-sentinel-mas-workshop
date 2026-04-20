locals {
  name = "sentinel-${var.environment}"
}

resource "aws_secretsmanager_secret" "sqs_queue_url" {
  name = "${local.name}-sqs-queue-url"
}

resource "aws_secretsmanager_secret" "anthropic_api_key" {
  name = "${local.name}-anthropic-api-key"
}
