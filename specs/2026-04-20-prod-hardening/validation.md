# Validation — Phase 12: Production Environment and Hardening

---

## Automated

### Terraform (root dev modules)
- `terraform init -backend=false && terraform validate` passes in `infra/`
- `terraform fmt -recursive -check` passes

### Terraform (prod environment)
- `terraform init -backend=false && terraform validate` passes in `infra/environments/prod/`
- `terraform fmt -recursive -check` passes in `infra/environments/prod/`

### Python services (no regressions)
- `pytest services/api/tests/` — all existing tests pass
- `pytest services/central/tests/` — all existing tests pass

---

## Manual walkthrough

### Prod state isolation
1. Confirm `infra/environments/prod/backend.tf` uses key `prod/terraform.tfstate`
2. Confirm dev backend key is still `dev/terraform.tfstate`
3. `terraform init -backend=false` in both directories succeeds without cross-contamination warnings

### Prod RDS overrides
1. In `infra/environments/prod/main.tf`, confirm `rds` module is called with `deletion_protection = true` and `skip_final_snapshot = false`
2. Confirm `infra/modules/rds/main.tf` uses the variables (not hardcoded values)

### Dual NAT gateway
1. In `infra/environments/prod/main.tf`, confirm `networking` module is called with `nat_gateway_count = 2`
2. In `infra/main.tf` (dev), confirm `nat_gateway_count` is not set (defaults to 1 — no change)

### Secrets Manager entries
1. Confirm three secrets exist in prod `main.tf`: `sentinel-prod-db-url` (via rds module), `sentinel-prod-sqs-queue-url`, `sentinel-prod-anthropic-api-key`
2. Confirm `sqs-queue-url` and `anthropic-api-key` secrets have NO version resource (values set out-of-band)
3. Confirm `central` ECS task definition includes `ANTHROPIC_API_KEY` in `secrets` block

### Autoscaling config
1. After `terraform plan` (mock), confirm `aws_appautoscaling_target` and `aws_appautoscaling_policy` resources appear for api and central
2. Confirm policy target value is `70.0` and metric is `ECSServiceAverageCPUUtilization`
3. Confirm min=1, max=2 in prod; dev still defaults to min=1, max=2 (same, no regression)

### CloudWatch dashboard
1. After `terraform apply` in prod, verify dashboard `sentinel-prod-dashboard` appears in CloudWatch console
2. Dashboard has exactly 4 widgets covering: CPU, 5xx errors, policy rejections, SQS depth

### Runbook
1. `playbook/runbook.md` exists and has all required sections
2. Manual rollback procedure references the correct CodeDeploy app/group names (`sentinel-prod-api`, `sentinel-prod-api-dg`)
3. Key rotation procedure references `sentinel-prod-anthropic-api-key`

---

## Edge cases

- `create_oidc_provider = false` in prod: confirm `github_actions` IAM role still creates correctly using the `oidc_provider_arn` variable from the existing dev provider
- NAT gateway count change from 1→2: applying prod must not modify dev state (separate state files guarantee this)
- `anthropic-api-key` secret with no version: ECS task launch will fail at runtime until the value is set — this is expected and documented in the runbook

---

## Definition of done

- [ ] `infra/environments/prod/` directory exists with `backend.tf`, `main.tf`, `variables.tf`, `versions.tf`, `terraform.tfvars.example`
- [ ] `terraform validate` passes in both `infra/` and `infra/environments/prod/`
- [ ] RDS module accepts `deletion_protection` and `skip_final_snapshot` as variables; prod sets both correctly
- [ ] Networking module accepts `nat_gateway_count`; prod sets 2, dev unset (defaults to 1)
- [ ] `infra/modules/secrets/` module exists; creates `sqs-queue-url` and `anthropic-api-key` shells without values
- [ ] ECS central task definition includes `ANTHROPIC_API_KEY` secret reference
- [ ] `aws_appautoscaling_target` and policy exist for api and central in ECS module
- [ ] `aws_cloudwatch_dashboard` resource added to cloudwatch module with 4 widgets
- [ ] `playbook/runbook.md` exists with all 5 sections (health checks, rollback, key rotation, image promotion, emergency stop)
- [ ] All existing Python tests still pass
