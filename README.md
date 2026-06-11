# Personal Assistant Multi-Agent System

A production-oriented multi-agent personal assistant platform built with LangGraph, Python, AWS, and Next.js.

The system uses an orchestrator-driven architecture that routes user requests to specialized agents responsible for scheduling meetings, travel planning, restaurant discovery, news retrieval, and general conversation.

---

# Features

## Calendar Management

* Schedule meetings
* Check availability
* Detect conflicts
* Handle time zones
* Integrate with Microsoft 365 Calendar

## Travel Planning

* Search flights
* Compare travel options
* Apply user preferences
* Coordinate with calendar availability

## Dining Discovery

* Search restaurants
* Filter by cuisine
* Filter by budget
* Filter by location
* Search reservation availability

## News Aggregation

* Fetch latest news
* Search by topic
* Summarize articles
* Prioritize trusted sources

## Companion Chat

* Open-ended conversation
* Q&A
* Brainstorming
* Explanations

## Long-Term Memory

* User preferences
* Travel preferences
* Meeting preferences
* Restaurant preferences
* News interests

## Human Approval Workflow

Actions requiring confirmation must be approved before execution.

---

# Architecture

```text
┌─────────────┐
│   Next.js   │
│  Frontend   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│     ALB     │
└──────┬──────┘
       │
       ▼
┌──────────────────────────┐
│      ECS Fargate         │
│   LangGraph Runtime      │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Orchestrator Agent      │
└───────┬───────┬──────────┘
        │       │
        ▼       ▼

 Calendar      Travel
  Agent         Agent

 Dining        News
  Agent         Agent

      Companion Agent

           │
           ▼

 ┌───────────────────────┐
 │ Shared Services       │
 ├───────────────────────┤
 │ Memory Service        │
 │ Approval Service      │
 │ EventBridge           │
 │ Bedrock LLM           │
 │ Microsoft 365 API     │
 └───────────────────────┘
```

---

# Agent Architecture

## Orchestrator Agent

The entry point for all user requests.

Responsibilities:

* Intent detection
* Agent routing
* Multi-agent coordination
* Response aggregation
* Conversation management

Examples:

```text
Book me a flight to New York
→ Travel Agent

Find a restaurant tonight
→ Dining Agent

What's happening in AI today?
→ News Agent

Schedule a meeting with Alex
→ Calendar Agent
```

---

## Calendar Agent

Responsibilities:

* Parse natural language dates
* Check availability
* Find available slots
* Create meeting proposals
* Detect conflicts
* Handle time zones

Example:

```text
Schedule a meeting with Alex next Tuesday afternoon
```

---

## Travel Agent

Responsibilities:

* Search flights
* Compare options
* Apply travel preferences
* Coordinate with calendar

Example:

```text
Find flights to Tokyo next month
```

---

## Dining Agent

Responsibilities:

* Search restaurants
* Apply cuisine preferences
* Apply budget constraints
* Search reservation availability

Example:

```text
Find a Japanese restaurant downtown tonight
```

---

## News Agent

Responsibilities:

* Retrieve latest headlines
* Search by topic
* Summarize content
* Rank relevant results

Example:

```text
What happened in AI today?
```

---

## Companion Agent

Responsibilities:

* General conversation
* Explanations
* Brainstorming
* Open-ended interactions

Example:

```text
Help me think through a startup idea
```

---

# Shared Services

## Memory Service

Stores long-term user preferences.

Examples:

```json
{
  "user_id": "123",
  "preferred_airline": "Air Canada",
  "seat_preference": "Aisle",
  "meeting_start_time": "09:00",
  "favorite_cuisine": "Japanese"
}
```

Responsibilities:

* Store preferences
* Retrieve preferences
* Provide context to agents

---

## Approval Service

Provides human-in-the-loop confirmation.

Example workflow:

```text
Travel Agent
      │
      ▼
Approval Service
      │
      ▼
User Approval
      │
      ▼
Continue Workflow
```

---

# Event-Driven Communication

Agents communicate through events rather than direct coupling.

Examples:

```text
calendar.availability.checked

travel.search.requested

restaurant.search.completed

approval.required

memory.preference.retrieved
```

Benefits:

* Loose coupling
* Better observability
* Easier scaling
* Future microservice support

---

# Technology Stack

## Frontend

* Next.js
* TypeScript

## Backend

* Python 3.12+
* LangGraph
* Pytest

## Cloud

* AWS ECS Fargate
* Amazon EventBridge
* Amazon DynamoDB
* Amazon Bedrock

## External Integrations

* Microsoft Graph API
* Flight Search Providers
* Restaurant Search Providers
* News Providers

---

# Project Structure

```text
project-root/

├── frontend/
│   ├── src/
│   └── package.json
│
├── backend/
│   ├── agents/
│   │
│   ├── orchestrator/
│   │
│   ├── memory/
│   │
│   ├── approval/
│   │
│   ├── tools/
│   │
│   ├── integrations/
│   │
│   ├── graph/
│   │
│   ├── events/
│   │
│   └── tests/
│
├── infrastructure/
│
├── docs/
│
└── README.md
```

---

# LangGraph Design

Each specialist agent is implemented as a LangGraph subgraph.

```text
Main Graph
    │
    ├── Calendar Subgraph
    ├── Travel Subgraph
    ├── Dining Subgraph
    ├── News Subgraph
    └── Companion Subgraph
```

Each subgraph owns:

* State
* Prompt
* Tools
* Routing logic
* Policies

---

# Example Workflow

User request:

```text
Book me a flight and hotel for a 3-day trip to Tokyo next month
```

Execution flow:

```text
1. User Request

2. Orchestrator
      ↓

3. Travel Agent

4. Travel Agent
      ├── Memory Service
      ├── Calendar Agent
      └── External Search APIs

5. Approval Service

6. Response Aggregation

7. User Response
```

---

# Security Principles

* User authentication required
* Principle of least privilege
* Human approval before actions
* Secure secret management
* Audit logging for agent decisions

---

# Testing Strategy

## Unit Tests

* Agent logic
* Tool wrappers
* State transitions

## Integration Tests

* LangGraph workflows
* Memory retrieval
* Event publishing

## End-to-End Tests

* User request to final response
* Multi-agent workflows
* Approval flows

---

# Roadmap

## Phase 1

* Orchestrator Agent
* Calendar Agent
* Travel Agent
* Dining Agent
* News Agent
* Companion Agent
* Memory Service

## Phase 2

* Approval workflows
* User preference learning
* Advanced routing
* Enhanced observability

## Phase 3

* Additional agents
* Multi-user collaboration
* Advanced planning workflows
* Voice interfaces

---

# Status

🚧 Design & Development

The system is currently under active development.

