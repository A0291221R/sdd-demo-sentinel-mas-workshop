# ADR 001 — ECS Fargate over Kubernetes

**Date:** 2025-10-01
**Status:** Accepted

---

## Context

Sentinel MAS needs a container orchestration platform. The two realistic
options for an AWS-first stack were ECS Fargate and Kubernetes (EKS).

The team is two to three engineers. The system runs three services at moderate
traffic. There is no requirement for multi-cloud portability.

## Decision

Use **ECS Fargate**.

## Reasoning

ECS Fargate eliminates node management entirely. There are no EC2 instances
to patch, no kubelet to operate, and no control plane to version. For a
small team with an AWS-only requirement, this removes an entire category of
operational burden.

ECS integrates natively with CodeDeploy blue/green, IAM task roles, Secrets
Manager injection, and CloudWatch — all services already in the stack. Kubernetes
equivalents (IRSA, External Secrets Operator, Prometheus) require additional
components and expertise.

Kubernetes would be appropriate if any of the following became true:
- Multi-cloud deployment is required
- The team grows to a size where dedicated platform engineering is feasible
- Traffic patterns require horizontal pod autoscaling at sub-minute granularity

## Consequences

- No node cost visibility — Fargate pricing is per vCPU and memory per second
- Container startup is slower than EC2-backed ECS (~30s cold start vs ~5s)
- Advanced scheduling (bin packing, affinity rules) is not available
- Migration to Kubernetes later would require rewriting task definitions as manifests
