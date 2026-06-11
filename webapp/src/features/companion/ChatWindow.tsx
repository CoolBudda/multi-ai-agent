"use client";

import { useState } from "react";

interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      role: "assistant",
      content: "Hi! I'm your personal assistant. How can I help you today?",
    },
  ]);
  const [input, setInput] = useState("");

  // TODO: wire up real streaming API via src/lib/api.ts
  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    setMessages((prev) => [
      ...prev,
      { id: Date.now(), role: "user", content: trimmed },
      {
        id: Date.now() + 1,
        role: "assistant",
        content: "(placeholder response)",
      },
    ]);
    setInput("");
  };

  return (
    <div className="flex flex-1 flex-col">
      {/* Header */}
      <header className="flex items-center border-b border-gray-200 bg-white px-6 py-4 dark:border-gray-800 dark:bg-gray-900">
        <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
          Personal Assistant
        </h1>
      </header>

      {/* Message list */}
      <div className="flex flex-1 flex-col gap-3 overflow-y-auto px-6 py-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-prose rounded-2xl px-4 py-2 text-sm ${
                msg.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-50"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
      </div>

      {/* Input bar */}
      <div className="border-t border-gray-200 bg-white px-6 py-4 dark:border-gray-800 dark:bg-gray-900">
        <form
          className="flex gap-3"
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Message your assistant…"
            className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-50"
          />
          <button
            type="submit"
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            disabled={!input.trim()}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
