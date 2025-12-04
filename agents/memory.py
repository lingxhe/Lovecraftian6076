from typing import Any, Dict, List

from langchain_openai import ChatOpenAI


def _build_summary_prompt(
    chat_history: List[Dict[str, str]],
    character: Dict[str, Any],
    current_scene: str,
) -> str:
    """Build a concise prompt for summarizing older chat history."""
    name = character.get("name", "Investigator")
    san = character.get("san", 60)

    # We only feed in the older part, but we still give a bit of context
    history_text = ""
    for msg in chat_history:
        role = msg.get("role", "assistant")
        prefix = "Player" if role == "user" else "Keeper"
        content = msg.get("content", "").strip()
        if not content:
            continue
        history_text += f"{prefix}: {content}\n\n"

    prompt = f"""
You are helping maintain a concise memory for a solo Call of Cthulhu game log.

Player character: {name}, current SAN {san}, current scene id: {current_scene}.

Below is an excerpt of the **older** part of the conversation between the player and the Keeper.
Your job is to rewrite it as a short, information-dense summary that preserves:
- Key events and discoveries
- Important NPCs and their attitudes
- Scene transitions and locations visited
- Critical dice/SAN results that affected the story
- Any persistent character changes (e.g., SAN loss, injuries, promises, enemies)

Do **not** invent new events. Do **not** include meta-comments about summarizing.
Write 1 to 3 short sentences or a compact bullet list in plain Markdown.

Older conversation:

{history_text}
"""

    return prompt.strip()


def compress_chat_history(
    chat_history: List[Dict[str, str]],
    character: Dict[str, Any],
    current_scene: str,
    api_key: str,
    *,
    min_messages_before_compress: int = 24,
    keep_recent_messages: int = 8,
) -> List[Dict[str, str]]:
    """
    Optionally compress older chat history into a single summary message.

    - If history is short, return it unchanged.
    - If long, summarize all but the most recent N messages into one assistant message,
      then append the recent messages after that.
    """
    # Simple length-based heuristic; token-based would require extra deps
    if len(chat_history) < min_messages_before_compress:
        return chat_history

    # If we have no API key here, we can't summarize safely → return as-is
    if not api_key:
        return chat_history

    # Split into older and recent segments
    cutoff = max(0, len(chat_history) - keep_recent_messages)
    older = chat_history[:cutoff]
    recent = chat_history[cutoff:]

    if not older:
        return chat_history

    # Build summarization prompt
    prompt = _build_summary_prompt(older, character, current_scene)

    # Use a small, cheap model; follow the same config style as kp_agent
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        api_key=api_key,
    )

    summary_msg = llm.invoke(prompt)

    # Represent summary as an assistant message that future turns can see
    summary_entry: Dict[str, str] = {
        "role": "assistant",
        "content": f"**Summary of earlier events:**\n\n{summary_msg.content}",
    }

    return [summary_entry] + recent


