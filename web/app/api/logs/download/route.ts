import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const character = searchParams.get("character");

    if (!character) {
      return NextResponse.json({ error: "Character parameter required" }, { status: 400 });
    }

    const pythonBackendUrl = process.env.PYTHON_BACKEND_URL || "http://localhost:8000";
    const response = await fetch(
      `${pythonBackendUrl}/api/logs/download?character=${encodeURIComponent(character)}`
    );

    if (!response.ok) {
      throw new Error(await response.text());
    }

    const blob = await response.blob();
    return new NextResponse(blob, {
      headers: {
        "Content-Type": "text/markdown",
        "Content-Disposition": `attachment; filename="chat_log_${character}.md"`,
      },
    });
  } catch (error) {
    console.error("Download log API error:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}

