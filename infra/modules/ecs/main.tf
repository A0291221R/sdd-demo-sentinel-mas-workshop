locals {
  name = "sentinel-${var.environment}"
}

# ECR repositories
resource "aws_ecr_repository" "api" {
  name                 = "${local.name}-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = { Name = "${local.name}-api" }
}

resource "aws_ecr_repository" "central" {
  name                 = "${local.name}-central"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = { Name = "${local.name}-central" }
}

resource "aws_ecr_repository" "ui" {
  name                 = "${local.name}-ui"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = { Name = "${local.name}-ui" }
}

# ECS cluster
resource "aws_ecs_cluster" "this" {
  name = local.name

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = { Name = local.name }
}

# CloudWatch log groups
resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/${local.name}-api"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "central" {
  name              = "/ecs/${local.name}-central"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "ui" {
  name              = "/ecs/${local.name}-ui"
  retention_in_days = 14
}

# Task definitions
resource "aws_ecs_task_definition" "api" {
  family                   = "${local.name}-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.api_task_role_arn

  container_definitions = jsonencode([{
    name      = "api"
    image     = "${aws_ecr_repository.api.repository_url}:latest"
    essential = true

    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]

    environment = [
      { name = "QUEUE_URL", value = var.queue_url }
    ]

    secrets = [
      { name = "DATABASE_URL", valueFrom = var.db_url_secret_arn }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.api.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "api"
      }
    }
  }])
}

resource "aws_ecs_task_definition" "central" {
  family                   = "${local.name}-central"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.central_task_role_arn

  container_definitions = jsonencode([{
    name      = "central"
    image     = "${aws_ecr_repository.central.repository_url}:latest"
    essential = true

    environment = [
      { name = "QUEUE_URL", value = var.queue_url }
    ]

    secrets = [
      { name = "DATABASE_URL", valueFrom = var.db_url_secret_arn }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.central.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "central"
      }
    }
  }])
}

resource "aws_ecs_task_definition" "ui" {
  family                   = "${local.name}-ui"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = var.execution_role_arn

  container_definitions = jsonencode([{
    name      = "ui"
    image     = "${aws_ecr_repository.ui.repository_url}:latest"
    essential = true

    portMappings = [{
      containerPort = 80
      protocol      = "tcp"
    }]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.ui.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ui"
      }
    }
  }])
}

# ECS services
resource "aws_ecs_service" "api" {
  name            = "${local.name}-api"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [var.app_sg_id]
  }

  deployment_controller {
    type = "CODE_DEPLOY"
  }

  lifecycle {
    # CodeDeploy manages task_definition and load_balancer after first deploy;
    # Terraform must not overwrite those fields on subsequent plans.
    ignore_changes = [task_definition, load_balancer]
  }
}

resource "aws_ecs_service" "central" {
  name            = "${local.name}-central"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.central.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [var.app_sg_id]
  }
}

resource "aws_ecs_service" "ui" {
  name            = "${local.name}-ui"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.ui.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [var.app_sg_id]
  }

  lifecycle {
    ignore_changes = [task_definition]
  }
}
