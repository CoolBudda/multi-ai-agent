# Chat Interface Implementation Plan

## 1. Goal
Direct restatement of the spec purpose: provide users with a conversational input surface that sends messages to the backend and renders streaming assistant responses incrementally.

## 2. Scope Mapping
- Included: Chat input field, message submission, SSE/WebSocket streaming display, input state management, and session-scoped conversation history.
- Excluded: Domain response card rendering (covered by domain-response-cards plan).

## 3. File Changes
- webapp/src/features/companion/ChatWindow.tsx
- webapp/src/features/companion/useConversationStore.ts
- webapp/src/lib/api.ts
- webapp/src/types/index.ts

## 4. LangGraph Nodes (if applicable)
- N/A

## 5. Tools
- N/A

## 6. State Updates
- messages
- isStreaming

## 7. Implementation Steps (strict order)
1. Define ChatMessage type { id, role: 'user' | 'assistant', content, timestamp } in src/types/index.ts.
2. Define ConversationStore { messages: ChatMessage[], isStreaming: boolean } as a Zustand slice in src/features/companion/useConversationStore.ts.
3. Implement streaming chat API call in src/lib/api.ts via SSE or WebSocket; no direct fetch in components.
4. Implement ChatWindow component marked 'use client'; wire input submission to api call; disable input while isStreaming is true.
5. Implement incremental chunk append to the current assistant message as stream chunks arrive.
6. Re-enable input and set isStreaming false on stream end or error.
7. Display inline error message on stream failure without leaving input disabled.
8. Scope conversation history to the current browser session only (no persistence across reloads).

## 8. Dependencies
- Zustand
- TanStack Query (useMutation for non-streaming path or manual fetch for SSE)
- src/lib/api.ts

## 9. Test Plan
- Unit tests: Message append logic, isStreaming state transitions, error state recovery.
- Integration tests: Submitted message reaches backend and streaming response chunks render incrementally.
- Workflow tests: Full send-stream-complete flow; stream failure shows inline error and restores input.

## 10. Acceptance Criteria Mapping
- FR-001 Users can type and submit messages to the assistant. -> Validate input submission sends request to backend via api.ts.
- FR-002 Responses stream into the UI as they arrive. -> Validate each chunk is appended incrementally before stream ends.
- FR-003 The input is disabled while a response is in progress. -> Validate isStreaming true blocks input.
- FR-004 All messages are stored in the session conversation history. -> Validate ConversationStore accumulates messages within session.
- FR-005 An API failure shows an inline error and restores the input. -> Validate error state renders message and re-enables input.

## 11. Open Questions
- None identified from the current requirements.
