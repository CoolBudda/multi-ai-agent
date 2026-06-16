# Architecture

## Overview

The Personal Assistant Multi-Agent System is a LangGraph-based orchestration platform running on AWS.

The platform consists of:

* A central Orchestrator Agent
* Multiple specialist agents
* Shared platform services
* Event-driven communication
* Human approval workflows
* Long-term memory retrieval

The architecture is intentionally modular so new agents and integrations can be added without redesigning the system.

---

# High-Level System Architecture

```text
┌────────────────────┐
│      Frontend      │
│      Next.js       │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│     API Layer      │
│   ALB / API Route  │
└─────────┬──────────┘
          │
          ▼
┌──────────────────────────────┐
│      LangGraph Runtime       │
│      ECS Fargate Service     │
└──────────────┬───────────────┘
               │
               ▼
      ┌──────────────────┐
      │  Orchestrator    │
      │      Agent       │
      └───────┬──────────┘
              │
 ┌────────────┼────────────┐
 │            │            │
 ▼            ▼            ▼

Calendar    Travel      Dining
 Agent       Agent       Agent

 ▼            ▼            ▼

News      Companion
Agent       Agent

              │
              ▼

     Shared Platform Services
```

---

# Core Principles

## Single Entry Point

All requests enter through the Orchestrator Agent.

No specialist agent is directly exposed to clients.

Operational policy:

* `POST /v1/assistant/requests` is the supported ingress path for accepted requests.
* `POST /v1/agents/{agent}/invoke` is reserved for governance checks and always rejects direct specialist access with `403` and `error_code=direct_specialist_access_denied`.
* Every accepted ingress request emits/updates a routing record where `initial_handler=orchestrator`.
* If intent confidence is below the configured threshold, routing falls back to `companion`.

Benefits:

* Consistent user experience
* Centralized routing
* Centralized policy enforcement
* Easier observability

---

## Agent Specialization

Each agent owns a single business domain.

| Agent        | Responsibility           |
| ------------ | ------------------------ |
| Orchestrator | Routing and coordination |
| Calendar     | Scheduling               |
| Travel       | Flight search            |
| Dining       | Restaurant search        |
| News         | News retrieval           |
| Companion    | General conversation     |

Agents should not contain logic belonging to another domain.

---

## Shared Services

Capabilities used by multiple agents are implemented as services instead of agents whenever possible.

Examples:

* Memory Service
* Approval Service
* Event Service

This prevents unnecessary agent-to-agent reasoning.

---

# Runtime Architecture

## Deployment Model

```text
AWS ECS Fargate

┌────────────────────────┐
│   LangGraph Runtime    │
│                        │
│  Orchestrator Agent    │
│  Calendar Agent        │
│  Travel Agent          │
│  Dining Agent          │
│  News Agent            │
│  Companion Agent       │
│                        │
└────────────────────────┘
```

All agents execute inside the same backend service.

Agents are implemented as Python modules and LangGraph subgraphs.

Benefits:

* Simpler deployment
* Lower latency
* Easier debugging
* Shared state access
* Lower infrastructure cost

---

# LangGraph Architecture

## Main Graph

```text
START
  │
  ▼

Load Context
  │
  ▼

Intent Detection
  │
  ▼

Route Request
  │
  ▼

Specialist Agent
  │
  ▼

Approval Required?
  │
 ┌┴──────────────┐
 │               │
No             Yes
 │               │
 ▼               ▼

Response     Approval Node
 │               │
 └──────┬────────┘
        │
        ▼

Response Builder
        │
        ▼

END
```

---

# Orchestrator Agent

## Responsibilities

* Intent detection
* Agent routing
* Context assembly
* Response aggregation
* Workflow coordination

The orchestrator should not perform domain-specific work.

Instead it delegates work to specialist agents.

---

## Routing Strategy

Example routing table:

```python
{
    "calendar": "calendar_agent",
    "travel": "travel_agent",
    "dining": "dining_agent",
    "news": "news_agent",
    "chat": "companion_agent"
}
```

Example:

```text
Book a flight to Tokyo
      ↓
Travel Agent

Find a restaurant tonight
      ↓
Dining Agent
```

---

# Specialist Agents

## Calendar Agent

### Responsibilities

* Parse dates
* Parse time expressions
* Check availability
* Detect conflicts
* Generate meeting proposals

### Tools

```text
OutlookCalendarTool
```

### Integrations

```text
Microsoft Graph API
```

---

## Travel Agent

