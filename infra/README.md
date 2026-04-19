# Sentinel MAS — Terraform Infrastructure

Terraform configuration for the Sentinel MAS dev environment on AWS.
Terraform 1.6+, AWS provider ~> 5.0.

---

## Bootstrap (one-time, manual)

The S3 state bucket and DynamoDB lock table must exist before `terraform init`.

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=ap-southeast-1

# S3 state bucket
aws s3api create-bucket \
  --bucket "sentinel-mas-tf-state-${ACCOUNT_ID}" \
  --region "${REGION}" \
  --create-bucket-configuration LocationConstraint="${REGION}"

aws s3api put-bucket-versioning \
  --bucket "sentinel-mas-tf-state-${ACCOUNT_ID}" \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-encryption \
  --bucket "sentinel-mas-tf-state-${ACCOUNT_ID}" \
  --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

# DynamoDB lock table
aws dynamodb create-table \
  --table-name sentinel-mas-tf-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region "${REGION}"
```

Then update `backend.tf`, replacing `<account-id>` with your actual account ID.

---

## Usage

```bash
cd infra

# Initialise (first time or after backend changes)
terraform init

# Preview changes
terraform plan \
  -var="db_password=<secret>" \
  -var="domain_name=sentinel-dev.example.com"

# Apply
terraform apply \
  -var="db_password=<secret>" \
  -var="domain_name=sentinel-dev.example.com"
```

---

## Schema migration

After the first `terraform apply`, run the migration script to create the
database tables:

```bash
psql "postgres://sentinel:<password>@$(terraform output -raw rds_endpoint)/sentinel" \
  -f scripts/migrate.sql
```

---

## ACM certificate validation

After `terraform apply`, the `acm_validation_cname` output contains the DNS
CNAME record that must be added to your domain's DNS to validate the
certificate. HTTPS will not work until this record is propagated.

```bash
terraform output acm_validation_cname
```

---

## Modules

| Module | Purpose |
|--------|---------|
| `networking` | VPC, subnets, IGW, NAT, security groups |
| `iam` | ECS task roles, execution role, CodeDeploy role |
| `rds` | PostgreSQL 15 RDS instance |
| `sqs` | Task queue + DLQ |
| `ecs` | ECR repos, ECS cluster, task definitions, services |
| `alb` | ALB, listeners, target groups, ACM certificate |
| `codedeploy` | Blue/green deployment groups for api and central |

---

## Validation (no AWS credentials required)

```bash
terraform init -backend=false
terraform validate
terraform fmt -recursive -check
```
