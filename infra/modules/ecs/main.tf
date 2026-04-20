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

    environment = var.sqs_queue_url_secret_arn != "" ? [] : [
      { name = "QUEUE_URL", value = var.queue_url }
    ]

    secrets = concat(
      [{ name = "DATABASE_URL", valueFrom = var.db_url_secret_arn }],
      var.sqs_queue_url_secret_arn != "" ? [{ name = "QUEUE_URL", valueFrom = var.sqs_queue_url_secret_arn }] : []
    )

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

    environment = concat(
      [{ name = "PYTHONUNBUFFERED", value = "1" }],
      var.sqs_queue_url_secret_arn != "" ? [] : [{ name = "QUEUE_URL", value = var.queue_url }]
    )

    secrets = concat(
      [{ name = "DATABASE_URL", valueFrom = var.db_url_secret_arn }],
      var.anthropic_api_key_secret_arn != "" ? [{ name = "ANTHROPIC_API_KEY", valueFrom = var.anthropic_api_key_secret_arn }] : [],
      var.sqs_queue_url_secret_arn != "" ? [{ name = "QUEUE_URL", valueFrom = var.sqs_queue_url_secret_arn }] : []
    )

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
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [var.app_sg_id]
  }

  load_balancer {
    target_group_arn = var.api_tg_arn_blue
    container_name   = "api"
    container_port   = 8000
  }

  deployment_controller {
    type = "CODE_DEPLOY"
  }

  lifecycle {
    # CodeDeploy manages task_definition and load_balancer after first deploy.
    # desired_count is managed by autoscaling after first deploy.
    ignore_changes = [task_definition, load_balancer, desired_count]
  }
}

resource "aws_ecs_service" "central" {
  name            = "${local.name}-central"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.central.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [var.app_sg_id]
  }

  lifecycle {
    ignore_changes = [desired_count]
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

  load_balancer {
    target_group_arn = var.ui_target_group_arn
    container_name   = "ui"
    container_port   = 80
  }

  lifecycle {
    ignore_changes = [task_definition]
  }
}

# Autoscaling — only created when enable_autoscaling = true (prod)
resource "aws_appautoscaling_target" "api" {
  count              = var.enable_autoscaling ? 1 : 0
  max_capacity       = var.autoscaling_max_capacity
  min_capacity       = var.autoscaling_min_capacity
  resource_id        = "service/${aws_ecs_cluster.this.name}/${aws_ecs_service.api.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_target" "central" {
  count              = var.enable_autoscaling ? 1 : 0
  max_capacity       = var.autoscaling_max_capacity
  min_capacity       = var.autoscaling_min_capacity
  resource_id        = "service/${aws_ecs_cluster.this.name}/${aws_ecs_service.central.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "api_cpu" {
  count              = var.enable_autoscaling ? 1 : 0
  name               = "${local.name}-api-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.api[0].resource_id
  scalable_dimension = aws_appautoscaling_target.api[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.api[0].service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}

resource "aws_appautoscaling_policy" "central_cpu" {
  count              = var.enable_autoscaling ? 1 : 0
  name               = "${local.name}-central-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.central[0].resource_id
  scalable_dimension = aws_appautoscaling_target.central[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.central[0].service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}
