# CI/CD Pipeline Implementation Plan

## 1. Goal
Direct restatement of the spec purpose: automate linting, testing, container image build, and ECS deployment on every push to the main branch.

## 2. Scope Mapping
- Included: GitHub Actions workflow, lint and test gates, Docker build and ECR push, ECS rolling deployment, and deployment status reporting.
- Excluded: Infrastructure provisioning (covered by infrastructure-as-code plan).

## 3. File Changes
- .github/workflows/ci-cd.yml

## 4. LangGraph Nodes (if applicable)
- N/A

## 5. Tools
- GitHub Actions
- ESLint
- Prettier
- Pytest
- Vitest
- Docker
- AWS ECR
- AWS ECS

## 6. State Updates
- N/A

## 7. Implementation Steps (strict order)
1. Define GitHub Actions workflow triggered on push to main.
2. Implement lint-and-test job: run eslint, prettier --check, pytest, and vitest; fail fast on any failure.
3. Gate build job on lint-and-test job success.
4. Implement build job: build Docker image tagged with git SHA.
5. Implement ECR push step: authenticate with AWS OIDC and push image to ECR.
6. Implement deploy step: update ECS service with --force-new-deployment and minimum healthy percent 100%.
7. Implement wait-for-stability step and report commit status on success or failure.
8. Ensure no plaintext AWS credentials are stored; use GitHub OIDC federation.

## 8. Dependencies
- ECS Fargate runtime plan (ECS cluster and service must exist)
- ECR repository (must exist before image push)
- GitHub OIDC IAM role (must be configured in AWS)

## 9. Test Plan
- Unit tests: Workflow syntax validated with act or actionlint.
- Integration tests: Push to main triggers pipeline; lint failure blocks deploy; successful push deploys new image to ECS.
- Workflow tests: Failed ECS health check halts rollout and preserves previous revision; commit status reflects pipeline result.

## 10. Acceptance Criteria Mapping
- FR-001 Run ESLint, Prettier check, Pytest, and Vitest on every push. -> Validate all four steps are present in lint-and-test job.
- FR-002 Block the build if any lint or test step fails. -> Validate build job depends on lint-and-test and fails fast.
- FR-003 On success, build a Docker image, push it to ECR, and deploy to ECS via rolling update. -> Validate build, push, and deploy steps run in sequence after passing tests.
- FR-004 Report success or failure status on the commit. -> Validate commit status check is set at pipeline end.

## 11. Open Questions
- None identified from the current requirements.
