locals {
  name            = "sentinel-${var.environment}"
  certificate_arn = var.certificate_arn != "" ? var.certificate_arn : try(aws_acm_certificate.this[0].arn, "")
  https_enabled   = var.certificate_arn != ""
}

# ACM certificate — created when certificate_arn is not provided.
# DNS validation CNAME must be added manually; see outputs.acm_validation_cname.
# Once the cert reaches ISSUED state, set certificate_arn in tfvars and re-apply
# to switch from HTTP-only mode to HTTPS.
resource "aws_acm_certificate" "this" {
  count             = var.certificate_arn == "" ? 1 : 0
  domain_name       = var.domain_name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = { Name = "${local.name}-cert" }
}

# ALB
resource "aws_lb" "this" {
  name               = "${local.name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_sg_id]
  subnets            = var.public_subnet_ids

  tags = { Name = "${local.name}-alb" }
}

# Target groups
resource "aws_lb_target_group" "api_blue" {
  name        = "${local.name}-api-blue"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
  }
}

resource "aws_lb_target_group" "api_green" {
  name        = "${local.name}-api-green"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
  }
}

resource "aws_lb_target_group" "ui" {
  name        = "${local.name}-ui"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    path              = "/"
    healthy_threshold = 2
    interval          = 30
  }
}

# HTTP listener — two modes:
# bootstrap (no valid cert): forwards directly so ALB is functional immediately
# https_enabled: redirects to HTTPS
resource "aws_lb_listener" "http_forward" {
  count             = local.https_enabled ? 0 : 1
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ui.arn
  }
}

resource "aws_lb_listener" "http_redirect" {
  count             = local.https_enabled ? 1 : 0
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# HTTPS listener — only when a validated cert is provided
resource "aws_lb_listener" "https" {
  count             = local.https_enabled ? 1 : 0
  load_balancer_arn = aws_lb.this.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = local.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ui.arn
  }
}

# API path rule — attaches to whichever listener is active
resource "aws_lb_listener_rule" "api" {
  listener_arn = local.https_enabled ? aws_lb_listener.https[0].arn : aws_lb_listener.http_forward[0].arn
  priority     = 10

  condition {
    path_pattern {
      values = ["/query", "/result/*", "/tasks/*", "/health"]
    }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api_blue.arn
  }
}
