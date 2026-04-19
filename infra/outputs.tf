output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer."
  value       = module.alb.alb_dns_name
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint."
  value       = module.rds.rds_endpoint
}

output "sqs_queue_url" {
  description = "URL of the SQS task queue."
  value       = module.sqs.queue_url
}

output "ecr_api_url" {
  description = "ECR repository URL for the api service."
  value       = module.ecs.ecr_api_url
}

output "ecr_central_url" {
  description = "ECR repository URL for the central service."
  value       = module.ecs.ecr_central_url
}

output "ecr_ui_url" {
  description = "ECR repository URL for the ui service."
  value       = module.ecs.ecr_ui_url
}

output "acm_validation_cname" {
  description = "DNS CNAME record required to validate the ACM certificate."
  value       = module.alb.acm_validation_cname
}
