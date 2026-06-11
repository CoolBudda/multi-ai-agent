# Secrets Management Implementation Plan

## 1. Goal
Direct restatement of the spec purpose: store and inject external API credentials and sensitive configuration securely so they are never exposed in code, images, or logs.

## 2. Scope Mapping
- Included: AWS Secrets Manager secret definitions, ECS secrets injection, credential rotation, and access control.
- Excluded: Application-level credential usage (handled in service layer tools).

## 3. File Changes
- agenterrafrom/modules/secrets/main.tf
- agenterrafrom/modules/secrets/variables.tf
- agenterrafrom/modules/secrets/outputs.tf
- agenterrafrom/modules/iam/main.tf
- agentservice/.env.example

## 4. LangGraph Nodes (if applicable)
- N/A

## 5. Tools
- Terraform
- AWS Secrets Manager

## 6. State Updates
- N/A

## 7. Implementation Steps (strict order)
1. Define aws_secretsmanager_secret resources for multi-ai-agent/microsoft-graph, multi-ai-agent/flight-api, multi-ai-agent/restaurant-api, and multi-ai-agent/news-api.
2. Define aws_secretsmanager_secret_version placeholder values for each secret.
3. Define IAM policy document granting secretsmanager:GetSecretValue on all secret ARNs.
4. Attach the policy to the ECS task execution role.
5. Reference secret ARNs in the ECS task definition secrets field.
6. Output secret ARNs for ECS task definition consumption.
7. Document real credential injection process in agentservice/.env.example (no plaintext values).

## 8. Dependencies
- Terraform (infrastructure-as-code plan must be implemented first)
- IAM module (ECS task execution role must exist)
- ECS module (task definition secrets field)

## 9. Test Plan
- Unit tests: terraform validate for secrets module.
- Integration tests: terraform apply creates secrets; ECS task starts and environment variables are populated from Secrets Manager.
- Workflow tests: After secret rotation in Secrets Manager, a newly launched ECS task reads the updated value.

## 10. Acceptance Criteria Mapping
- FR-001 Store all external API credentials in AWS Secrets Manager. -> Validate all four secret resources are provisioned.
- FR-002 Inject secrets into the ECS container at task start via the ECS secrets field. -> Validate task definition secrets field references secret ARNs.
- FR-003 Support credential rotation without requiring a redeployment. -> Validate new ECS task picks up rotated secret value.
- FR-004 Never expose credentials in images, environment variable files, source control, or logs. -> Validate no plaintext credentials in source; validate CloudWatch logs contain no secret values.

## 11. Open Questions
- None identified from the current requirements.
