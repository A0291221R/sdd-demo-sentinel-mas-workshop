# Requirements — Phase 12: Production Environment and Hardening

_Branch: `phase-12-prod-hardening` | Date: 2026-04-20_

---

## Scope

### Included

**1. Terraform prod workspace** — `infra/environments/prod/` directory:

| File | Purpose |
|------|---------|
| `backend.tf` | S3 state at `prod/terraform.tfstate` in the same bucket as dev |
| `main.tf` | Calls all root modules with `environment = "prod"` overrides |
| `variables.tf` | Prod-specific variable defaults (instance sizes, deletion protection) |
| `terraform.tfvars.example` | Example values file (no secrets) |

Prod overrides relative to dev:
- RDS: `instance_class = "db.t3.small"`, `deletion_protection = true`, `skip_final_snapshot = false`
- ECS: desired_count = 2 for api and central; Fargate autoscaling min=1, max=2 (cpu_utilization ≥ 70%)
- Networking: two NAT gateways (one per AZ) for redundancy
- CodeDeploy: same blue/green config, alarm wired to prod alarms

**2. Secrets Manager entries** — three secrets created via Terraform in the prod environment:

| Secret name | Value | Where used |
|-------------|-------|-----------|
| `sentinel-prod-db-url` | Full Postgres connection string | ECS task def (api, central) — already handled by `rds` module pattern from Phase 10 |
| `sentinel-prod-sqs-queue-url` | SQS queue URL | ECS task def (api, central) — new; replace `environment` var with `secrets` block |
| `sentinel-prod-anthropic-api-key` | Anthropic API key | ECS task def (central) — new secret + IAM permission |

The `sqs-queue-url` and `anthropic-api-key` secrets are created as `aws_secretsmanager_secret` resources with empty initial versions; values are set out-of-band (console/CLI) to keep credentials out of Terraform state.

**3. CloudWatch dashboard** — `infra/modules/cloudwatch/main.tf` gains an `aws_cloudwatch_dashboard` resource:

Widgets:
- Agent throughput: `AWS/ECS` `CPUUtilization` for api and central
- Error rate: `HTTPCode_Target_5XX_Count` (ALB) — reuses alarm metric
- Policy rejections: `sentinel/PolicyRejections` custom metric
- SQS queue depth: `AWS/SQS` `ApproximateNumberOfMessagesVisible`

**4. Fargate autoscaling** — added to `infra/modules/ecs/main.tf`:
- `aws_appautoscaling_target` for api and central services
- `aws_appautoscaling_policy` (TargetTrackingScaling, cpu_utilization = 70%)
- Min capacity = 1, max capacity = 2 (light traffic profile: 10 req/min)

**5. Runbook** — `playbook/runbook.md`:
- On-call contact and escalation path
- How to check service health (ALB target groups, ECS service events)
- How to trigger a manual CodeDeploy rollback
- How to rotate the Anthropic API key (Secrets Manager + ECS force-new-deployment)
- How to promote a dev image to prod (ECR tag copy + deploy workflow)

### Not included

- Multi-region deployment (explicitly deferred in roadmap)
- Automated secrets rotation (Secrets Manager rotation Lambda — post-MVP)
- Actual load test execution (define autoscaling config; defer benchmark run)
- Prod DNS / ACM validation (same manual step as dev — see infra/README.md)

---

## Decisions

**1. Environment structure: `infra/environments/prod/` not Terraform workspaces** — Terraform workspaces share the same module code but separate state. A separate `environments/prod/` directory with its own `main.tf` and `variables.tf` is more explicit: a reader can see exactly what differs between dev and prod without running `terraform workspace select`. This pattern also avoids the footgun of `terraform destroy` in the wrong workspace.

**2. SQS URL as a secret** — SQS queue URLs contain the AWS account ID and are not authentication credentials. However, storing them in Secrets Manager alongside `DATABASE_URL` and `ANTHROPIC_API_KEY` is consistent (one pattern for all runtime config that varies by environment), avoids hardcoding account IDs in task definitions, and incurs negligible cost.

**3. Anthropic key as a shell secret (not auto-populated)** — The key value is never written into Terraform state. The `aws_secretsmanager_secret` resource is created with no initial version; the value is set via `aws secretsmanager put-secret-value` by a human operator. The IAM execution role gains `secretsmanager:GetSecretValue` on `sentinel-prod-anthropic-api-key`.

**4. Autoscaling capped at max=2 for light traffic** — 10 req/min peak does not justify more than two Fargate tasks. CPU target of 70% provides headroom for burst without over-provisioning. Raising the cap is a one-line Terraform change when traffic grows.

**5. Dashboard in existing `cloudwatch` module** — Adding the `aws_cloudwatch_dashboard` to the existing module avoids a new module; the dashboard is already referencing the same metric names and alarm ARNs. No additional wiring required in `main.tf`.

---

## Context

- Existing pattern: all modules use `locals { name = "sentinel-${var.environment}" }` — prod resources automatically get `sentinel-prod-*` names
- `infra/modules/rds/main.tf` already has the `aws_secretsmanager_secret` + version pattern from Phase 10; the sqs and anthropic secrets follow the same shape
- RDS deletion_protection and skip_final_snapshot comments in `rds/main.tf` already note "Phase 12 prod: set these"
- The `iam` module's `execution_extras` policy already grants `secretsmanager:GetSecretValue` for `sentinel-${var.environment}-*` — prod secrets named `sentinel-prod-*` are covered automatically
- Autoscaling requires the ECS service to not use `CODE_DEPLOY` controller for central (already fixed in Phase 10); api uses CODE_DEPLOY but autoscaling target still applies
- Runbook lives in `playbook/` — existing `playbook/README.md` and `playbook/ship.md` set the pattern
