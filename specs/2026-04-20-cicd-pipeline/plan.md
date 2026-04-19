# Plan — Phase 11: CI/CD Pipeline

---

## Group 1 — GitHub Actions: CI workflow

1.1 Create `.github/workflows/ci.yml` with matrix strategy for `api`, `central`, `ui`

1.2 **api job steps:**
   - `actions/checkout`
   - `actions/setup-python@v5` (python-version: `3.11`)
   - `pip install ruff mypy pytest` + service requirements
   - `ruff check services/api`
   - `mypy --strict services/api`
   - `pytest services/api/tests/`

1.3 **central job steps** (same pattern):
   - `ruff check services/central`
   - `mypy --strict services/central`
   - `pytest services/central/tests/`

1.4 **ui job steps:**
   - `actions/setup-node@v4` (node-version: `20`)
   - `npm ci` in `services/ui/`
   - `npm run lint` (eslint)
   - `npx tsc --noEmit` in `services/ui/`
   - `npm run test -- --run` (vitest)

---

## Group 2 — GitHub Actions: build-push workflow

2.1 Create `.github/workflows/build-push.yml`
   - Trigger: `push` to `main`, on `ci` workflow completion (success only)
   - Permissions: `id-token: write`, `contents: read`

2.2 Add OIDC role assumption step using `aws-actions/configure-aws-credentials@v4`
   - Input: `role-to-assume` referencing a GitHub Actions deployment role ARN (stored as `AWS_DEPLOY_ROLE_ARN` secret)
   - Region: `ap-southeast-1`

2.3 Add `aws-actions/amazon-ecr-login@v2` step

2.4 For each service (`api`, `central`, `ui`):
   - `docker/build-push-action@v5` with:
     - `context: services/<name>`
     - `push: true`
     - `tags: <ECR_URL>/<name>:${{ github.sha }}, <ECR_URL>/<name>:latest`
     - `cache-from: type=gha`
     - `cache-to: type=gha,mode=max`

---

## Group 3 — GitHub Actions: deploy workflow

3.1 Create `.github/workflows/deploy.yml`
   - Trigger: `workflow_run` on `build-push` completing with `conclusion: success`

3.2 OIDC credential step (same role as build-push)

3.3 CodeDeploy deployment for `api`:
   ```bash
   aws deploy create-deployment \
     --application-name sentinel-dev-api \
     --deployment-group-name sentinel-dev-api-dg \
     --deployment-config-name CodeDeployDefault.ECSCanary10Percent5Minutes \
     --description "GitHub SHA ${{ github.sha }}"
   ```

3.4 ECS rolling update for `central` (force new deployment):
   ```bash
   aws ecs update-service \
     --cluster sentinel-dev \
     --service sentinel-dev-central \
     --force-new-deployment
   ```

---

## Group 4 — CloudWatch alarms: Terraform module

4.1 Create `infra/modules/cloudwatch/main.tf` with:
   - `aws_cloudwatch_metric_alarm.api_5xx` — metric: `HTTPCode_Target_5XX_Count`, namespace: `AWS/ApplicationELB`, statistic: `Sum`, period: 300, threshold: 5
   - `aws_cloudwatch_metric_alarm.policy_rejections` — metric: `PolicyRejections`, namespace: `sentinel`, statistic: `Sum`, period: 300, threshold: 10
   - Both alarms use `treat_missing_data = "notBreaching"`

4.2 Create `infra/modules/cloudwatch/variables.tf`:
   - `environment`, `alb_arn_suffix`, `api_tg_arn_suffix`, `alarm_sns_arn` (optional, defaults `""`)

4.3 Create `infra/modules/cloudwatch/outputs.tf`:
   - `api_5xx_alarm_arn`, `policy_rejection_alarm_arn`

4.4 Wire `module "cloudwatch"` in root `infra/main.tf`:
   - Pass `alb_arn_suffix = module.alb.alb_arn_suffix`, `api_tg_arn_suffix = module.alb.api_tg_arn_suffix_blue`

4.5 Add missing ALB outputs: `alb_arn_suffix`, `api_tg_arn_suffix_blue` to `infra/modules/alb/outputs.tf`

---

## Group 5 — Auto-rollback wiring

5.1 Update `infra/modules/codedeploy/main.tf` — add `alarm_configuration` block to `aws_codedeploy_deployment_group.api`:
   ```hcl
   alarm_configuration {
     alarms  = [var.api_5xx_alarm_name]
     enabled = true
   }
   ```

5.2 Add `api_5xx_alarm_name` variable to `infra/modules/codedeploy/variables.tf`

5.3 Pass `api_5xx_alarm_name = module.cloudwatch.api_5xx_alarm_name` in root `main.tf`

5.4 Add `api_5xx_alarm_name` output to `infra/modules/cloudwatch/outputs.tf`

---

## Group 6 — PolicyRejections custom metric emission

6.1 In `services/central/sentinel_policy.py`, after recording a rejection, call `boto3` `put_metric_data`:
   ```python
   cloudwatch.put_metric_data(
       Namespace="sentinel",
       MetricData=[{"MetricName": "PolicyRejections", "Value": 1, "Unit": "Count"}],
   )
   ```

6.2 Make the CloudWatch client optional/lazy (only emit if `AWS_DEFAULT_REGION` is set) so existing tests pass without AWS credentials.

6.3 Add IAM permission `cloudwatch:PutMetricData` on namespace `sentinel` to `infra/modules/iam/main.tf` central task role.

---

## Group 7 — Terraform validate

7.1 Run `terraform init -backend=false && terraform validate` in `infra/` after all Terraform changes

---

## Group 8 — IAM role for GitHub Actions OIDC (Terraform)

8.1 Add `aws_iam_openid_connect_provider` for `token.actions.githubusercontent.com` in `infra/modules/iam/main.tf`

8.2 Add `aws_iam_role.github_actions` with trust policy scoped to `repo:A0291221R/sdd-demo-sentinel-mas-workshop:ref:refs/heads/main`

8.3 Attach permissions: `ecr:GetAuthorizationToken`, `ecr:BatchGetImage`, `ecr:InitiateLayerUpload`, `ecr:UploadLayerPart`, `ecr:CompleteLayerUpload`, `ecr:PutImage`, `codedeploy:CreateDeployment`, `codedeploy:GetDeployment`, `ecs:UpdateService`, `ecs:DescribeServices`

8.4 Output `github_actions_role_arn` from `infra/modules/iam/outputs.tf`
