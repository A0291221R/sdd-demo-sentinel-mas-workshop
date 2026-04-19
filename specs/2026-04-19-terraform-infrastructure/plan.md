# Plan — Phase 10: Terraform Infrastructure (Dev Environment)

_Branch: `phase-10-terraform-infrastructure` | Date: 2026-04-19_

---

## Directory layout (target)

```
infra/
├── backend.tf
├── main.tf
├── variables.tf
├── outputs.tf
├── versions.tf
├── README.md
├── scripts/
│   └── migrate.sql
└── modules/
    ├── networking/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── iam/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── rds/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── sqs/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── ecs/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── alb/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    └── codedeploy/
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

---

## Task groups

Groups are independently completable and validateable. Run
`terraform validate && terraform fmt -check` inside each module directory
after completing it.

---

### Group 1 — Root scaffold

1.1 Create `infra/versions.tf`:
    - `terraform { required_version = "~> 1.6" }`
    - AWS provider `~> 5.0`, region from variable

1.2 Create `infra/backend.tf`:
    - S3 backend, bucket `sentinel-mas-tf-state-<account-id>` (placeholder),
      key `dev/terraform.tfstate`, region, encrypt = true
    - DynamoDB table `sentinel-mas-tf-locks`

1.3 Create `infra/variables.tf`:
    - `environment` (default `"dev"`)
    - `aws_region` (default `"ap-southeast-1"`)
    - `db_password` (sensitive, no default)
    - `domain_name` (no default — ALB certificate domain)

1.4 Create `infra/outputs.tf` (populated as modules are added):
    - `alb_dns_name`, `rds_endpoint`, `sqs_queue_url`, `ecr_api_url`,
      `ecr_central_url`, `ecr_ui_url`

1.5 Create `infra/README.md` with bootstrap instructions (S3 bucket +
    DynamoDB table creation commands).

---

### Group 2 — networking module

2.1 `aws_vpc` — CIDR `10.0.0.0/16`, DNS hostnames enabled

2.2 2 public subnets (`10.0.1.0/24`, `10.0.2.0/24`) across 2 AZs;
    2 private subnets (`10.0.10.0/24`, `10.0.11.0/24`)

2.3 `aws_internet_gateway`, `aws_eip` + `aws_nat_gateway` (in public subnet 1)

2.4 Route tables: public (0.0.0.0/0 → IGW), private (0.0.0.0/0 → NAT)

2.5 Security groups:
    - `alb_sg`: ingress 80/443 from 0.0.0.0/0; egress all
    - `app_sg`: ingress 8000 from `alb_sg`; egress all
    - `rds_sg`: ingress 5432 from `app_sg`

2.6 Outputs: `vpc_id`, `public_subnet_ids`, `private_subnet_ids`,
    `alb_sg_id`, `app_sg_id`, `rds_sg_id`

---

### Group 3 — iam module

3.1 ECS task execution role (trust: `ecs-tasks.amazonaws.com`):
    - `AmazonECSTaskExecutionRolePolicy` (managed)
    - Inline policy: ECR `GetAuthorizationToken`, Secrets Manager `GetSecretValue`

3.2 ECS task role for `api` service:
    - Inline policy: SQS `SendMessage` on the queue ARN (passed as variable)

3.3 ECS task role for `central` service:
    - Inline policy: SQS `ReceiveMessage`, `DeleteMessage`; RDS connect

3.4 CodeDeploy role (trust: `codedeploy.amazonaws.com`):
    - `AWSCodeDeployRoleForECS` (managed)

3.5 Outputs: `execution_role_arn`, `api_task_role_arn`,
    `central_task_role_arn`, `codedeploy_role_arn`

---

### Group 4 — rds module

4.1 `aws_db_subnet_group` using private subnets

4.2 `aws_db_parameter_group` for PostgreSQL 15

4.3 `aws_db_instance`:
    - engine `postgres`, engine_version `15`, instance class `db.t3.micro`
    - `allocated_storage = 20`, `storage_encrypted = true`
    - `db_name = "sentinel"`, username `sentinel`, password from variable
    - `skip_final_snapshot = true` (dev), `deletion_protection = false`
    - VPC security group: `rds_sg`

4.4 `infra/scripts/migrate.sql`:
    ```sql
    CREATE TABLE IF NOT EXISTS tasks (
        task_id     TEXT PRIMARY KEY,
        status      TEXT NOT NULL,
        intent      TEXT,
        agent_result JSONB,
        error       TEXT,
        created_at  TIMESTAMPTZ DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS audit_log (
        id          BIGSERIAL PRIMARY KEY,
        task_id     TEXT NOT NULL,
        entry       JSONB NOT NULL,
        created_at  TIMESTAMPTZ DEFAULT NOW()
    );
    ```

4.5 Outputs: `rds_endpoint`, `rds_port`, `db_name`

---

### Group 5 — sqs module

5.1 `aws_sqs_queue` (DLQ): `sentinel-dlq-<env>`, `message_retention_seconds = 1209600`

5.2 `aws_sqs_queue` (main): `sentinel-queue-<env>`,
    `visibility_timeout_seconds = 60`,
    `redrive_policy` → DLQ ARN, `maxReceiveCount = 3`

5.3 Outputs: `queue_url`, `queue_arn`, `dlq_arn`

---

### Group 6 — ecs module

6.1 `aws_ecr_repository` for `api`, `central`, `ui` (image_tag_mutability = MUTABLE,
    scan on push = true)

6.2 `aws_ecs_cluster` — `sentinel-<env>`

6.3 Task definition for `api`:
    - Fargate, CPU 256 / memory 512
    - Container image: ECR `api` repo (placeholder tag `latest`)
    - Port 8000, env vars: `QUEUE_URL`, `DATABASE_URL`
    - Task role: `api_task_role_arn`; execution role: `execution_role_arn`
    - CloudWatch log group `/ecs/sentinel-api-<env>`

6.4 Task definition for `central`:
    - Fargate, CPU 512 / memory 1024
    - Container image: ECR `central` repo
    - No port; env vars: `QUEUE_URL`, `DATABASE_URL`
    - Task role: `central_task_role_arn`

6.5 Task definition for `ui`:
    - Fargate, CPU 256 / memory 512
    - Container image: ECR `ui` repo (nginx serving static build)
    - Port 80

6.6 `aws_ecs_service` for each task definition:
    - `desired_count = 1`, `launch_type = "FARGATE"`
    - `network_configuration`: private subnets, `app_sg`
    - `deployment_controller = "CODE_DEPLOY"` for `api` and `central`

6.7 Outputs: `cluster_arn`, `api_service_name`, `central_service_name`,
    `ui_service_name`, `ecr_api_url`, `ecr_central_url`, `ecr_ui_url`

---

### Group 7 — alb module

7.1 `aws_lb` — internet-facing, `alb_sg`, public subnets

7.2 `aws_lb_target_group` for `api` (port 8000, protocol HTTP,
    health check `GET /health`)

7.3 `aws_lb_target_group` for `ui` (port 80, protocol HTTP,
    health check `GET /`)

7.4 `aws_lb_listener` port 80 — redirect to HTTPS

7.5 `aws_lb_listener` port 443 (HTTPS):
    - Default action: forward to `ui` TG
    - `aws_lb_listener_rule`: path `/api/*` → `api` TG (priority 10)

7.6 `aws_acm_certificate` + `aws_acm_certificate_validation` for `domain_name`
    (DNS validation — outputs the CNAME record for manual DNS entry)

7.7 Outputs: `alb_dns_name`, `alb_arn`, `api_tg_arn`, `ui_tg_arn`

---

### Group 8 — codedeploy module

8.1 `aws_codedeploy_app` for `api` (`compute_platform = "ECS"`)

8.2 `aws_codedeploy_app` for `central`

8.3 `aws_codedeploy_deployment_group` for `api`:
    - Blue/green ECS deployment
    - `deployment_config_name = "CodeDeployDefault.ECSCanary10Percent5Minutes"`
    - `auto_rollback_configuration`: enabled, event `DEPLOYMENT_FAILURE`
    - Bake time: 10 minutes via `terminate_blue_instances_on_deployment_success`
      (`action = "TERMINATE"`, `termination_wait_time_in_minutes = 10`)
    - References ALB listener ARN + target group names from alb module

8.4 `aws_codedeploy_deployment_group` for `central` (same pattern, no ALB)

8.5 Outputs: `api_deployment_group_name`, `central_deployment_group_name`

---

### Group 9 — Root module wiring

9.1 Update `infra/main.tf` to call all 7 modules, passing outputs as inputs:
    - networking → iam, rds, sqs, ecs, alb, codedeploy
    - iam → ecs, codedeploy
    - rds → ecs (DATABASE_URL env var)
    - sqs → iam (queue ARN for policies), ecs (QUEUE_URL env var)
    - alb → codedeploy (listener ARN, TG ARNs)

9.2 Update `infra/outputs.tf` with final root-level outputs.

---

### Group 10 — Validation

10.1 Run `terraform fmt -recursive` from `infra/`

10.2 Run `terraform validate` from `infra/` (requires `terraform init -backend=false`)

10.3 Confirm no fmt or validate errors across all modules.
