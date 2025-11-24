import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export interface Character {
  name: string;
  str: number;
  int: number;
  pow: number;
  spot: number;
  listen: number;
  stealth: number;
  charm: number;
  luck: number;
  san: number;
  avatar: string;
  background_story: string;
}

export interface Message {
  role: "user" | "assistant";
  content: string;
}

interface AppState {
  character: Character | null;
  messages: Message[];
  currentScene: string;
  apiKey: string;
  setCharacter: (character: Character | null) => void;
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  setCurrentScene: (scene: string) => void;
  setApiKey: (key: string) => void;
  resetConversation: () => void;
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      character: null,
      messages: [],
      currentScene: "arrival_village",
      apiKey: "",
      setCharacter: (character) => set({ character }),
      setMessages: (messages) => set({ messages }),
      addMessage: (message) =>
        set((state) => ({ messages: [...state.messages, message] })),
      setCurrentScene: (scene) => set({ currentScene: scene }),
      setApiKey: (key) => set({ apiKey: key }),
      resetConversation: () =>
        set({
          messages: [],
          currentScene: "arrival_village",
        }),
    }),
    {
      name: "coc-solo-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);

