# Infrastructure as Code

## Purpose
Define all AWS infrastructure resources in version-controlled IaC so environments can be reproduced consistently and changes follow the same review process as application code.

## Scope
IaC definitions for ECS, ALB, DynamoDB, EventBridge, Secrets Manager, VPC, IAM roles, and CloudWatch alarms.

## Requirements
- All AWS resources are defined in IaC.
- Running the IaC apply command on a clean AWS account creates a fully functioning environment.
- Infrastructure changes go through CI review before being applied.
- IaC definitions live in the same repository as application code.

## Inputs
- IaC tool: **Terraform**.
- AWS account and region configuration.
- Application-specific resource parameters (table names, image URIs, secret ARNs).

## Outputs
- Provisioned AWS environment matching the IaC definition.
- Change plan output before apply.
- Applied infrastructure state.

## Business Rules
- No AWS resources are created or modified manually outside of IaC.
- IaC changes require a pull request and passing CI checks before merge.
- Sensitive values (credentials, account IDs) must not be committed in plaintext; use parameter stores or IaC secrets backends.

## Workflow
1. Developer modifies a Terraform `.tf` file.
2. CI runs `terraform plan` to preview changes.
3. Pull request review covers both code and infrastructure changes.
4. On merge, CI runs `terraform apply` to apply changes to the target environment.
5. Change is visible in the Terraform state and AWS console.

## Data Model
- IaC resources: VPC, subnets, ALB, ECS cluster, ECS task definition, ECS service, DynamoDB table, EventBridge bus, Secrets Manager secrets, IAM roles, CloudWatch alarms.

## Error Handling
- If the IaC apply fails partway, the tool must roll back or surface the partial state clearly so it can be resolved.
- IaC drift (manual changes) must be detected and reported.

## Acceptance Criteria
- A clean AWS account can be fully provisioned from the IaC definitions.
- Infrastructure changes require a pull request and CI check.
- All resources defined in IaC match the running environment state.

## Open Questions
- None. Terraform is the selected IaC tool.
