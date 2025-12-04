"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Download, RotateCcw, Settings, Eye, EyeOff } from "lucide-react";
import { useStore } from "@/store/useStore";
import { downloadLog, getKPResponse } from "@/lib/api";
import { Dice3DOverlay } from "./Dice3DOverlay";

const TypewriterText = ({
  text,
  active,
  onComplete,
  className = "",
  speed = 25,
}: {
  text: string;
  active: boolean;
  onComplete?: () => void;
  className?: string;
  speed?: number;
}) => {
  const [displayed, setDisplayed] = useState(active ? "" : text);
  const [isComplete, setIsComplete] = useState(!active);

  useEffect(() => {
    if (!active) {
      setDisplayed(text);
      setIsComplete(true);
      return;
    }

    setDisplayed("");
    setIsComplete(false);
    let index = 0;
    const interval = setInterval(() => {
      index += 1;
      setDisplayed(text.slice(0, index));
      if (index >= text.length) {
        clearInterval(interval);
         setIsComplete(true);
        onComplete?.();
      }
    }, speed);

    return () => clearInterval(interval);
  }, [text, active, speed, onComplete]);

  return (
    <div className={`typewriter-text ${className}`}>
      <span className="whitespace-pre-wrap">{displayed}</span>
      {active && !isComplete && (
        <span className="typewriter-caret ml-1" />
      )}
    </div>
  );
};

const MarkdownText = ({ text, className = "" }: { text: string; className?: string }) => {
  const toHtml = (md: string) => {
    let html = md
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    // bold **text**
    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    // italic *text*
    html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");
    // line breaks
    html = html.replace(/\n/g, "<br />");

    return html;
  };

  return (
    <div
      className={className}
      dangerouslySetInnerHTML={{ __html: toHtml(text) }}
    />
  );
};

