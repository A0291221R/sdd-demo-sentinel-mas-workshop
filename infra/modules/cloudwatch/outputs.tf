output "api_5xx_alarm_arn" {
  value = aws_cloudwatch_metric_alarm.api_5xx.arn
}

output "api_5xx_alarm_name" {
  value = aws_cloudwatch_metric_alarm.api_5xx.alarm_name
}

output "policy_rejection_alarm_arn" {
  value = aws_cloudwatch_metric_alarm.policy_rejections.arn
}
