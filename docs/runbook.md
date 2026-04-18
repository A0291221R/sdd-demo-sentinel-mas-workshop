# Runbook

On-call reference for Sentinel MAS. Each section follows the same structure:
**symptom → diagnosis → remediation**.

---

## General diagnostics

Before investigating a specific issue, collect baseline state:

```bash
# ECS service health
aws ecs describe-services \
  --cluster sentinel-mas \
  --services sentinel-mas-api sentinel-mas-ui sentinel-mas-central \
  --query 'services[*].{name:serviceName,running:runningCount,desired:desiredCount,status:status}'

# Recent CloudWatch alarms
aws cloudwatch describe-alarms \
  --state-value ALARM \
  --query 'MetricAlarms[*].{name:AlarmName,reason:StateReason}'

# SQS queue depth
aws sqs get-queue-attributes \
  --queue-url https://sqs.REGION.amazonaws.com/ACCOUNT/sentinel-mas-tasks \
  --attribute-names ApproximateNumberOfMessages,ApproximateNumberOfMessagesNotVisible
```

---

## Incidents

### API service returning 5xx errors

**Symptoms**
- CloudWatch alarm `sentinel-mas-api-error-rate` in ALARM state
- Users see 500 or 503 from the dashboard

**Diagnose**

```bash
# Check recent error logs
aws logs filter-log-events \
  --log-group-name /ecs/sentinel-mas/api \
  --filter-pattern "ERROR" \
  --start-time $(date -d '15 minutes ago' +%s000)

# Check task health
aws ecs describe-tasks \
  --cluster sentinel-mas \
  --tasks $(aws ecs list-tasks --cluster sentinel-mas --service-name sentinel-mas-api --query 'taskArns' --output text)
```

**Remediate**

If tasks are crashing: check logs for the root cause. If it is a configuration
issue, update Secrets Manager and force a new deployment (see deployment.md).

If tasks are healthy but returning errors: check RDS connectivity.

```bash
# Test DB connectivity from a running task
aws ecs execute-command \
  --cluster sentinel-mas --task TASK_ID --container api \
  --interactive --command "python -c \"import asyncpg; print('ok')\""
```

If RDS is unreachable: check security group rules and RDS instance status.

---

### Central agent not processing tasks

**Symptoms**
- SQS queue depth rising
- `sentinel-mas-queue-depth` alarm in ALARM state
- Agent status dashboard shows agents idle

**Diagnose**

```bash
# Queue depth trend
aws cloudwatch get-metric-statistics \
  --namespace AWS/SQS \
  --metric-name ApproximateNumberOfMessagesVisible \
  --dimensions Name=QueueName,Value=sentinel-mas-tasks \
  --start-time $(date -d '1 hour ago' --iso-8601=seconds) \
  --end-time $(date --iso-8601=seconds) \
  --period 300 \
  --statistics Average

# Central agent logs
aws logs tail /ecs/sentinel-mas/central --follow
```

**Remediate**

If the central agent is crashing in a loop: check logs for the exception.
Common causes are LLM API key expiry or a malformed task in the queue.

To drain a poisoned message from the queue:

```bash
# Receive and delete the message (inspect body first)
aws sqs receive-message \
  --queue-url https://sqs.REGION.amazonaws.com/ACCOUNT/sentinel-mas-tasks \
  --max-number-of-messages 1

aws sqs delete-message \
  --queue-url ... \
  --receipt-handle RECEIPT_HANDLE
```

If the LLM API key has expired: rotate it in Secrets Manager and force a
new deployment of the central service.

---

### UI not loading

**Symptoms**
- Browser shows blank page or connection refused
- ALB health check alarm for UI target group

**Diagnose**

```bash
# Check UI task status
aws ecs describe-services \
  --cluster sentinel-mas --services sentinel-mas-ui \
  --query 'services[0].{running:runningCount,desired:desiredCount,events:events[0:3]}'

# Check ALB target health
aws elbv2 describe-target-health \
  --target-group-arn ARN_OF_UI_TARGET_GROUP
```

**Remediate**

If target health is `unhealthy`: check the UI task logs. The most common
cause is a failed asset build in the Docker image. Re-trigger the CI pipeline
to rebuild and redeploy.

If targets are healthy but UI is unreachable: check ALB listener rules to
confirm `/*` is routing to the correct target group. This can be misconfigured
after a failed blue/green swap.

---

### Deployment stuck in bake period

**Symptoms**
- GitHub Actions deployment step running for more than 20 minutes
- CodeDeploy console shows `IN_PROGRESS` with canary at 10%

**Diagnose**

The bake period will complete naturally at the 10-minute mark unless an alarm
fires. If it has been more than 15 minutes:

```bash
aws deploy get-deployment \
  --deployment-id d-XXXXXXXXX \
  --query 'deploymentInfo.{status:status,percentComplete:deploymentOverview}'
```

**Remediate**

If you need to abort:

```bash
aws deploy stop-deployment \
  --deployment-id d-XXXXXXXXX \
  --auto-rollback-enabled
```

If the alarm that triggered the hold is a false positive:

```bash
# Silence the alarm temporarily (15 minutes)
aws cloudwatch set-alarm-state \
  --alarm-name ALARM_NAME \
  --state-value OK \
  --state-reason "False positive — manually cleared during deployment bake"
```

---

### Sentinel policy rejecting legitimate tool calls

**Symptoms**
- Agents returning policy rejection errors in logs
- Operators report that valid queries are failing

**Diagnose**

```bash
# Filter policy rejection events
aws logs filter-log-events \
  --log-group-name /ecs/sentinel-mas/central \
  --filter-pattern "PolicyRejection"
```

Review the rejection records. Each record contains: agent name, requested
tool, rejection reason (unauthorised / rate limit / access control).

**Remediate**

If a rate limit is firing incorrectly: review the limit configuration in
`services/central/policy/sentinel_policy.py`. Increase the limit or adjust
the window, then redeploy.

If an access control rule is too restrictive: update the agent's permitted
tool list in `AGENT_REGISTRY` and redeploy.

Never disable the policy layer entirely — it is the primary security boundary
between agents and external systems.

---

## Escalation

| Severity | Condition | Action |
|----------|-----------|--------|
| P1 | API unavailable > 5 minutes | Page on-call lead |
| P2 | Error rate > 5% for > 10 minutes | Slack `#sentinel-incidents` |
| P3 | Queue depth > 1000 messages | Slack `#sentinel-alerts`, investigate during business hours |
| P4 | Single agent failing | Log ticket, no immediate action required |

---

## Useful dashboards

- **ECS service health**: CloudWatch → Dashboards → `sentinel-mas-overview`
- **API latency and errors**: CloudWatch → Dashboards → `sentinel-mas-api`
- **SQS queue depth**: CloudWatch → Dashboards → `sentinel-mas-queues`
- **X-Ray traces**: X-Ray → Service map → filter by `sentinel-mas`
