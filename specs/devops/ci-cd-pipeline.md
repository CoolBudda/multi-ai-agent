# CI/CD Pipeline

## Purpose
Automate linting, testing, container image build, and ECS deployment on every push to the main branch.

## Scope
GitHub Actions workflow, lint and test gates, Docker build and ECR push, ECS rolling deployment, and deployment status reporting.

## Requirements
- Run ESLint, Prettier check, Pytest, and Vitest on every push.
- Block the build if any lint or test step fails.
- On success, build a Docker image, push it to ECR, and deploy to ECS via rolling update.
- Report success or failure status on the commit.

## Inputs
- Source code push to the main branch.
- ECR repository URL.
- ECS cluster and service names.
- AWS credentials (via GitHub OIDC or IAM role).

## Outputs
- Lint and test results.
- Built and tagged Docker image in ECR.
- Updated ECS service with the new image.
- Commit status check result.

## Business Rules
- A failing lint or test step must block image build and deployment.
- Rolling deployment must use `--force-new-deployment` with minimum healthy percent 100%.
- No credentials are stored as plaintext GitHub secrets where OIDC federation is available.

## Workflow
1. Push to main triggers the pipeline.
2. Run `eslint`, `prettier --check`, `pytest`, `vitest`.
3. If all pass, build the Docker image.
4. Authenticate to ECR and push the image.
5. Update the ECS service to deploy the new image.
6. Wait for service stability and report status.

## Data Model
- Pipeline stages: `lint-and-test`, `build`, `push`, `deploy`.
- Docker image tag: `git-sha` or `latest`.

## Error Handling
- Lint or test failure stops the pipeline immediately and marks the commit as failed.
- If the ECS deploy fails health checks, ECS halts the rollout and preserves the previous revision.
- Alert the team on pipeline failure.

## Acceptance Criteria
- Every push to main triggers lint, test, build, push, and deploy in sequence.
- A failing lint or test prevents deployment.
- A successful deploy updates the running ECS service.
- The pipeline status is visible on the commit.

## Open Questions
- None identified from the current requirements.
