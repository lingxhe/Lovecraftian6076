"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Bot, Download, RotateCcw, Settings, User } from "lucide-react";
import { useStore } from "@/store/useStore";
import { downloadLog, getKPResponse } from "@/lib/api";

const OPENING_SCENE = (name: string) => `The taxi hums steadily along the winding mountain road...

*What would you like to do, ${name}?*`;

export default function ChatPage() {
  const router = useRouter();
  const {
    character,
    messages,
    currentScene,
    apiKey,
    setMessages,
    addMessage,
    setCurrentScene,
    setApiKey,
    resetConversation,
    setCharacter,
  } = useStore();

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!character) {
      router.replace("/create-character");
    }
  }, [character, router]);

  useEffect(() => {
    if (character && messages.length === 0) {
      addMessage({
        role: "assistant",
        content: OPENING_SCENE(character.name || "Investigator"),
      });
    }
  }, [character, messages.length, addMessage]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  if (!character) {
    return null;
  }

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMessage = { role: "user" as const, content: input.trim() };
    addMessage(userMessage);
    setInput("");
    setLoading(true);

    try {
      const response = await getKPResponse(
        userMessage.content,
        character,
        [...messages, userMessage],
        apiKey,
        currentScene
      );

      addMessage({ role: "assistant", content: response.response });
      if (response.current_scene && response.current_scene !== currentScene) {
        setCurrentScene(response.current_scene);
      }
      if (response.character) {
        setCharacter(response.character);
      }
    } catch (error) {
      addMessage({
        role: "assistant",
        content: `⚠️ Error: ${error instanceof Error ? error.message : "Unknown error"}`,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadLog = async () => {
    if (!character) return;
    try {
      const blob = await downloadLog(character.name);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `chat_log_${character.name}_${new Date().toISOString().split("T")[0]}.md`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert("Failed to download log. Please try again later.");
    }
  };

  const handleRestart = () => {
    if (confirm("Are you sure you want to restart the conversation? This will clear all records.")) {
      resetConversation();
      setMessages([]);
      addMessage({
        role: "assistant",
        content: OPENING_SCENE(character.name || "Investigator"),
      });
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-950 text-white">
      {showSidebar && (
        <aside className="w-80 border-r border-slate-800 bg-slate-900/70 p-4 space-y-6">
          <div>
            <h2 className="text-lg font-semibold mb-3">⚙️ Configuration</h2>
            <label className="text-sm text-slate-400">OpenAI API Key</label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="sk-..."
              className="mt-2 w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-sm"
            />
            <p className="text-xs text-slate-500 mt-1">Stored locally in browser, not uploaded to server</p>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-2">Character</h3>
            <div className="text-3xl">{character.avatar}</div>
            <p className="mt-2 text-slate-200">{character.name}</p>
            <p className="text-sm text-slate-400">
              STR {character.str} · INT {character.int} · POW {character.pow}
            </p>
            <p className="text-sm text-slate-400">
              SAN {character.san} · LUCK {character.luck}
            </p>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-2">Current Scene</h3>
            <p className="text-slate-300">{currentScene}</p>
          </div>

          <div className="space-y-2">
            <button
              onClick={handleDownloadLog}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-blue-600 hover:bg-blue-700 py-2"
            >
              <Download className="w-4 h-4" />
              Download Log
            </button>
            <button
              onClick={handleRestart}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-orange-600 hover:bg-orange-700 py-2"
            >
              <RotateCcw className="w-4 h-4" />
              Restart Conversation
            </button>
          </div>
        </aside>
      )}

      <main className="flex-1 flex flex-col">
        <header className="flex items-center justify-between border-b border-slate-800 bg-slate-900/80 px-6 py-4">
          <div>
            <h1 className="text-2xl font-semibold">Keeper Chat</h1>
            <p className="text-sm text-slate-400">
              Keeper powered by LangGraph + OpenAI API, with scene transitions and dice tools
            </p>
          </div>
          <button
            onClick={() => setShowSidebar((prev) => !prev)}
            className="rounded-lg border border-slate-700 px-3 py-2 hover:bg-slate-800"
          >
            <Settings className="w-4 h-4" />
          </button>
        </header>

        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.role === "assistant" && (
                <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center">
                  <Bot className="w-5 h-5" />
                </div>
              )}
              <div
                className={`max-w-3xl rounded-2xl px-5 py-3 ${
                  msg.role === "user" ? "bg-blue-600 text-white" : "bg-slate-800 text-slate-100"
                }`}
              >
                <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>
              </div>
              {msg.role === "user" && (
                <div className="w-10 h-10 rounded-full bg-blue-700 flex items-center justify-center text-2xl">
                  {character.avatar || <User className="w-5 h-5" />}
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex gap-3 justify-start">
              <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center animate-pulse" />
              <div className="bg-slate-800 rounded-2xl px-5 py-3 text-slate-300">KP is thinking...</div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <footer className="border-t border-slate-800 bg-slate-900/80 px-6 py-4">
          <div className="flex gap-3 max-w-4xl mx-auto">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Describe your action, ask a question, or make a skill check..."
              className="flex-1 rounded-xl bg-slate-800 border border-slate-700 px-4 py-3 focus:border-blue-500 outline-none"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-700 font-semibold"
            >
              Send
            </button>
          </div>
        </footer>
      </main>
    </div>
  );
}

