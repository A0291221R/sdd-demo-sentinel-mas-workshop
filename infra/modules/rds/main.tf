locals {
  name = "sentinel-${var.environment}"
}

resource "aws_db_subnet_group" "this" {
  name       = "${local.name}-rds-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = { Name = "${local.name}-rds-subnet-group" }
}

resource "aws_db_parameter_group" "this" {
  name   = "${local.name}-pg15"
  family = "postgres15"

  tags = { Name = "${local.name}-pg15" }
}

resource "aws_db_instance" "this" {
  identifier        = "${local.name}-postgres"
  engine            = "postgres"
  engine_version    = "15"
  instance_class    = var.instance_class
  allocated_storage = 20
  storage_encrypted = true

  db_name  = "sentinel"
  username = "sentinel"
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.this.name
  parameter_group_name   = aws_db_parameter_group.this.name
  vpc_security_group_ids = [var.rds_sg_id]

  skip_final_snapshot       = var.skip_final_snapshot
  deletion_protection       = var.deletion_protection
  final_snapshot_identifier = var.skip_final_snapshot ? null : var.final_snapshot_identifier

  tags = { Name = "${local.name}-postgres" }

  lifecycle {
    precondition {
      condition     = var.skip_final_snapshot || var.final_snapshot_identifier != ""
      error_message = "final_snapshot_identifier must be set when skip_final_snapshot is false."
    }
  }
}

# Store the full database URL as a Secrets Manager secret so ECS tasks
# never receive the password as a plaintext environment variable.
resource "aws_secretsmanager_secret" "db_url" {
  name = "sentinel-${var.environment}-db-url"
}

resource "aws_secretsmanager_secret_version" "db_url" {
  secret_id     = aws_secretsmanager_secret.db_url.id
  secret_string = "postgres://sentinel:${var.db_password}@${aws_db_instance.this.endpoint}/${aws_db_instance.this.db_name}"
}
