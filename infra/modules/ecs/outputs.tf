output "cluster_arn" {
  value = aws_ecs_cluster.this.arn
}

output "cluster_name" {
  value = aws_ecs_cluster.this.name
}

output "api_service_name" {
  value = aws_ecs_service.api.name
}

output "central_service_name" {
  value = aws_ecs_service.central.name
}

output "ui_service_name" {
  value = aws_ecs_service.ui.name
}

output "ecr_api_url" {
  value = aws_ecr_repository.api.repository_url
}

output "ecr_central_url" {
  value = aws_ecr_repository.central.repository_url
}

output "ecr_ui_url" {
  value = aws_ecr_repository.ui.repository_url
}
