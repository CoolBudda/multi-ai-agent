# ECS Fargate Runtime Implementation Plan

## 1. Goal
Direct restatement of the spec purpose: host the LangGraph backend and all agents in a single, scalable ECS Fargate service.

## 2. Scope Mapping
- Included: ECS task definition, Fargate service configuration, auto-scaling, health checks, and container image management.
- Excluded: Application code, CI/CD pipeline trigger logic.

## 3. File Changes
- agenterrafrom/modules/ecs/main.tf
- agenterrafrom/modules/ecs/variables.tf
- agenterrafrom/modules/ecs/outputs.tf
- agenterrafrom/modules/iam/main.tf
- agentservice/Dockerfile

## 4. LangGraph Nodes (if applicable)
- N/A

## 5. Tools
- Terraform
- AWS ECS Fargate
- AWS ECR

## 6. State Updates
- N/A

## 7. Implementation Steps (strict order)
1. Define ECS cluster resource.
2. Define ECS task execution role with permissions for ECR pull and Secrets Manager GetSecretValue.
3. Define ECS task role with DynamoDB permissions (from DynamoDB plan).
4. Define ECS task definition with family, cpu=1024, memory=2048, networkMode=awsvpc, container port 8000, secrets field referencing Secrets Manager ARNs, and log configuration to CloudWatch Logs.
5. Define ECS Fargate service with minimum 2 tasks, spread across two AZs, attached to ALB target group.
6. Define auto-scaling target and policies: scale out at CPU > 70%, memory > 75%, ALB req > 500/min; scale in at CPU < 30%.
7. Configure health check path GET /health on the ALB target group.
8. Define rolling deployment configuration with minimum healthy percent 100%.
9. Write agentservice/Dockerfile exposing port 8000 with health check endpoint.
10. Output ECS service name and cluster ARN for CI/CD pipeline consumption.

## 8. Dependencies
- Terraform (infrastructure-as-code plan must be implemented first)
- networking-load-balancing plan (VPC, subnets, ALB target group must exist)
- data-storage-dynamodb plan (task role IAM policy must exist)
- secrets-management plan (secret ARNs must exist)
- ECR repository with container image

## 9. Test Plan
- Unit tests: terraform validate for ecs module; Dockerfile builds successfully.
- Integration tests: terraform apply creates ECS cluster, task definition, and service with 2 tasks across 2 AZs; GET /health returns 200.
- Workflow tests: Rolling deployment with new image completes without dropping requests; failed health check halts deployment and preserves previous revision.

## 10. Acceptance Criteria Mapping
- FR-001 Run the LangGraph runtime and all agents as a single ECS Fargate service. -> Validate single ECS service runs with all agent code.
- FR-002 Scale the service based on CPU, memory, and request-count thresholds. -> Validate auto-scaling policies and thresholds are configured.
- FR-003 Maintain high availability across at least two Availability Zones. -> Validate minimum 2 tasks each placed in a distinct AZ.
- FR-004 Perform rolling deployments with zero downtime. -> Validate minimum healthy percent 100% and rolling update configuration.

## 11. Open Questions
- None identified from the current requirements.
