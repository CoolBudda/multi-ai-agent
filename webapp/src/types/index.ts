/** Shared TypeScript types and interfaces */

export interface User {
  id: string;
  email: string;
}

export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
}
