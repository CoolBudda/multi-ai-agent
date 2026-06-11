# Infrastructure as Code Implementation Plan

## 1. Goal
Direct restatement of the spec purpose: define all AWS infrastructure resources in version-controlled IaC so environments can be reproduced consistently and changes follow the same review process as application code.

## 2. Scope Mapping
- Included: IaC definitions for ECS, ALB, DynamoDB, EventBridge, Secrets Manager, VPC, IAM roles, and CloudWatch alarms.
- Excluded: Application code, non-AWS resources.

## 3. File Changes
- agenterrafrom/main.tf
- agenterrafrom/variables.tf
- agenterrafrom/outputs.tf
- agenterrafrom/modules/vpc/main.tf
- agenterrafrom/modules/dynamodb/main.tf
- agenterrafrom/modules/ecs/main.tf
- agenterrafrom/modules/alb/main.tf
- agenterrafrom/modules/iam/main.tf
- agenterrafrom/modules/secrets/main.tf
- agenterrafrom/modules/cloudwatch/main.tf
- agenterrafrom/environments/dev/main.tf
- agenterrafrom/environments/dev/terraform.tfvars

## 4. LangGraph Nodes (if applicable)
- N/A

## 5. Tools
- Terraform

## 6. State Updates
- N/A

## 7. Implementation Steps (strict order)
1. Define provider and backend configuration in agenterrafrom/main.tf.
2. Define input variables for AWS account, region, and resource parameters.
3. Implement VPC module with public and private subnets across two AZs.
4. Implement DynamoDB module with user-preferences table and IAM policy.
5. Implement Secrets Manager module with all required secret definitions.
6. Implement IAM module with ECS task role and task execution role.
7. Implement ECS module with cluster, task definition, and service.
8. Implement ALB module with HTTPS listener and target group rules.
9. Implement CloudWatch module with log groups, metric alarms, and SNS topics.
10. Implement outputs for all resource ARNs and endpoints.
11. Define dev environment composition in environments/dev/main.tf.
12. Validate with terraform plan on a clean AWS account.

## 8. Dependencies
- Terraform >= 1.6.0
- AWS provider ~> 5.0
- AWS account with required permissions

## 9. Test Plan
- Unit tests: terraform validate for each module.
- Integration tests: terraform plan on clean account produces zero errors.
- Workflow tests: terraform apply on clean account provisions all required resources.

## 10. Acceptance Criteria Mapping
- FR-001 All AWS resources are defined in IaC. -> Validate each required resource has a corresponding Terraform resource block.
- FR-002 Running IaC apply on a clean account creates a fully functioning environment. -> Validate apply completes with no errors on clean account.
- FR-003 Infrastructure changes go through CI review before being applied. -> Validate CI runs terraform plan on pull request.
- FR-004 IaC definitions live in the same repository as application code. -> Validate agenterrafrom/ is present in the repository root.

## 11. Open Questions
- None. Terraform is the selected IaC tool.
