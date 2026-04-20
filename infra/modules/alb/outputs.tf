output "alb_dns_name" {
  value = aws_lb.this.dns_name
}

output "alb_arn" {
  value = aws_lb.this.arn
}

output "alb_arn_suffix" {
  value = aws_lb.this.arn_suffix
}

output "api_tg_arn_suffix_blue" {
  value = aws_lb_target_group.api_blue.arn_suffix
}

output "https_listener_arn" {
  # Returns the HTTPS listener ARN when available, otherwise the HTTP listener ARN.
  # CodeDeploy and the listener rule both use this so they always have a valid target.
  value = var.certificate_arn != "" ? aws_lb_listener.https[0].arn : aws_lb_listener.http_forward[0].arn
}

output "api_tg_name_blue" {
  value = aws_lb_target_group.api_blue.name
}

output "api_tg_name_green" {
  value = aws_lb_target_group.api_green.name
}

output "ui_tg_arn" {
  value = aws_lb_target_group.ui.arn
}

output "acm_validation_cname" {
  description = "Add this CNAME to your DNS to validate the ACM certificate. Empty when certificate_arn is provided."
  value = var.certificate_arn == "" ? {
    for dvo in aws_acm_certificate.this[0].domain_validation_options :
    dvo.domain_name => {
      name  = dvo.resource_record_name
      type  = dvo.resource_record_type
      value = dvo.resource_record_value
    }
  } : {}
}

output "api_tg_arn_blue" {
  value = aws_lb_target_group.api_blue.arn
}
