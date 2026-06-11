# Secrets Management

## Purpose
Store and inject external API credentials and sensitive configuration securely so they are never exposed in code, images, or logs.

## Scope
AWS Secrets Manager secret definitions, ECS secrets injection, credential rotation, and access control.

## Requirements
- Store all external API credentials in AWS Secrets Manager.
- Inject secrets into the ECS container at task start via the ECS secrets field.
- Support credential rotation without requiring a redeployment.
- Never expose credentials in container images, environment variable files, source control, or logs.

## Inputs
- Secrets Manager secret ARNs.
- ECS task definition secrets configuration.
- Rotated credential values.

## Outputs
- Secrets available as environment variables inside the running container.
- Updated secret values picked up by new ECS tasks after rotation.

## Business Rules
- Secrets are injected via the ECS task definition `secrets` field — not environment variable files.
- The ECS task execution role must have `secretsmanager:GetSecretValue` on the relevant secret ARNs.
- Credentials must never appear in application logs.
- After a secret is rotated in Secrets Manager, new ECS tasks pick up the updated value on the next task start.

## Workflow
1. A secret is created or rotated in Secrets Manager.
2. The ECS task definition references the secret ARN in the `secrets` field.
3. At task start, ECS pulls the current secret value and injects it as an environment variable.
4. The application reads the credential from the environment variable at runtime.

## Data Model
- `multi-ai-agent/microsoft-graph`: `{ client_id, client_secret, tenant_id }`
- `multi-ai-agent/flight-api`: `{ api_key }`
- `multi-ai-agent/restaurant-api`: `{ api_key }`
- `multi-ai-agent/news-api`: `{ api_key }`

## Error Handling
- If Secrets Manager is unavailable at task start, the ECS task fails to launch rather than starting without credentials.
- Failed secret retrieval must not fall back to a hardcoded value.

## Acceptance Criteria
- All external API credentials are stored in Secrets Manager and absent from source code and images.
- Credentials are available inside the container at runtime via environment variables.
- After rotating a secret, a newly launched ECS task uses the updated value.
- Credentials never appear in CloudWatch logs.

## Open Questions
- None identified from the current requirements.
