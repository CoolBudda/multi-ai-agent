# GitHub Copilot Instructions

## Project Overview

This is a **Personal Assistant Multi-Agent System** — a production-oriented platform where an orchestrator-driven architecture routes user requests to specialized agents. The system handles calendar scheduling, travel planning, dining discovery, news aggregation, and companion chat.

---

## Tech Stack

- **Backend**: Python 3.12+, LangGraph, AWS (ECS Fargate, EventBridge, Bedrock), Microsoft 365 API
- **Frontend**: TypeScript, Next.js
- **Infrastructure**: AWS ALB, ECS Fargate
- **Testing**: Pytest

---

## Architecture Principles

### Single Entry Point
All requests enter through the **Orchestrator Agent**. Specialist agents are never called directly by the frontend or API layer.

If intent detection does not match any specialist agent domain with sufficient confidence, the Orchestrator must route the request to the Companion Agent as the default fallback handler. The Companion Agent must not attempt to perform actions outside its domain in this case.

### Agent Specialization
Each agent owns exactly one business domain. Do not add logic to an agent that belongs to another domain.

| Agent        | Responsibility           |
| ------------ | ------------------------ |
| Orchestrator | Intent detection, routing, response aggregation |
| Calendar     | Scheduling, availability, conflicts, time zones |
| Travel       | Flight search, preference application, booking |
| Dining       | Restaurant search, reservations, dietary filters |
| News         | Headlines, topic search, article summarization |
| Companion    | General conversation, Q&A, brainstorming |

### Shared Services Over Agent-to-Agent Coupling
Capabilities needed by multiple agents (memory, approvals, events) are implemented as **services**, not agents, to prevent unnecessary LLM reasoning hops.

### Event-Driven Communication
Agents communicate through events, not direct calls. Event names follow the pattern `<domain>.<action>.<status>` (e.g., `calendar.availability.checked`, `travel.search.requested`).

### Human-in-the-Loop
Any action with real-world side effects (booking, reservation, sending invites) must pass through the **Approval Service** before execution.

If the user rejects an approval request, the Approval Service emits a `<domain>.<action>.rejected` event. The Orchestrator must return a user-facing confirmation that the action was cancelled and no changes were made. The agent graph must not retry the action without a new explicit user request.

---

## LangGraph Conventions

- All agents are implemented as **LangGraph subgraphs** and Python modules.
- The main graph flow: `Load Context → Intent Detection → Route Request → Specialist Agent → Approval? → Response Builder`.
- Use `StateGraph` for agent graphs. Keep state typed with TypedDict or Pydantic models.
- Every agent node should be a pure function when possible — side effects belong in tool nodes, with one explicit exception: memory context retrieval at agent start is the only permitted side effect in an agent node, and it must call the Memory Service through the service layer. All other external I/O must occur in tool nodes via the service layer.

---

## Agent Collaboration Patterns

- **Travel Agent** coordinates calendar availability by querying the Orchestrator, which routes to the Calendar Agent — agents must not call each other directly; all cross-agent coordination goes through the Orchestrator.
- **Calendar Agent** retrieves user scheduling preferences from the Memory Service at agent start.
- **Dining Agent** retrieves dietary restrictions from the Memory Service at agent start.
- **News Agent** retrieves preferred topics from the Memory Service at agent start.
- **Companion Agent** must route requests to the Safety/Policy layer when the user message contains any of the following: mental health distress signals, requests for medical or legal advice, political opinion generation, or content that may violate content moderation policies. All other requests are handled directly.
- The Orchestrator passes single-agent responses to the Response Builder unchanged. When multiple specialist agents are invoked for a single request, the Orchestrator merges their outputs into a single structured response before invoking the Response Builder.
- When the Orchestrator detects that a request spans multiple domains, it invokes all relevant specialist agents in parallel and aggregates their responses. When domain assignment is ambiguous for a single-domain request, the Orchestrator must select the highest-confidence domain match and route to that agent only. The confidence threshold for routing is defined in the Orchestrator's intent detection configuration.

---

## Memory Service

User preferences are stored as structured JSON and retrieved by agents on demand.

```json
{
  "user_id": "string",
  "preferred_airline": "string",
  "seat_preference": "Aisle | Window | Middle",
  "meeting_start_time": "HH:MM",
  "favorite_cuisine": "string",
  "news_topics": ["string"]
}
```