const OPENING_SCENE = (name: string) => `The taxi hums steadily along the winding mountain road, its wipers smearing rain across the windshield. You sit in the back seat beside your suitcase—the sum of your old life—on your way to a new beginning in Arkham. The driver, a thin man in a worn cap, hasn’t spoken much. Only the low hiss of the tires and the rhythmic drone of the engine fill the silence.

As the car climbs higher, fog begins to roll in—thick, gray, and slow-moving. The landscape outside grows sparse: no other cars, no houses, only black trees leaning under the weight of the mist. Then, with a sputter and a cough, the engine falters.

“Damn it,” the driver mutters, steering the vehicle to the roadside. He tries the ignition twice, then sighs. “No luck. We’re near a village called Emberhead—just over that hill.” He gestures towards faint lights in the mist. “You’ll have to see if you can find a place to stay the night there. I’ll go and look for a mechanic.”

You step out into the damp air, clutching your coat tighter. The road behind you disappears into the mist. Ahead, through the drizzle, the village of Emberhead waits—silent except for the distant crackle of unseen fires.

Your journey to a new life has taken an unexpected detour.

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
  const [apiKeyVisible, setApiKeyVisible] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const typedMessagesRef = useRef<Set<number>>(new Set());
  const hydrateExistingMessagesRef = useRef(messages.length > 0);
  const [showDiceOverlay, setShowDiceOverlay] = useState(false);
  const [diceValues, setDiceValues] = useState<{ total: number; tens: number; ones: number } | null>(null);
  const [diceNotation, setDiceNotation] = useState<string>("1d100");
  const [testRoll, setTestRoll] = useState<number | null>(null);
  const [pendingDiceRequest, setPendingDiceRequest] = useState<{
    type: "dice" | "san";
    skillName?: string;
    difficulty?: string;
    skillValue?: number;
    currentSan?: number;
    sanLoss?: number;
  } | null>(null);

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

  useEffect(() => {
    if (messages.length === 0) {
      typedMessagesRef.current.clear();
      hydrateExistingMessagesRef.current = false;
      return;
    }

    if (hydrateExistingMessagesRef.current) {
      const typed = new Set<number>();
      messages.forEach((_, idx) => typed.add(idx));
      typedMessagesRef.current = typed;
      hydrateExistingMessagesRef.current = false;
    }
  }, [messages]);

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

      const assistantText = response.response;

      // Detect dice request markers: [DICE_REQUEST:skill_name:difficulty:skill_value]
      const diceRequestMatch = assistantText.match(/\[DICE_REQUEST:(.+?):(.+?):(\d+)\]/);
      if (diceRequestMatch) {
        const skillName = diceRequestMatch[1];
        const difficulty = diceRequestMatch[2];
        const skillValue = parseInt(diceRequestMatch[3], 10);
        setPendingDiceRequest({
          type: "dice",
          skillName,
          difficulty,
          skillValue,
        });
        // Remove the marker from the displayed message
        const cleanedText = assistantText.replace(/\[DICE_REQUEST:.+?\]\s*\n*/g, "").trim();
        // Only add message if there's actual content (not just the marker)
        if (cleanedText) {
          addMessage({ role: "assistant", content: cleanedText });
        }
        // If only marker, don't add message - just show the dice button
      } else {
        // Detect SAN check request markers: [SAN_CHECK_REQUEST:current_san:san_loss]
        const sanRequestMatch = assistantText.match(/\[SAN_CHECK_REQUEST:(\d+):(\d+)\]/);
        if (sanRequestMatch) {
          const currentSan = parseInt(sanRequestMatch[1], 10);
          const sanLoss = parseInt(sanRequestMatch[2], 10);
          setPendingDiceRequest({
            type: "san",
            currentSan,
            sanLoss,
          });
          // Remove the marker from the displayed message
          const cleanedText = assistantText.replace(/\[SAN_CHECK_REQUEST:.+?\]\s*\n*/g, "").trim();
          // Only add message if there's actual content (not just the marker)
          if (cleanedText) {
            addMessage({ role: "assistant", content: cleanedText });
          }
          // If only marker, don't add message - just show the dice button
        } else {
          // No dice request, just add the message normally
          addMessage({ role: "assistant", content: assistantText });
        }
      }
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

  const handleDiceRollClick = () => {
    if (!pendingDiceRequest) return;
    setDiceNotation("1d100");
    setShowDiceOverlay(true);
  };

  const handleDiceResult = async (value: number) => {
    if (!pendingDiceRequest) return;
    
    setShowDiceOverlay(false);
    
    // Format the result message based on request type
    let resultMessage = "";
    if (pendingDiceRequest.type === "dice") {
      // Format: DiceResult: 73:skill_name:difficulty:skill_value
      resultMessage = `DiceResult: ${value}:${pendingDiceRequest.skillName}:${pendingDiceRequest.difficulty}:${pendingDiceRequest.skillValue}`;
    } else {
      // Format: SANResult: 73:current_san:san_loss
      resultMessage = `SANResult: ${value}:${pendingDiceRequest.currentSan}:${pendingDiceRequest.sanLoss}`;
    }
    
    // Clear pending request
    setPendingDiceRequest(null);
    
    // Add the result message to chat history first (for display)
    const resultUserMessage = { role: "user" as const, content: resultMessage };
    addMessage(resultUserMessage);
    
    // Send the result as a user message
    setLoading(true);
    try {
      const response = await getKPResponse(
        resultMessage,
        character,
        [...messages, resultUserMessage],
        apiKey,
        currentScene
      );

      const assistantText = response.response;
      
      // Check for new dice requests in the response
      const diceRequestMatch = assistantText.match(/\[DICE_REQUEST:(.+?):(.+?):(\d+)\]/);
      if (diceRequestMatch) {
        const skillName = diceRequestMatch[1];
        const difficulty = diceRequestMatch[2];
        const skillValue = parseInt(diceRequestMatch[3], 10);
        setPendingDiceRequest({
          type: "dice",
          skillName,
          difficulty,
          skillValue,
        });
        const cleanedText = assistantText.replace(/\[DICE_REQUEST:.+?\]\s*\n*/g, "").trim();
        addMessage({ role: "assistant", content: cleanedText || assistantText });
      } else {
        const sanRequestMatch = assistantText.match(/\[SAN_CHECK_REQUEST:(\d+):(\d+)\]/);
        if (sanRequestMatch) {
          const currentSan = parseInt(sanRequestMatch[1], 10);
          const sanLoss = parseInt(sanRequestMatch[2], 10);
          setPendingDiceRequest({
            type: "san",
            currentSan,
            sanLoss,
          });
          const cleanedText = assistantText.replace(/\[SAN_CHECK_REQUEST:.+?\]\s*\n*/g, "").trim();
          addMessage({ role: "assistant", content: cleanedText || assistantText });
        } else {
          addMessage({ role: "assistant", content: assistantText });
        }
      }
      
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

  return (
    <div className="parchment-page flex min-h-screen text-slate-900 relative">
       {showSidebar && (
         <aside className="w-80 border-r border-amber-900/30 bg-black/15 backdrop-blur-sm p-6 space-y-6 overflow-y-auto sticky top-0 h-screen self-start">
           <div className="bg-black/25 border border-amber-900/40 rounded-xl p-4 space-y-4 shadow-[0_10px_30px_rgba(0,0,0,0.45)]">
            <h3 className="text-lg font-semibold text-slate-200">Character</h3>
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full overflow-hidden border-2 border-amber-700/50 shadow-lg shadow-amber-900/20 flex items-center justify-center bg-slate-900">
                {character.avatar?.startsWith("data:image") ? (
                  <img
                    src={character.avatar}
                    alt="Avatar"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="text-3xl">{character.avatar}</div>
                )}
              </div>
              <div className="flex-1">
                <p className="font-semibold text-slate-100">{character.name}</p>
                <div className="mt-2 space-y-1 text-xs text-slate-400">
                  <div className="flex gap-3">
                    <span>STR {character.str}</span>
                    <span>INT {character.int}</span>
                    <span>POW {character.pow}</span>
                  </div>
                  <div className="flex gap-3">
                    <span>SAN {character.san}</span>
                    <span>LUCK {character.luck}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
            <h3 className="text-lg font-semibold text-slate-200 mb-2">Current Scene</h3>
            <p className="text-sm text-amber-300 font-mono bg-slate-900/50 px-3 py-2 rounded-lg border border-amber-900/50">
              {currentScene}
            </p>
          </div>

          <div className="space-y-2">
            <button
              onClick={handleDownloadLog}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-blue-600/80 hover:bg-blue-600 border border-blue-500/50 py-3 transition-all shadow-lg shadow-blue-900/20 hover:shadow-blue-900/30 font-medium"
            >
              <Download className="w-4 h-4" />
              Download Log
            </button>
            <button
              onClick={handleRestart}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-orange-600/80 hover:bg-orange-600 border border-orange-500/50 py-3 transition-all shadow-lg shadow-orange-900/20 hover:shadow-orange-900/30 font-medium"
            >
              <RotateCcw className="w-4 h-4" />
              Restart Conversation
            </button>
            <button
              onClick={() => {
                setTestRoll(null);
                setDiceNotation("1d100");
                setShowDiceOverlay(true);
              }}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-amber-600/80 hover:bg-amber-600 border border-amber-500/60 py-2 transition-all shadow-lg shadow-amber-900/20 hover:shadow-amber-900/30 font-medium text-slate-950"
            >
              Test Roll d10
            </button>
            {testRoll !== null && (
              <p className="text-xs text-amber-200/90 text-center">
                Last d10 roll: <span className="font-semibold">{testRoll}</span>
              </p>
            )}
          </div>
        </aside>
      )}

      <main className="flex-1 flex flex-col">
        <header className="flex flex-wrap gap-4 items-center justify-between border-b border-amber-900/30 bg-black/10 backdrop-blur-sm px-6 py-4">
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-amber-200 to-amber-400 bg-clip-text text-transparent">
              Keeper Chat
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Powered by LangGraph + OpenAI API
            </p>
          </div>
          <div className="flex-1 flex flex-wrap items-center justify-end gap-3">
            <div className="hidden sm:flex items-center gap-2 bg-slate-900/70 border border-slate-700/60 rounded-xl px-3 py-2 backdrop-blur-sm shadow-inner shadow-black/20 min-w-[220px]">
              <input
                type={apiKeyVisible ? "text" : "password"}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="OpenAI API Key"
                className="bg-transparent flex-1 outline-none text-sm text-slate-200 placeholder:text-slate-500"
              />
              <button
                type="button"
                onClick={() => setApiKeyVisible((prev) => !prev)}
                className="text-slate-400 hover:text-amber-300 transition-colors"
                title={apiKeyVisible ? "Hide API Key" : "Show API Key"}
              >
                {apiKeyVisible ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <button
              onClick={() => setShowSidebar((prev) => !prev)}
              className="rounded-xl border border-slate-700/50 px-4 py-2 hover:bg-slate-800/50 transition-all backdrop-blur-sm"
            >
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto px-4 md:px-8 py-8 space-y-6">
          {messages.map((msg, index) => {
            const isUser = msg.role === "user";
            const hasMarkdown = msg.content.includes("**") || msg.content.includes("*") || msg.content.includes("\n");
            return (
              <div key={index} className="w-full max-w-4xl mx-auto space-y-1">
                <div className="flex items-center justify-between text-[11px] tracking-[0.3em] text-amber-900/70 uppercase">
                  <span>{isUser ? "Investigator" : "Keeper"}</span>
                  <span className="text-slate-500">
                    Entry {index + 1 < 10 ? `0${index + 1}` : index + 1}
                  </span>
                </div>
                <div className="px-1">
                  {isUser ? (
                    hasMarkdown ? (
                      <MarkdownText
                        text={msg.content}
                        className="leading-relaxed text-[15px] font-serif text-slate-900"
                      />
                    ) : (
                      <div className="whitespace-pre-wrap leading-relaxed text-[15px] font-serif text-slate-900">
                        {msg.content}
                      </div>
                    )
                  ) : hasMarkdown ? (
                    <MarkdownText
                      text={msg.content}
                      className="leading-relaxed text-[15px] text-slate-900"
                    />
                  ) : (
                    <TypewriterText
                      text={msg.content}
                      active={!typedMessagesRef.current.has(index)}
                      onComplete={() => typedMessagesRef.current.add(index)}
                      className="leading-relaxed text-[15px] text-slate-900"
                    />
                  )}
                </div>
              </div>
            );
          })}
          {loading && (
            <div className="w-full max-w-4xl mx-auto space-y-1">
              <div className="flex items-center justify-between text-[11px] tracking-[0.3em] text-amber-900/70 uppercase">
                <span>Keeper</span>
                <span className="text-slate-500">Entry ...</span>
              </div>
              <div className="px-1 flex items-center gap-3 text-slate-500">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
                <span className="text-sm">Keeper is composing the next entry...</span>
              </div>
            </div>
          )}
          
          {/* Dice Roll Button - shown when there's a pending dice request */}
          {pendingDiceRequest && (
            <div className="max-w-4xl mx-auto mb-4">
              <div className="rounded-2xl bg-amber-100/90 border-2 border-amber-600/60 shadow-lg px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">🎲</span>
                  <div>
                    <p className="font-semibold text-slate-900">
                      {pendingDiceRequest.type === "dice"
                        ? `${pendingDiceRequest.skillName} Check Required`
                        : "Sanity Check Required"}
                    </p>
                    {pendingDiceRequest.type === "dice" && (
                      <p className="text-xs text-slate-600 mt-1">
                        Difficulty: {pendingDiceRequest.difficulty} | Value: {pendingDiceRequest.skillValue}
                      </p>
                    )}
                    {pendingDiceRequest.type === "san" && (
                      <p className="text-xs text-slate-600 mt-1">
                        Current SAN: {pendingDiceRequest.currentSan} | Potential Loss: {pendingDiceRequest.sanLoss}
                      </p>
                    )}
                  </div>
                </div>
                <button
                  onClick={handleDiceRollClick}
                  disabled={loading}
                  className="px-6 py-3 rounded-xl bg-gradient-to-r from-amber-600 to-rose-500 text-slate-950 font-semibold shadow-lg shadow-amber-900/40 hover:from-amber-500 hover:to-rose-400 disabled:from-slate-500 disabled:to-slate-500 disabled:text-slate-300 disabled:cursor-not-allowed disabled:shadow-none transition-all"
                >
                  Roll Dice
                </button>
              </div>
            </div>
          )}
          
          <div className="max-w-4xl mx-auto rounded-2xl bg-amber-50/85 border border-amber-900/40 shadow-[0_18px_45px_rgba(0,0,0,0.45)] backdrop-blur-sm px-6 py-5 space-y-4 text-slate-900">
            <div className="flex items-center justify-between">
              <p className="text-xs uppercase tracking-[0.3em] text-amber-900/80 font-semibold">
                Your Next Entry
              </p>
              <span className="text-xs text-amber-900/70">Ctrl / Cmd + Enter to send</span>
            </div>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              rows={5}
              placeholder="Describe your action as if writing a journal entry on worn parchment..."
              className="w-full bg-transparent border border-amber-900/40 rounded-xl px-4 py-3 text-[15px] font-serif text-slate-900 placeholder:text-amber-900/60 focus:border-amber-700 focus:ring-2 focus:ring-amber-600/40 outline-none transition-all resize-none"
            />
            <div className="flex items-center justify-between">
              <p className="text-xs text-amber-900/80">Long entries encouraged—paint the scene.</p>
              <button
                onClick={handleSend}
                disabled={!input.trim() || loading}
                className="px-6 py-3 rounded-xl bg-gradient-to-r from-amber-600 to-rose-500 text-slate-950 font-semibold shadow-lg shadow-amber-900/40 hover:from-amber-500 hover:to-rose-400 disabled:from-slate-500 disabled:to-slate-500 disabled:text-slate-300 disabled:cursor-not-allowed disabled:shadow-none transition-all"
              >
                Submit Entry
              </button>
            </div>
          </div>
          
          <div ref={messagesEndRef} />
        </div>
      </main>

      <Dice3DOverlay
        show={showDiceOverlay}
        onClose={() => {
          setShowDiceOverlay(false);
          // Don't clear pending request if user closes overlay without rolling
        }}
        rollNotation={diceNotation}
        onResult={(value) => {
          if (pendingDiceRequest) {
            // Handle dice result for pending request
            handleDiceResult(value);
          } else {
            // For test rolls we record the raw d10 value
            setTestRoll(value);
          }
        }}
      />
    </div>
  );
}

