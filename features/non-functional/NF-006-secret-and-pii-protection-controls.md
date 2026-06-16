# NF-006: Secret and PII Protection Controls

## Type
Non-Functional

## Description
Credentials must be stored in AWS Secrets Manager and never passed as plaintext configuration or logged. Runtime logging must exclude raw user PII and secrets.

## Requirement Trace
- Source File: docs/deployment.md
- Source Reference: Secrets Management section and Observability > Logging rules ("Never log: raw message content, API credentials, user PII").

## Notes
- Secrets are injected via ECS task definition `secrets` entries.
