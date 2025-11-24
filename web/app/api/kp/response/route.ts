import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  let currentScene = "arrival_village";
  try {
    const body = await request.json();
    const { user_input, character, chat_history, api_key, current_scene } = body;
    currentScene = current_scene || "arrival_village";

    const pythonBackendUrl = process.env.PYTHON_BACKEND_URL || "http://localhost:8000";

    const response = await fetch(`${pythonBackendUrl}/api/kp/response`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_input,
        character,
        chat_history,
        api_key,
        current_scene,
      }),
    });

    if (!response.ok) {
      throw new Error(`Python backend error: ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("KP response API error:", error);
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Unknown error",
        response: "⚠️ Error: Unable to reach KP backend.",
        current_scene: currentScene,
      },
      { status: 500 }
    );
  }
}

