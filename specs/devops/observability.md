# Observability

## Purpose
Give operators and developers the visibility needed to diagnose issues, monitor performance, and trace requests through the multi-agent system.

## Scope
Structured CloudWatch logging, CloudWatch metrics and alarms, and AWS X-Ray distributed tracing.

## Requirements
- All ECS container logs go to CloudWatch Logs in structured format.
- CloudWatch metrics track request count, agent latency, tool error rate, approval rate, and LLM token usage.
- Alarms notify operators when latency, error rate, or task count breach thresholds.
- X-Ray traces span the full request lifecycle from Orchestrator through all agent nodes and tool calls.

## Inputs
- Application log output from the ECS container.
- CloudWatch metric data.
- X-Ray trace segments from instrumented code.

## Outputs
- CloudWatch log streams under `/ecs/multi-ai-agent`.
- CloudWatch alarms with SNS notifications.
- X-Ray service map and trace details.

## Business Rules
- Logs must include: request ID, user ID (no raw PII), agent name, intent, tool name, latency, error codes.
- Logs must never contain raw message content, API credentials, or user PII.
- Alarms: Orchestrator p99 latency > 10 000 ms; tool error rate > 5% over 5 min; ECS task count < minimum desired.
- Each X-Ray trace must include segments for: `load_context`, `detect_intent`, `route_request`, specialist agent nodes, tool calls, and `build_response`.

## Workflow
1. Application emits structured log lines to stdout.
2. CloudWatch Logs agent captures and streams to `/ecs/multi-ai-agent`.
3. CloudWatch Metrics receive custom metric data from the application.
4. Alarm rules evaluate metrics on schedule; SNS notifies on breach.
5. X-Ray SDK records trace segments at instrumented code points.
6. Traces are visible in the X-Ray console with the full request path.

## Data Model
- Log record: `{ timestamp, level, request_id, user_id, agent, intent, tool, latency_ms, error_code }`
- Metric names: `OrchestratorLatency`, `AgentLatency`, `ToolErrorRate`, `ApprovalRate`, `LLMTokenUsage`.
- Alarm thresholds defined in CloudWatch alarm resources.

## Error Handling
- If the CloudWatch Logs agent fails, container logs are still written to stdout for manual retrieval.
- If X-Ray is unavailable, the application continues to function; tracing is best-effort.

## Acceptance Criteria
- All ECS container logs appear in CloudWatch Logs without PII or credentials.
- CloudWatch alarms fire and deliver SNS notifications when thresholds are breached.
- X-Ray traces show the full request path including all agent and tool segments.

## Open Questions
- None identified from the current requirements.
