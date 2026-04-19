locals {
  name = "sentinel-${var.environment}"
}

resource "aws_cloudwatch_metric_alarm" "api_5xx" {
  alarm_name          = "${local.name}-api-5xx-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = var.alb_arn_suffix
    TargetGroup  = var.api_tg_arn_suffix
  }

  alarm_description = "API target 5xx errors exceeded threshold — CodeDeploy will roll back."
  alarm_actions     = var.alarm_sns_arn != "" ? [var.alarm_sns_arn] : []
  ok_actions        = var.alarm_sns_arn != "" ? [var.alarm_sns_arn] : []

  tags = { Name = "${local.name}-api-5xx-rate" }
}

resource "aws_cloudwatch_metric_alarm" "policy_rejections" {
  alarm_name          = "${local.name}-policy-rejection-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "PolicyRejections"
  namespace           = "sentinel"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  treat_missing_data  = "notBreaching"

  alarm_description = "Sentinel policy rejection rate exceeded threshold."
  alarm_actions     = var.alarm_sns_arn != "" ? [var.alarm_sns_arn] : []
  ok_actions        = var.alarm_sns_arn != "" ? [var.alarm_sns_arn] : []

  tags = { Name = "${local.name}-policy-rejection-rate" }
}