### Responsibilities

* Flight search
* Travel recommendations
* Preference application

### Tools

```text
FlightSearchTool
```

### Inputs

* User request
* Travel preferences
* Calendar constraints

---

## Dining Agent

### Responsibilities

* Restaurant search
* Availability search
* Cuisine filtering
* Budget filtering

### Tools

```text
RestaurantSearchTool
```

---

## News Agent

### Responsibilities

* Retrieve news
* Summarize content
* Topic search

### Tools

```text
NewsSearchTool
```

---

## Companion Agent

### Responsibilities

* General conversation
* Knowledge assistance
* Brainstorming

### Tools

LLM only unless future tools are added.

---

# Shared Services

## Memory Service

### Purpose

Store and retrieve long-term user preferences.

### Storage

```text
Amazon DynamoDB
```

### Example Record

```json
{
  "user_id": "123",
  "preferred_airline": "Air Canada",
  "seat_preference": "Aisle",
  "meeting_start_time": "09:00",
  "favorite_cuisine": "Japanese"
}
```

### Access Pattern

```text
Agent
  │
  ▼
Memory Service
  │
  ▼
DynamoDB
```

---

## Approval Service

### Purpose

Provide human-in-the-loop approval.

### Example Workflow

```text
Travel Agent
      │
      ▼

Approval Request

      │
      ▼

User Confirmation

      │
      ▼

Continue Workflow
```

### Approval Candidates

* Calendar event creation
* Flight booking
* Restaurant reservation
* Any future transactional action

---

# Event Architecture

## Event Bus

```text
Amazon EventBridge
```

Used for:

* Audit events
* Agent lifecycle events
* Workflow monitoring
* Future service decoupling

---

## Example Events

```text
agent.request.received

agent.route.completed

calendar.availability.checked

travel.search.completed

restaurant.search.completed

memory.preference.loaded

approval.required

approval.completed
```

---

# State Model

## Conversation State

Managed by LangGraph.

Example:

```python
class AssistantState(TypedDict):
    user_id: str
    session_id: str
    user_input: str
    intent: str
    agent_name: str
    retrieved_preferences: dict
    approval_required: bool
    approval_status: str
    agent_response: str
    final_response: str
```

---

# Tool Architecture

Agents never call external APIs directly.

Instead:

```text
Agent
  │
  ▼
Tool Layer
  │
  ▼
External Provider
```

Example:

```text
Calendar Agent
      │
      ▼
OutlookCalendarTool
      │
      ▼
Microsoft Graph API
```

Benefits:

* Easier testing
* Easier mocking
* Cleaner agent prompts
* Provider replacement without agent changes

---

# Security Architecture

## Authentication

User Account System

Responsibilities:

* Authentication
* Session management
* Identity propagation

---

## Authorization

User context is passed through the workflow.

Example:

```python
user_id
tenant_id
roles
permissions
```

Every tool invocation must validate user authorization.

---

# Observability

## Logging

Log:

* User requests
* Agent routing
* Tool calls
* Errors
* Approval decisions

---

## Metrics

Track:

* Request count
* Agent latency
* Tool latency
* Approval rate
* Error rate
* LLM token usage

---

## Tracing

Trace:

```text
Request
  ├─ Orchestrator
  ├─ Memory
  ├─ Specialist Agent
  ├─ Tool
  └─ Response
```

Recommended:

* OpenTelemetry
* CloudWatch
* AWS X-Ray

---

# Future Expansion

The architecture supports adding:

* Hotel Agent
* Shopping Agent
* Finance Agent
* Email Agent
* Task Management Agent

New agents should:

1. Own a single business domain
2. Expose a LangGraph subgraph
3. Register routing metadata
4. Reuse shared platform services

No architectural redesign should be required.

---

# Design Decisions

| Decision              | Choice            |
| --------------------- | ----------------- |
| Agent Framework       | LangGraph         |
| Runtime               | ECS Fargate       |
| Programming Language  | Python 3.12+      |
| Frontend              | Next.js           |
| LLM Provider          | Amazon Bedrock    |
| Memory Store          | DynamoDB          |
| Calendar Integration  | Microsoft 365     |
| Event Bus             | EventBridge       |
| Approval Model        | Human-in-the-loop |
| Agent Deployment      | Single Service    |
| Communication Pattern | Event-Driven      |
| Testing Framework     | Pytest            |
| Authentication        | User Accounts     |
| Long-Term Memory      | Retrieval-Based   |

```
```
