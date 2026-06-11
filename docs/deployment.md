# Deployment

## Overview

The Personal Assistant Multi-Agent System runs entirely on AWS. The backend is a single ECS Fargate service hosting the LangGraph runtime and all agents. The frontend is a Next.js application served separately. All components are connected through an Application Load Balancer.

---

## Infrastructure Components

| Component | Service | Purpose |
|---|---|---|
| Frontend | Next.js (self-hosted or Vercel) | User interface |
| Load Balancer | AWS ALB | HTTPS termination, request routing |
| Backend Runtime | AWS ECS Fargate | LangGraph + all agents |
| LLM | Amazon Bedrock | Agent reasoning |
| Memory Store | Amazon DynamoDB | User preferences |
| Event Bus | Amazon EventBridge | Agent lifecycle events, audit trail |
| Secrets | AWS Secrets Manager | API credentials, tokens |
| Container Registry | Amazon ECR | Docker images |
| Logs & Metrics | Amazon CloudWatch | Observability |
| Tracing | AWS X-Ray | Distributed request tracing |

---

## System Architecture

```
Browser
  │
  ▼
AWS ALB  (HTTPS :443)
  ├── /api/*   → ECS Fargate (LangGraph backend)
  └── /*       → Next.js frontend

ECS Fargate Service
  └── LangGraph Runtime
        ├── Orchestrator Agent
        ├── Calendar Agent   → Microsoft Graph API
        ├── Travel Agent     → Flight Search API
        ├── Dining Agent     → Restaurant Search API
        ├── News Agent       → News API
        └── Companion Agent

Shared Services (within ECS)
  ├── Memory Service    → DynamoDB
  ├── Approval Service  → ALB callback / WebSocket
  └── Event Service     → EventBridge
```

---

## ECS Fargate Service

### Task Definition

```json
{
  "family": "multi-ai-agent-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "langgraph-runtime",
      "image": "<account>.dkr.ecr.<region>.amazonaws.com/multi-ai-agent:latest",
      "portMappings": [{ "containerPort": 8000, "protocol": "tcp" }],
      "environment": [
        { "name": "AWS_REGION", "value": "<region>" },
        { "name": "DYNAMODB_TABLE", "value": "user-preferences" },
        { "name": "EVENTBRIDGE_BUS", "value": "multi-ai-agent-events" }
      ],
      "secrets": [
        { "name": "MICROSOFT_GRAPH_CLIENT_SECRET", "valueFrom": "arn:aws:secretsmanager:..." },
        { "name": "FLIGHT_API_KEY", "valueFrom": "arn:aws:secretsmanager:..." },
        { "name": "RESTAURANT_API_KEY", "valueFrom": "arn:aws:secretsmanager:..." },
        { "name": "NEWS_API_KEY", "valueFrom": "arn:aws:secretsmanager:..." }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/multi-ai-agent",
          "awslogs-region": "<region>",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Scaling Policy

| Metric | Scale Out | Scale In |
|---|---|---|
| CPU utilization | > 70% for 2 min | < 30% for 5 min |
| Memory utilization | > 75% for 2 min | < 40% for 5 min |
| ALB request count | > 500 req/min | < 100 req/min |

Minimum tasks: **2** (one per Availability Zone for HA).  
Maximum tasks: **10**.

---

## Container Image

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build & Push

```bash
# Authenticate to ECR
aws ecr get-login-password --region <region> | \
  docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com

# Build
docker build -t multi-ai-agent .

# Tag
docker tag multi-ai-agent:latest \
  <account>.dkr.ecr.<region>.amazonaws.com/multi-ai-agent:latest

# Push
docker push <account>.dkr.ecr.<region>.amazonaws.com/multi-ai-agent:latest
```

---

## CI/CD Pipeline

```
Push to main
  │
  ▼
GitHub Actions
  ├── 1. Lint (ruff, eslint, prettier --check)
  ├── 2. Unit tests (pytest, vitest)
  ├── 3. Build Docker image
  ├── 4. Push to ECR
  └── 5. Deploy to ECS (rolling update)
        └── aws ecs update-service --force-new-deployment
```

### Rolling Deployment

ECS performs a rolling update with the following settings:
- **Minimum healthy percent**: 100% (no downtime)
- **Maximum percent**: 200% (new tasks start before old tasks stop)
- Health check grace period: 30 seconds

---

## Networking

```
VPC
  ├── Public Subnets  (2 AZs)
  │     └── ALB
  └── Private Subnets (2 AZs)
        └── ECS Fargate tasks
              └── NAT Gateway → Internet (for external APIs)
