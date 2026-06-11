# Observability Implementation Plan

## 1. Goal
Direct restatement of the spec purpose: give operators and developers the visibility needed to diagnose issues, monitor performance, and trace requests through the multi-agent system.

## 2. Scope Mapping
- Included: Structured CloudWatch logging, CloudWatch metrics and alarms, and AWS X-Ray distributed tracing.
- Excluded: Application business logic, frontend monitoring.

## 3. File Changes
- agenterrafrom/modules/cloudwatch/main.tf
- agenterrafrom/modules/cloudwatch/variables.tf
- agenterrafrom/modules/cloudwatch/outputs.tf
- agentservice/src/api/main.py
- agentservice/src/graph/main_graph.py
- agentservice/src/agents/orchestrator_agent.py

## 4. LangGraph Nodes (if applicable)
- N/A

## 5. Tools
- AWS CloudWatch
- AWS X-Ray
- AWS SNS

## 6. State Updates
- request_id
- user_id
- agent_name
- intent
- tool_name
- latency_ms
- error_code

## 7. Implementation Steps (strict order)
1. Define CloudWatch Logs log group /ecs/multi-ai-agent in Terraform.
2. Configure ECS task definition to forward container stdout to the log group.
3. Implement structured log emission in agentservice: each log line includes request_id, user_id (no PII), agent, intent, tool, latency_ms, error_code; no raw message content or credentials.
4. Define CloudWatch custom metrics: OrchestratorLatency, AgentLatency, ToolErrorRate, ApprovalRate, LLMTokenUsage.
5. Define CloudWatch alarms: Orchestrator p99 latency > 10000ms, tool error rate > 5% over 5 min, ECS task count < minimum desired.
6. Define SNS topic and subscription for alarm notifications.
7. Instrument orchestrator and agent nodes with X-Ray SDK: segments for load_context, detect_intent, route_request, specialist agent nodes, tool calls, and build_response.
8. Validate no raw message content, credentials, or PII appears in log output.

## 8. Dependencies
- ECS Fargate runtime plan (log group attached to ECS task)
- CloudWatch module in Terraform

## 9. Test Plan
- Unit tests: Structured log format validation; X-Ray segment naming; metric emission.
- Integration tests: CloudWatch log stream receives entries; alarms trigger SNS on threshold breach.
- Workflow tests: X-Ray trace shows full request path from Orchestrator through agent nodes and tool calls.

## 10. Acceptance Criteria Mapping
- FR-001 All ECS container logs go to CloudWatch Logs in structured format. -> Validate log stream /ecs/multi-ai-agent receives structured entries.
- FR-002 CloudWatch metrics track the required dimensions. -> Validate all five metric names are emitted per request.
- FR-003 Alarms notify operators when thresholds are breached. -> Validate alarm fires and SNS notification is delivered on threshold breach.
- FR-004 X-Ray traces span the full request lifecycle. -> Validate X-Ray trace includes all required segment names.

## 11. Open Questions
- None identified from the current requirements.
