output "sqs_queue_url_secret_arn" {
  value = aws_secretsmanager_secret.sqs_queue_url.arn
}

output "anthropic_api_key_secret_arn" {
  value = aws_secretsmanager_secret.anthropic_api_key.arn
}
