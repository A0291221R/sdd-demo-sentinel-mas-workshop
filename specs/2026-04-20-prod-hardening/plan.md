# Plan — Phase 12: Production Environment and Hardening

---

## Group 1 — Prod Terraform environment directory

1.1 Create `infra/environments/prod/backend.tf`:
   - Same S3 bucket as dev: `sentinel-mas-tf-state-590183890857`
   - Key: `prod/terraform.tfstate`
   - Region: `ap-southeast-1`, encrypt: `true`, dynamodb_table: `sentinel-mas-tf-locks`

1.2 Create `infra/environments/prod/variables.tf`:
   - `environment = "prod"` (default)
   - `aws_region = "ap-southeast-1"` (default)
   - `db_password` (sensitive, no default)
   - `domain_name` (no default)
   - `github_repo = "A0291221R/sdd-demo-sentinel-mas-workshop"` (default)
   - `create_oidc_provider = false` (default — provider already created by dev)

1.3 Create `infra/environments/prod/main.tf` — calls all root modules with prod overrides:
   - Pass `environment = "prod"` everywhere
   - Source modules as `../../modules/<name>` (relative path from environments/prod/)

1.4 Create `infra/environments/prod/terraform.tfvars.example`:
   ```hcl
   db_password = "<set via CI secret or manual>"
   domain_name = "sentinel.example.com"
   ```

1.5 Create `infra/environments/prod/versions.tf` — same Terraform/provider constraints as `infra/versions.tf`

---

## Group 2 — RDS prod overrides

2.1 Add variables to `infra/modules/rds/variables.tf`:
   - `instance_class` (default: `"db.t3.micro"`) — prod sets `"db.t3.small"`
   - `deletion_protection` (default: `false`) — prod sets `true`
   - `skip_final_snapshot` (default: `true`) — prod sets `false`
   - `final_snapshot_identifier` (default: `""`) — prod sets `"${name}-final-snapshot"`

2.2 Update `infra/modules/rds/main.tf` to use these variables instead of hardcoded values; remove the dev-only comments

---

## Group 3 — Networking prod overrides (dual NAT)

3.1 Add `nat_gateway_count` variable to `infra/modules/networking/variables.tf` (default: `1`)

3.2 Update `infra/modules/networking/main.tf`:
   - `aws_eip.nat` becomes `count = var.nat_gateway_count`
   - `aws_nat_gateway.this` becomes `count = var.nat_gateway_count`, each in `public[count.index]`
   - Private route table references `aws_nat_gateway.this[0]` (existing behaviour unchanged)
   - Remove the single-NAT dev comment; the variable makes the choice explicit

---

## Group 4 — Secrets Manager entries for prod

4.1 Create `infra/modules/secrets/main.tf`:
   - `aws_secretsmanager_secret.sqs_queue_url` — name: `sentinel-${var.environment}-sqs-queue-url`
   - `aws_secretsmanager_secret.anthropic_api_key` — name: `sentinel-${var.environment}-anthropic-api-key`
   - No `aws_secretsmanager_secret_version` resources — values are set out-of-band

4.2 Create `infra/modules/secrets/variables.tf`: `environment`

4.3 Create `infra/modules/secrets/outputs.tf`: `sqs_queue_url_secret_arn`, `anthropic_api_key_secret_arn`

4.4 Add `anthropic_api_key` secret injection to `infra/modules/ecs/main.tf`:
   - Add `var.anthropic_api_key_secret_arn` variable
   - Add to central task definition `secrets` block: `{ name = "ANTHROPIC_API_KEY", valueFrom = var.anthropic_api_key_secret_arn }`

4.5 Update `infra/modules/ecs/variables.tf` with new variable

4.6 Wire `module "secrets"` in both `infra/main.tf` (dev — optional, for consistency) and `infra/environments/prod/main.tf`

---

## Group 5 — ECS autoscaling

5.1 Add `aws_appautoscaling_target` to `infra/modules/ecs/main.tf` for api and central:
   ```hcl
   resource "aws_appautoscaling_target" "api" {
     max_capacity       = var.autoscaling_max_capacity
     min_capacity       = var.autoscaling_min_capacity
     resource_id        = "service/${aws_ecs_cluster.this.name}/${aws_ecs_service.api.name}"
     scalable_dimension = "ecs:service:DesiredCount"
     service_namespace  = "ecs"
   }
   ```

5.2 Add `aws_appautoscaling_policy` (TargetTrackingScaling) for both api and central:
   - Metric: `ECSServiceAverageCPUUtilization`
   - Target: `70.0`

5.3 Add autoscaling variables to `infra/modules/ecs/variables.tf`:
   - `autoscaling_min_capacity` (default: `1`)
   - `autoscaling_max_capacity` (default: `2`)

5.4 Prod `main.tf` passes `autoscaling_min_capacity = 1`, `autoscaling_max_capacity = 2`; dev leaves defaults

---

## Group 6 — CloudWatch dashboard

6.1 Add `aws_cloudwatch_dashboard` to `infra/modules/cloudwatch/main.tf`:
   - Widget 1: ECS CPUUtilization line chart (api + central)
   - Widget 2: ALB HTTPCode_Target_5XX_Count
   - Widget 3: sentinel/PolicyRejections custom metric
   - Widget 4: SQS ApproximateNumberOfMessagesVisible

6.2 Add variables to `infra/modules/cloudwatch/variables.tf`:
   - `cluster_name`, `api_service_name`, `central_service_name`, `sqs_queue_name`

6.3 Wire new variables from root `main.tf` (ecs and sqs module outputs already exist)

---

## Group 7 — Runbook

7.1 Create `playbook/runbook.md` with sections:
   - On-call contacts and escalation
   - Health checks (ALB target group health, ECS service events, RDS status)
   - Manual CodeDeploy rollback procedure
   - Anthropic API key rotation (Secrets Manager + ECS force-new-deployment)
   - Promoting dev image to prod (ECR tag copy + deploy workflow dispatch)
   - Emergency stop (scale ECS service to 0)

---

## Group 8 — Terraform validate

8.1 Run `terraform init -backend=false && terraform validate` in `infra/` (root modules)

8.2 Run `terraform init -backend=false && terraform validate` in `infra/environments/prod/`
