output "execution_role_arn" {
  value = aws_iam_role.execution.arn
}

output "api_task_role_arn" {
  value = aws_iam_role.api_task.arn
}

output "central_task_role_arn" {
  value = aws_iam_role.central_task.arn
}

output "codedeploy_role_arn" {
  value = aws_iam_role.codedeploy.arn
}

output "github_actions_role_arn" {
  value = aws_iam_role.github_actions.arn
}