Retrieve memory context at the start of a specialist agent's execution by calling the Memory Service through the service layer (not inside tool calls, and not as a direct I/O call from the agent node — see LangGraph Conventions for the precedence rule).

If a memory field required for agent execution is absent or null, the agent must proceed using a sensible default (defined per-agent) and must not block execution or raise an error. Agents should prompt the user to set missing preferences only when the missing field materially affects the response quality.

---

## Code Conventions

- Use Python type hints everywhere.
- Agent state schemas use `TypedDict` or Pydantic `BaseModel`.
- Tool functions are decorated with `@tool` (LangChain/LangGraph convention).
- Keep agent graph definitions separate from business logic (tools, services).
- Name files after their domain: `calendar_agent.py`, `travel_agent.py`, etc.
- Tests live in a `tests/` directory mirroring the source structure. Use Pytest fixtures for LangGraph state setup.

---

## Security

- Never log or expose raw API credentials or user PII.
- All external API calls (Microsoft 365, flight APIs, restaurant APIs) must go through a dedicated service layer, not called directly from agent nodes.
- If a service layer call fails, the agent must emit a `<domain>.<action>.failed` event with the error code and must return a user-facing message explaining that the action could not be completed and suggesting the user retry. Agents must not silently swallow service errors or return partial results without indicating degradation.
- Human approval is mandatory before any write operation (calendar events, bookings, reservations).

---

## Infrastructure (Terraform)

You are working in a spec-driven Terraform repository.

Rules:
- Always follow `plans/` before writing code.
- Never invent AWS resources not present in a spec under `specs/`.
- Terraform must be modular under `agenterrafrom/modules/`.
- Changes must be minimal and deterministic.
- All fixes must be patch-based, not rewrites.

### Conventions
- One module per AWS service domain (e.g., `modules/vpc`, `modules/dynamodb`, `modules/ecs`).
- Each module exposes typed `variables.tf` and `outputs.tf`.
- Environment compositions live under `agenterrafrom/environments/<env>/`.
- Sensitive values must never be committed in plaintext; reference Secrets Manager ARNs or use a secrets backend.
- `terraform validate` and `terraform plan` must pass before any merge.

---

## Frontend

### Stack
- **Framework**: Next.js (App Router)
- **Language**: TypeScript — strict mode enabled (`"strict": true` in `tsconfig.json`)
- **Styling**: Tailwind CSS — use utility classes; avoid inline styles
- **State Management**: Zustand — one store slice per domain (e.g., `useCalendarStore`, `useTravelStore`)
- **Data Fetching**: TanStack Query (React Query) — use for all server-state; avoid `useState` + `useEffect` for async data
- **Streaming**: LangGraph streaming responses handled via Server-Sent Events (SSE) or WebSocket where supported

### Project Structure
```
src/
  app/           # Next.js App Router pages and layouts
  components/    # Shared UI components (no business logic)
  features/      # Domain-scoped components, hooks, and stores
    calendar/
    travel/
    dining/
    news/
    companion/
  lib/           # API clients, utilities, constants
  stores/        # Global or cross-domain Zustand store slices only (e.g., auth, session)
  types/         # Shared TypeScript types and interfaces
```

### Conventions
- Co-locate domain components, hooks, and store slices inside `features/<domain>/`. The top-level `src/stores/` directory is reserved for global or cross-domain store slices only (e.g., auth, session); domain-specific store slices must live in `src/features/<domain>/`.
- All API calls to the backend go through `src/lib/api.ts` — never call `fetch` directly in components.
- Use React Server Components by default. Components that use TanStack Query hooks (`useQuery`, `useMutation`), Zustand stores, or browser event handlers must be marked `'use client'`. All other components, including those that fetch data via async Server Component patterns, should remain Server Components.
- Use TanStack Query `useQuery` / `useMutation` for all data fetching in Client Components.
- Export one component per file; file name matches the component name (`PascalCase`).
- No `any` types. Prefer `unknown` with type guards at system boundaries.

### Linting & Formatting
- **ESLint** with `eslint-config-next` — enforced in CI.
- **Prettier** — single source of formatting truth; no manual formatting.
- Run `eslint` and `prettier --check` as part of the pre-commit hook and CI pipeline.

### Testing
- **Vitest + React Testing Library** — unit and component tests; mirror source structure under `__tests__/`.
- **Playwright** — end-to-end tests under `e2e/`; cover critical user flows (schedule meeting, search flights, etc.).
- Avoid testing implementation details; test user-visible behavior.
