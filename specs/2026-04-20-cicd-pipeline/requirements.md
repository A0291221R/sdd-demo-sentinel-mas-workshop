# Requirements — Phase 11: CI/CD Pipeline

_Branch: `phase-11-cicd-pipeline` | Date: 2026-04-20_

---

## Scope

### Included

**GitHub Actions workflows** under `.github/workflows/`:

| File | Trigger | Purpose |
|------|---------|---------|
| `ci.yml` | push / pull_request | Lint, type-check, unit test all three services |
| `build-push.yml` | push to `main` | Build Docker images, push to ECR for all three services |
| `deploy.yml` | after `build-push` completes | Trigger CodeDeploy blue/green for `api` and rolling for `central` |

**CloudWatch alarms** — new `cloudwatch` Terraform module under `infra/modules/cloudwatch/`:

| Alarm | Metric | Threshold |
|-------|--------|-----------|
| `api-5xx-rate` | `HTTPCode_Target_5XX_Count` on ALB target group | > 5 in 5 min |
| `central-policy-rejection-rate` | Custom metric `sentinel/PolicyRejections` emitted from `central` | > 10 in 5 min |

**Auto-rollback wiring** — update `infra/modules/codedeploy/main.tf` to reference the `api-5xx-rate` alarm so CodeDeploy triggers rollback on alarm breach.

### Not included

- Production environment (Phase 12)
- Secrets rotation automation (Phase 12)
- Multi-service deployment ordering (only `api` uses CodeDeploy; `central` uses ECS rolling)
- Load testing or canary traffic analysis

---

## Decisions

**1. Single CI job vs matrix** — Use a matrix strategy (`service: [api, central, ui]`) so each service's lint/test/typecheck runs in parallel but failures are reported per service. Avoids a monolithic job that silently skips one service on a Python error.

**2. Docker build caching** — Use `docker/build-push-action` with `cache-from: type=gha` and `cache-to: type=gha,mode=max` to cache layer builds between runs. Keeps build times under 3 minutes for incremental changes.

**3. ECR authentication** — Use `aws-actions/amazon-ecr-login` with OIDC-based role assumption (no long-lived AWS keys stored as secrets). Requires an IAM OIDC provider for `token.actions.githubusercontent.com` in the AWS account.

**4. CodeDeploy trigger** — `deploy.yml` calls `aws deploy create-deployment` via AWS CLI. This avoids a third-party Action dependency and keeps the deployment command auditable in the workflow file.

**5. CloudWatch custom metric** — `central` already logs policy rejections via the `audit_log`; Phase 11 adds a `put_metric_data` call in `sentinel_policy.py` after each rejection. Namespace: `sentinel`, metric name: `PolicyRejections`, dimensions: `service=central`.

**6. Alarm module location** — New `infra/modules/cloudwatch/` module (not bolted onto `ecs` or `alb`) so the alarm set can grow independently. Wired from root `main.tf`.

---

## Context

- Existing patterns: `infra/modules/*/main.tf` — all modules follow the same `locals { name }` + tagged resource pattern
- GitHub Actions: repo already uses `github-education` remote; OIDC trust policy must name this org/repo
- `ruff` is the Python linter (see `services/api/` and `services/central/` — check for `pyproject.toml` or `ruff.toml`)
- `eslint` is already scaffolded by Vite in `services/ui/` — confirm config file name before referencing
- `mypy` is run with `--strict`; `tsc --noEmit` for TypeScript
- `pytest` for Python, `vitest run` for UI (already configured in `services/ui/package.json`)
- Docker images tagged with `$GITHUB_SHA` (short) for traceability; `latest` tag also pushed on `main`
- CodeDeploy deployment group names come from `infra/modules/codedeploy/outputs.tf`: `api_deployment_group_name`
- No new Python or npm dependencies without user approval
