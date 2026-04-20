# Sentinel MAS — Production Runbook

---

## On-call contacts and escalation

| Role | Contact |
|------|---------|
| Primary on-call | Check PagerDuty rotation |
| Escalation | chekeong82@gmail.com |

---

## Health checks

**ALB target groups**
```bash
aws elbv2 describe-target-health \
  --target-group-arn $(aws elbv2 describe-target-groups \
    --names sentinel-prod-api-tg-blue --query 'TargetGroups[0].TargetGroupArn' --output text)
```
Healthy targets should show `State.State = healthy`.

**ECS service events**
```bash
aws ecs describe-services \
  --cluster sentinel-prod \
  --services sentinel-prod-api sentinel-prod-central \
  --query 'services[*].{name:serviceName,running:runningCount,desired:desiredCount,events:events[0:3]}'
```

**RDS status**
```bash
aws rds describe-db-instances \
  --db-instance-identifier sentinel-prod-postgres \
  --query 'DBInstances[0].{Status:DBInstanceStatus,Class:DBInstanceClass}'
```

---

## Manual CodeDeploy rollback

Use when the current deployment is unhealthy and auto-rollback has not triggered.

```bash
# Find the last successful deployment ID
aws deploy list-deployments \
  --application-name sentinel-prod-api \
  --deployment-group-name sentinel-prod-api-dg \
  --include-only-statuses Succeeded \
  --query 'deployments[0]' --output text

# Stop the current in-progress deployment
aws deploy stop-deployment \
  --deployment-id <current-deployment-id> \
  --auto-rollback-enabled

# If auto-rollback does not trigger, create a manual rollback deployment
aws deploy create-deployment \
  --application-name sentinel-prod-api \
  --deployment-group-name sentinel-prod-api-dg \
  --previous-revision-id <last-good-revision-id>
```

---

## Anthropic API key rotation

1. Generate a new key at console.anthropic.com.

2. Update the secret value:
   ```bash
   aws secretsmanager put-secret-value \
     --secret-id sentinel-prod-anthropic-api-key \
     --secret-string "<new-key>"
   ```

3. Force ECS to pick up the new secret:
   ```bash
   aws ecs update-service \
     --cluster sentinel-prod \
     --service sentinel-prod-central \
     --force-new-deployment
   ```

4. Revoke the old key in the Anthropic console after confirming the new tasks are healthy.

---

## Promoting dev image to prod

1. Find the commit SHA of the image to promote:
   ```bash
   aws ecr describe-images \
     --repository-name sentinel-dev-api \
     --query 'imageDetails[?contains(imageTags,`latest`)].imageTags'
   ```

2. Copy the image tag to the prod ECR repository:
   ```bash
   MANIFEST=$(aws ecr batch-get-image \
     --repository-name sentinel-dev-api \
     --image-ids imageTag=<sha> \
     --query 'images[0].imageManifest' --output text)

   aws ecr put-image \
     --repository-name sentinel-prod-api \
     --image-tag <sha> \
     --image-manifest "$MANIFEST"
   ```

3. Trigger the deploy workflow manually via GitHub Actions:
   ```bash
   gh workflow run deploy.yml \
     --ref main \
     -f image_tag=<sha> \
     -f environment=prod
   ```

---

## Emergency stop (scale to zero)

Use only during a confirmed incident to stop all traffic processing.

```bash
aws ecs update-service --cluster sentinel-prod --service sentinel-prod-api     --desired-count 0
aws ecs update-service --cluster sentinel-prod --service sentinel-prod-central --desired-count 0
```

To restore:
```bash
aws ecs update-service --cluster sentinel-prod --service sentinel-prod-api     --desired-count 1
aws ecs update-service --cluster sentinel-prod --service sentinel-prod-central --desired-count 1
```
