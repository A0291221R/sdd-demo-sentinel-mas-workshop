module "networking" {
  source            = "../../modules/networking"
  environment       = var.environment
  nat_gateway_count = 2
}

module "sqs" {
  source      = "../../modules/sqs"
  environment = var.environment
}

module "iam" {
  source               = "../../modules/iam"
  environment          = var.environment
  sqs_queue_arn        = module.sqs.queue_arn
  github_repo          = var.github_repo
  create_oidc_provider = var.create_oidc_provider
  oidc_provider_arn    = var.oidc_provider_arn
}

module "rds" {
  source             = "../../modules/rds"
  environment        = var.environment
  private_subnet_ids = module.networking.private_subnet_ids
  rds_sg_id          = module.networking.rds_sg_id
  db_password        = var.db_password

  instance_class            = "db.t3.small"
  deletion_protection       = true
  skip_final_snapshot       = false
  final_snapshot_identifier = "sentinel-prod-final-snapshot"
}

module "secrets" {
  source      = "../../modules/secrets"
  environment = var.environment
}

module "ecs" {
  source      = "../../modules/ecs"
  environment = var.environment
  aws_region  = var.aws_region

  private_subnet_ids    = module.networking.private_subnet_ids
  app_sg_id             = module.networking.app_sg_id
  execution_role_arn    = module.iam.execution_role_arn
  api_task_role_arn     = module.iam.api_task_role_arn
  central_task_role_arn = module.iam.central_task_role_arn

  api_tg_arn_blue              = module.alb.api_tg_arn_blue
  queue_url                    = module.sqs.queue_url
  db_url_secret_arn            = module.rds.db_url_secret_arn
  anthropic_api_key_secret_arn = module.secrets.anthropic_api_key_secret_arn
  sqs_queue_url_secret_arn     = module.secrets.sqs_queue_url_secret_arn

  desired_count            = 2
  enable_autoscaling       = true
  autoscaling_min_capacity = 2
  autoscaling_max_capacity = 4
}

module "alb" {
  source      = "../../modules/alb"
  environment = var.environment

  vpc_id            = module.networking.vpc_id
  public_subnet_ids = module.networking.public_subnet_ids
  alb_sg_id         = module.networking.alb_sg_id
  domain_name       = var.domain_name
  certificate_arn   = var.certificate_arn
}

module "cloudwatch" {
  source      = "../../modules/cloudwatch"
  environment = var.environment
  aws_region  = var.aws_region

  alb_arn_suffix       = module.alb.alb_arn_suffix
  api_tg_arn_suffix    = module.alb.api_tg_arn_suffix_blue
  cluster_name         = module.ecs.cluster_name
  api_service_name     = module.ecs.api_service_name
  central_service_name = module.ecs.central_service_name
  sqs_queue_name       = module.sqs.queue_name
}

module "codedeploy" {
  source      = "../../modules/codedeploy"
  environment = var.environment

  codedeploy_role_arn = module.iam.codedeploy_role_arn
  cluster_name        = module.ecs.cluster_name
  api_service_name    = module.ecs.api_service_name
  alb_listener_arn    = module.alb.https_listener_arn
  api_tg_name_blue    = module.alb.api_tg_name_blue
  api_tg_name_green   = module.alb.api_tg_name_green
  api_5xx_alarm_name  = module.cloudwatch.api_5xx_alarm_name
}
