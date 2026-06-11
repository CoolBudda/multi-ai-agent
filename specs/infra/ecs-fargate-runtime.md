# ECS Fargate Runtime

## Purpose
Host the LangGraph backend and all agents in a single, scalable ECS Fargate service.

## Scope
ECS task definition, Fargate service configuration, auto-scaling, health checks, and container image management.

## Requirements
- Run the LangGraph runtime and all agents as a single ECS Fargate service.
- Scale the service based on CPU, memory, and request-count thresholds.
- Maintain high availability across at least two Availability Zones.
- Perform rolling deployments with zero downtime.

## Inputs
- Docker container image from ECR.
- Task definition (CPU, memory, port mappings, environment variables, secrets).
- ALB target group health check configuration.

## Outputs
- Running ECS service with desired task count.
- ALB target group registration.
- Auto-scaling actions on threshold breach.

## Business Rules
- Minimum 2 tasks running at all times (one per AZ).
- Maximum 10 tasks under auto-scaling.
- Rolling deployment must maintain 100% minimum healthy percent.
- Health check path: `GET /health` → 200 OK.
- All secrets must be sourced from AWS Secrets Manager; no plaintext in task definition environment variables.

## Workflow
1. CI/CD pushes a new image to ECR.
2. ECS task definition is updated to reference the new image.
3. `ecs update-service --force-new-deployment` triggers a rolling update.
4. New tasks start and pass health checks.
5. Old tasks are drained and stopped.

## Data Model
- Task definition fields: `family`, `cpu` (1024), `memory` (2048), `networkMode` (awsvpc), container port 8000.
- Auto-scaling: scale out at CPU > 70%, memory > 75%, ALB req > 500/min; scale in at CPU < 30%.

## Error Handling
- If a new task fails health checks, the deployment stops and the previous revision remains active.
- If the service task count drops below the minimum, trigger an alarm and attempt to restore desired count.

## Acceptance Criteria
- The ECS service runs on Fargate with at least 2 tasks across 2 AZs.
- Auto-scaling adds tasks when CPU or request thresholds are exceeded.
- Rolling deployments complete without dropping requests.
- A failed deployment preserves the previous stable revision.

## Open Questions
- None identified from the current requirements.
