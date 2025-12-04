import { Character, Message } from "@/store/useStore";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "/api";

export interface KPResponse {
  response: string;
  current_scene: string;
  character?: Character;
  compressed_history?: Message[];
}

export async function getKPResponse(
  userInput: string,
  character: Character,
  chatHistory: Message[],
  apiKey: string,
  currentScene: string
): Promise<KPResponse> {
  const response = await fetch(`${API_BASE}/kp/response`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_input: userInput,
      character,
      chat_history: chatHistory,
      api_key: apiKey,
      current_scene: currentScene,
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

export async function downloadLog(characterName: string): Promise<Blob> {
  const response = await fetch(
    `${API_BASE}/logs/download?character=${encodeURIComponent(characterName)}`,
    {
      method: "GET",
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to download log: ${response.statusText}`);
  }

  return response.blob();
}

