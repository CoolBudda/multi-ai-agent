# Chat Interface

## Purpose
Provide users with a conversational input surface that sends messages to the backend and renders streaming assistant responses incrementally.

## Scope
Chat input field, message submission, SSE/WebSocket streaming display, input state management, and session-scoped conversation history.

## Requirements
- Users can type and submit messages to the assistant.
- Responses stream into the UI as they arrive rather than rendering all at once.
- The input is disabled while a response is in progress.
- All messages (user and assistant) are stored in the session conversation history.
- Conversation history is visible by scrolling and is scoped to the current browser session.

## Inputs
- User-typed message.
- Streaming response chunks from the backend.
- Session store state.

## Outputs
- HTTP request to the backend via `src/lib/api.ts`.
- Incrementally rendered assistant response text.
- Updated conversation history in the Zustand session store.

## Business Rules
- All API calls go through `src/lib/api.ts` — no direct `fetch` calls from components.
- Input must be re-enabled immediately after stream completion or error.
- Conversation history does not persist across page reloads.
- Components using Zustand or TanStack Query hooks must be marked `'use client'`.

## Workflow
1. User types a message and submits.
2. Frontend disables input and sends the request.
3. Response streams via SSE or WebSocket.
4. Each chunk is appended to the assistant message in the UI.
5. On stream end, input is re-enabled and history is updated.

## Data Model
- `ChatMessage`: `{ id, role: 'user' | 'assistant', content, timestamp }`
- `ConversationStore`: `{ messages: ChatMessage[], isStreaming: boolean }`

## Error Handling
- If the stream fails or the connection drops, show an inline error message.
- Re-enable the input so the user can retry.
- Do not leave the UI in a disabled state after an error.

## Acceptance Criteria
- A submitted message is sent to the backend and a streaming response is rendered.
- The input is disabled during streaming and re-enabled after completion.
- Conversation history accumulates across messages within the session.
- An API failure shows an inline error and restores the input.

## Open Questions
- None identified from the current requirements.