```

### Security Groups

| Group | Inbound | Outbound |
|---|---|---|
| ALB | 443 from 0.0.0.0/0 | 8000 to ECS SG |
| ECS tasks | 8000 from ALB SG | 443 to 0.0.0.0/0 (external APIs, Bedrock, DynamoDB) |

---

## IAM Roles

### ECS Task Role (runtime permissions)

```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "events:PutEvents",
        "secretsmanager:GetSecretValue",
        "xray:PutTraceSegments",
        "xray:PutTelemetryRecords"
      ],
      "Resource": "*"
    }
  ]
}
```

### ECS Task Execution Role (ECS agent permissions)

Attach the AWS managed policy `AmazonECSTaskExecutionRolePolicy`. Add a custom statement for ECR pull and CloudWatch Logs.

---

## DynamoDB

### Table: `user-preferences`

| Attribute | Type | Key |
|---|---|---|
| `user_id` | String | Partition key |

Billing mode: **On-demand** (pay per request).

No TTL — preferences persist indefinitely.

---

## Amazon Bedrock

The LangGraph runtime invokes Amazon Bedrock for all LLM calls.

- Model: configured via environment variable `BEDROCK_MODEL_ID` (e.g., `anthropic.claude-3-5-sonnet-20241022-v2:0`).
- Region: must match the ECS task region.
- Credentials: provided via the ECS task role (no API keys).

---

## Amazon EventBridge

### Event Bus: `multi-ai-agent-events`

All agent lifecycle and domain events are emitted here. See [langgraph-design.md](langgraph-design.md) for the full event schema.

Example rule — archive all events for audit:

```json
{
  "EventBusName": "multi-ai-agent-events",
  "EventPattern": { "source": ["multi-ai-agent"] },
  "Targets": [{ "Id": "archive", "Arn": "arn:aws:events:::archive/..." }]
}
```

---

## Secrets Management

All credentials are stored in AWS Secrets Manager. No credentials are passed as plaintext environment variables or logged.

| Secret Name | Contents |
|---|---|
| `multi-ai-agent/microsoft-graph` | `client_id`, `client_secret`, `tenant_id` |
| `multi-ai-agent/flight-api` | `api_key` |
| `multi-ai-agent/restaurant-api` | `api_key` |
| `multi-ai-agent/news-api` | `api_key` |

Secrets are injected into the container at task start via the ECS `secrets` field in the task definition. They are never written to environment variable files or committed to source control.

---

## Observability

### Logging

All logs go to CloudWatch Logs under `/ecs/multi-ai-agent`.

Log every:
- Incoming user request (user ID + session ID, no PII in message body)
- Intent detection result and confidence score
- Agent routing decision
- Tool invocations (name, success/failure, latency)
- Approval decisions
- Service errors with event code

Never log: raw message content, API credentials, user PII.

### Metrics (CloudWatch)

| Metric | Unit | Alarm threshold |
|---|---|---|
| `RequestCount` | Count | — |
| `OrchestratorLatency` | Milliseconds | > 10 000 ms |
| `AgentLatency` | Milliseconds | > 8 000 ms |
| `ToolErrorRate` | Percent | > 5% over 5 min |
| `ApprovalRate` | Percent | — |
| `LLMTokenUsage` | Count | — |

### Distributed Tracing (X-Ray)

Instrument with the AWS X-Ray SDK. Each request produces a trace spanning:

```
Request
  ├── Orchestrator (load_context → detect_intent → route_request)
  ├── Memory Service (DynamoDB GetItem)
  ├── Specialist Agent (reason → call_tools)
  ├── Tool (external API call)
  ├── Approval Service (if required)
  └── Response Builder
```

---

## Health Checks

### ALB Target Group

```
Protocol: HTTP
Path:     /health
Interval: 30s
Timeout:  5s
Healthy threshold:   2
Unhealthy threshold: 3
```

### `/health` endpoint response

```json
{ "status": "ok", "version": "1.0.0" }
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `AWS_REGION` | Yes | AWS region |
| `DYNAMODB_TABLE` | Yes | DynamoDB table name for user preferences |
| `EVENTBRIDGE_BUS` | Yes | EventBridge bus name |
| `BEDROCK_MODEL_ID` | Yes | Bedrock model identifier |
| `INTENT_CONFIDENCE_THRESHOLD` | No | Minimum confidence to route to a specialist (default: `0.7`) |
| `LOG_LEVEL` | No | `INFO` (default) or `DEBUG` |

Secrets (injected via ECS secrets, not env vars):

| Secret | Env var name |
|---|---|
| `multi-ai-agent/microsoft-graph` | `MICROSOFT_GRAPH_CLIENT_SECRET` |
| `multi-ai-agent/flight-api` | `FLIGHT_API_KEY` |
| `multi-ai-agent/restaurant-api` | `RESTAURANT_API_KEY` |
| `multi-ai-agent/news-api` | `NEWS_API_KEY` |

---

## Runbook

### Deploy a new version

```bash
# 1. Push image to ECR (see Build & Push above)
# 2. Force a new deployment
aws ecs update-service \
  --cluster multi-ai-agent \
  --service langgraph-backend \
  --force-new-deployment
# 3. Monitor rollout
aws ecs wait services-stable \
  --cluster multi-ai-agent \
  --services langgraph-backend
```

### Roll back

```bash
# Redeploy the previous task definition revision
aws ecs update-service \
  --cluster multi-ai-agent \
  --service langgraph-backend \
  --task-definition multi-ai-agent-backend:<previous-revision>
```

### Scale manually

```bash
aws ecs update-service \
  --cluster multi-ai-agent \
  --service langgraph-backend \
  --desired-count 4
```

### View live logs

```bash
aws logs tail /ecs/multi-ai-agent --follow
```

### Check service health

```bash
aws ecs describe-services \
  --cluster multi-ai-agent \
  --services langgraph-backend \
  --query 'services[0].{status:status,running:runningCount,desired:desiredCount,pending:pendingCount}'
```
