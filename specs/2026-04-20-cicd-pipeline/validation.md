# Validation — Phase 11: CI/CD Pipeline

---

## Automated

### Terraform
- `terraform init -backend=false && terraform validate` passes with no errors in `infra/`
- `terraform fmt -recursive -check` passes (no formatting diffs)

### GitHub Actions workflow syntax
- `actionlint` or `gh workflow list` does not report YAML parse errors on all three workflow files
- Each workflow file has correct `on:` trigger, `permissions:`, and `jobs:` structure

### Python services (existing test suites must still pass)
- `pytest services/api/tests/` — all existing tests pass
- `pytest services/central/tests/` — all existing tests pass
- The `put_metric_data` call in `sentinel_policy.py` is guarded so tests pass without AWS credentials

### UI (existing test suite must still pass)
- `npm run test -- --run` in `services/ui/` passes

---

## Manual walkthrough

### CI workflow
1. Push a branch with a deliberate Python syntax error in `services/api/`
2. Verify the `ci.yml` run fails on the `api` matrix job and the `central`/`ui` jobs still complete
3. Fix the error and push again — verify all three matrix jobs turn green

### Build-push workflow
1. Merge a clean branch to `main`
2. Verify `build-push.yml` triggers automatically after `ci.yml` succeeds
3. In AWS Console → ECR, confirm three repositories each have a new image tagged with the commit SHA and `latest`

### Deploy workflow
1. After `build-push.yml` completes, verify `deploy.yml` triggers automatically
2. In AWS Console → CodeDeploy → `sentinel-dev-api-dg`, confirm a new deployment is IN_PROGRESS
3. In AWS Console → ECS → `sentinel-dev-central` service, confirm a new deployment is rolling

### CloudWatch alarms (Terraform)
1. After `terraform apply`, verify three alarms exist in CloudWatch: `sentinel-dev-api-5xx-rate`, `sentinel-dev-policy-rejection-rate`
2. All alarms start in `INSUFFICIENT_DATA` state (no traffic yet) — this is expected

### Auto-rollback wiring
1. In CodeDeploy → `sentinel-dev-api-dg` → deployment group settings, confirm the `sentinel-dev-api-5xx-rate` alarm is listed under "Roll back when alarms are configured"

### PolicyRejections metric emission
1. Trigger a policy rejection locally via existing `SentinelPolicy` tests with `AWS_DEFAULT_REGION` set to a dummy value
2. Confirm `put_metric_data` is called (mock or log assertion)
3. Confirm `put_metric_data` is NOT called (no exception) when `AWS_DEFAULT_REGION` is unset

---

## Edge cases

- Workflow runs on forks: `build-push` and `deploy` must only run on the `main` branch of the origin repo — verify `github.repository == 'A0291221R/sdd-demo-sentinel-mas-workshop'` condition
- ECR image push fails: `deploy.yml` must not trigger if `build-push.yml` exits with failure — verify `workflow_run` trigger filters on `conclusion: success`
- `central` service rolling update: `force-new-deployment` is idempotent; re-running `deploy.yml` twice must not break the service

---

## Definition of done

- [ ] All three workflow files exist under `.github/workflows/` and are syntactically valid
- [ ] `ci.yml` matrix covers lint + typecheck + test for `api`, `central`, `ui`
- [ ] `build-push.yml` pushes tagged images to ECR on merge to `main`
- [ ] `deploy.yml` triggers CodeDeploy for `api` and `ecs update-service` for `central`
- [ ] `infra/modules/cloudwatch/` module exists and `terraform validate` passes
- [ ] `aws_codedeploy_deployment_group.api` has `alarm_configuration` referencing the 5xx alarm
- [ ] `sentinel_policy.py` emits `PolicyRejections` metric; existing tests still pass
- [ ] `infra/modules/iam/main.tf` includes GitHub Actions OIDC role and `cloudwatch:PutMetricData` for central
