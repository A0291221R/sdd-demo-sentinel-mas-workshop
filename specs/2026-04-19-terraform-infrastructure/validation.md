# Validation — Phase 10: Terraform Infrastructure (Dev Environment)

_Branch: `phase-10-terraform-infrastructure` | Date: 2026-04-19_

---

## Automated checks

### Format

```bash
cd infra && terraform fmt -recursive -check
```

Must exit 0. All `.tf` files must be canonical Terraform format.

### Validation (no AWS credentials required)

```bash
cd infra && terraform init -backend=false && terraform validate
```

Must exit 0 with `Success! The configuration is valid.`

Run the same two commands inside each module directory independently:

```bash
for mod in modules/networking modules/iam modules/rds modules/sqs \
           modules/ecs modules/alb modules/codedeploy; do
  echo "=== $mod ===" && cd infra/$mod && terraform init -backend=false \
    && terraform validate && cd -
done
```

All must pass.

---

## Manual verification (requires AWS dev account)

### Bootstrap (one-time)

```bash
# Create S3 state bucket
aws s3api create-bucket \
  --bucket sentinel-mas-tf-state-$(aws sts get-caller-identity --query Account --output text) \
  --region ap-southeast-1 \
  --create-bucket-configuration LocationConstraint=ap-southeast-1

aws s3api put-bucket-versioning \
  --bucket sentinel-mas-tf-state-<account-id> \
  --versioning-configuration Status=Enabled

# Create DynamoDB lock table
aws dynamodb create-table \
  --table-name sentinel-mas-tf-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region ap-southeast-1
```

### Plan

```bash
cd infra
terraform init
terraform plan \
  -var="db_password=<secret>" \
  -var="domain_name=sentinel-dev.example.com"
```

Expected: plan completes with no errors; resource count matches the 7 modules.

### Apply

```bash
terraform apply \
  -var="db_password=<secret>" \
  -var="domain_name=sentinel-dev.example.com"
```

### Post-apply checks

| Check | Expected |
|-------|----------|
| ALB DNS name returned in outputs | Resolves in DNS within 1–2 min |
| RDS endpoint returned in outputs | Reachable from within VPC (use ECS exec or bastion) |
| SQS queue URL returned in outputs | Visible in AWS console, DLQ linked |
| ECR repos created | `api`, `central`, `ui` repos visible in ECR console |
| ECS cluster exists | `sentinel-dev` cluster with 3 services in ACTIVE state |
| CodeDeploy apps exist | `sentinel-api-dev` and `sentinel-central-dev` in console |
| Schema migration | Connect to RDS; verify `tasks` and `audit_log` tables exist |

### Traffic flow verification

1. Push placeholder Docker images to the ECR repos (any `nginx:alpine` will do)
2. Force new ECS deployments for all three services
3. `curl https://<alb_dns_name>/api/health` → `{"status":"ok"}`
4. `curl https://<alb_dns_name>/` → nginx default page (placeholder UI)
5. Submit a query via the ALB → verify it reaches the api service logs

---

## Edge cases

| Case | Expected behaviour |
|------|--------------------|
| `db_password` not set | `terraform plan` fails with missing variable error |
| S3 bucket doesn't exist | `terraform init` fails with backend config error |
| DynamoDB table doesn't exist | First `terraform apply` fails with state lock error |
| ALB cert validation pending | Apply completes; DNS CNAME must be manually added before HTTPS works |

---

## Definition of done

### Phase 10 gate (automated — no AWS credentials required)

- [ ] `terraform fmt -recursive -check` passes in `infra/`
- [ ] `terraform validate` passes in `infra/` with `-backend=false`
- [ ] `terraform validate` passes in each of the 7 module directories independently
- [ ] `infra/README.md` documents bootstrap steps clearly

### Full gate (requires AWS dev account)

- [ ] `terraform plan` completes with no errors
- [ ] `terraform apply` completes successfully
- [ ] All post-apply checks pass
- [ ] Traffic flow verification passes end-to-end
- [ ] `tasks` and `audit_log` tables exist in RDS after migration script
