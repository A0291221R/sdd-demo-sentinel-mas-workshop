# Deployment

## How deployments work

Every merge to `main` triggers an automated deployment via GitHub Actions.
There is no manual deploy step for routine releases.

```
merge to main
  └─▶ GitHub Actions: build + test
  └─▶ Docker images pushed to ECR
  └─▶ New ECS task definition registered
  └─▶ CodeDeploy blue/green deployment started
        └─▶ Green tasks started
        └─▶ 10% canary traffic shifted to green
        └─▶ 10-minute bake period
        └─▶ If healthy: 100% traffic to green
        └─▶ If unhealthy: automatic rollback to blue
```

The deployment is complete when CodeDeploy reports `SUCCEEDED` and blue tasks
have been terminated. Total time from merge to full traffic shift is typically
15–20 minutes.

---

## Check deployment status

```bash
# List recent deployments for a service
aws deploy list-deployments \
  --application-name sentinel-mas-api \
  --deployment-group-name sentinel-mas-api-dg \
  --query 'deployments[0:5]'

# Get status of a specific deployment
aws deploy get-deployment \
  --deployment-id d-XXXXXXXXX \
  --query 'deploymentInfo.{status:status,errorInfo:errorInformation}'

# Watch ECS service events
aws ecs describe-services \
  --cluster sentinel-mas \
  --services sentinel-mas-api \
  --query 'services[0].events[0:10]'
```

---

## Manual rollback

### Automatic rollback (preferred)

CodeDeploy rolls back automatically if any CloudWatch alarm fires during the
bake period. No action required.

### Force rollback during bake

If the deployment is still in progress (canary or bake phase):

```bash
aws deploy stop-deployment \
  --deployment-id d-XXXXXXXXX \
  --auto-rollback-enabled
```

This stops traffic shift and restores the blue target group.

### Rollback after full cutover

If the deployment has fully completed but you need to revert:

1. Find the previous task definition revision:

```bash
aws ecs list-task-definitions \
  --family-prefix sentinel-mas-api \
  --sort DESC \
  --query 'taskDefinitionArns[0:5]'
```

2. Update the ECS service to the previous revision:

```bash
aws ecs update-service \
  --cluster sentinel-mas \
  --service sentinel-mas-api \
  --task-definition sentinel-mas-api:PREVIOUS_REVISION \
  --force-new-deployment
```

This bypasses CodeDeploy and triggers a rolling ECS update directly.

---

## Promote to production

Production deployments require a manual approval step.

1. Open GitHub Actions → **Deploy** workflow
2. Find the pending run for your merge
3. Click **Review deployments**
4. Select `production` and click **Approve and deploy**

The same blue/green process runs against the production ECS cluster.

Only engineers with the `prod-deploy` GitHub team membership can approve
production deployments.

---

## Environment variables and secrets

All secrets are stored in AWS Secrets Manager. They are injected into ECS
tasks at launch time — never stored in environment variables or image layers.

To update a secret:

```bash
aws secretsmanager update-secret \
  --secret-id sentinel-mas/prod/db-password \
  --secret-string '{"password":"new-value"}'
```

ECS tasks pick up the new value on next task launch. To force a refresh
without a code change:

```bash
aws ecs update-service \
  --cluster sentinel-mas \
  --service sentinel-mas-api \
  --force-new-deployment
```

---

## Infrastructure changes

All infrastructure changes go through Terraform. Never make manual changes
to tracked resources in the AWS console.

```bash
# Plan changes (always review before apply)
cd infra/terraform/environments/dev
terraform plan -out=tfplan

# Apply
terraform apply tfplan

# Target a single resource
terraform apply -target=module.ecs.aws_ecs_service.api
```

For production infrastructure changes, open a PR to `main` with the Terraform
diff. A second engineer must review and approve before merge.

---

## Smoke test after deployment

After a deployment completes, run the smoke test suite against the target
environment:

```bash
# Dev
BASE_URL=https://api.dev.sentinel-mas.internal make smoke

# Prod
BASE_URL=https://api.sentinel-mas.internal make smoke
```

Smoke tests cover:
- `GET /health` returns 200
- `GET /api/agents` returns agent list
- `POST /api/tasks` creates a task and returns a task ID
- WebSocket connection to UI dashboard connects and receives heartbeat

---

## Useful aliases

```bash
# Tail ECS service logs (replace SERVICE with api, ui, or central)
alias logs-sentinel='aws logs tail /ecs/sentinel-mas/SERVICE --follow'

# SSH into a running ECS task (requires ECS Exec enabled)
alias exec-sentinel='aws ecs execute-command \
  --cluster sentinel-mas \
  --task TASK_ID \
  --container SERVICE \
  --interactive \
  --command "/bin/sh"'
```
