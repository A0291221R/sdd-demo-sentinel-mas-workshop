# Requirements — Phase 10: Terraform Infrastructure (Dev Environment)

_Branch: `phase-10-terraform-infrastructure` | Date: 2026-04-19_

---

## Scope

### Included

All seven Terraform modules for the dev AWS environment under `infra/`:

| Module | Resources |
|--------|-----------|
| `networking` | VPC, 2 public + 2 private subnets, IGW, NAT gateway, route tables, security groups |
| `iam` | ECS task execution role, ECS task role (per service), CodeDeploy role, ECR pull policy |
| `rds` | PostgreSQL 15 RDS instance (db.t3.micro), subnet group, parameter group, schema migration via `psql` |
| `sqs` | Standard queue + dead-letter queue (maxReceiveCount = 3), queue policy |
| `ecs` | ECS cluster, task definitions for `api`, `central`, and `ui` services, Fargate services with desired count = 1 |
| `alb` | ALB, HTTPS listener (port 443), HTTP → HTTPS redirect, target groups, listener rules: `/api/*` → api TG, `/*` → ui TG |
| `codedeploy` | CodeDeploy app, blue/green deployment group for `api` and `central`, 10-minute bake, auto-rollback on alarm |

### Root module

- `infra/main.tf` — wires all modules, passes outputs between them
- `infra/variables.tf` — `environment`, `aws_region`, `db_password` (sensitive), `domain_name`
- `infra/outputs.tf` — ALB DNS name, RDS endpoint, SQS queue URL, ECR repo URLs
- `infra/backend.tf` — S3 remote state with DynamoDB locking
- `infra/versions.tf` — Terraform `~> 1.6`, AWS provider `~> 5.0`

### Bootstrap (manual, one-time)

Before `terraform init`, an operator must create:
1. S3 bucket for state: `sentinel-mas-tf-state-<account-id>`
2. DynamoDB table for locking: `sentinel-mas-tf-locks` (partition key: `LockID`)

These are documented in `infra/README.md` — not managed by Terraform to avoid
the chicken-and-egg problem.

### Not included

- `prod` Terraform workspace — Phase 12
- CI/CD pipeline triggering Terraform — Phase 11
- Secrets Manager entries for prod credentials — Phase 12
- LocalStack configuration — explicitly out of scope (AWS dev account only)
- Docker Compose local stack — pre-existing; not modified in this phase
- Actual `terraform apply` to a live account — the deliverable is
  reviewable, `terraform validate`-passing HCL; applying requires AWS
  credentials outside this session

---

## Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Module structure | One directory per module under `infra/modules/` | Mirrors Terraform best-practice; independently reusable per module |
| State backend | S3 + DynamoDB | AWS-native; team-safe locking; no external dependency |
| Workspace strategy | `default` = dev, `prod` workspace in Phase 12 | Keeps dev simple; `terraform.workspace` drives resource naming |
| RDS sizing | db.t3.micro, single-AZ for dev | Cost-appropriate for dev; Multi-AZ in prod (Phase 12) |
| ECS launch type | Fargate | No node management; matches tech-stack.md |
| Container images | ECR repos per service (`api`, `central`, `ui`) | Co-located with ECS; CI pushes images in Phase 11 |
| ALB routing | Path-based: `/api/*` → api, `/*` → ui | Matches tech-stack.md ALB spec |
| CodeDeploy bake | 10-minute canary | Matches tech-stack.md specification |
| Schema migration | One-time `psql` script in `infra/scripts/migrate.sql` | Keeps Terraform pure HCL; no migration tool dependency until Phase 12 |
| Secrets | `db_password` as Terraform variable (sensitive); Secrets Manager in Phase 12 | Sufficient for dev; prod hardening deferred |

---

## Context

- **Stack**: Terraform 1.6+, AWS provider ~> 5.0, AWS-only (no LocalStack)
- **Services**: `services/api/` (FastAPI, port 8000), `services/central/` (consumer, no HTTP port), `services/ui/` (Vite static, port 80 via nginx)
- **QUEUE_URL** consumed by `api` and `central` — sourced from SQS module output
- **RDS endpoint** consumed by `api` and `central` — sourced from RDS module output (Phase 10 wires the env vars; actual RDS persistence code is Phase 12)
- **Existing patterns**: no existing Terraform in the repo; this is the first IaC layer
- **Validation gate**: `terraform validate` and `terraform fmt -check` in each module; no `terraform plan` required (needs live AWS credentials)
