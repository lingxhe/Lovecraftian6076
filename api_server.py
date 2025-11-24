"""
FastAPI bridge for Next.js frontend.
Run locally: uvicorn api_server:app --reload --port 8000
"""

import os
import sys
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.kp_agent import get_kp_response  # noqa: E402
from utils.logging import get_logger, init_logger, log_message  # noqa: E402

app = FastAPI(title="CoC Solo API")


allowed_origins = [
  "http://localhost:3000",
  "http://127.0.0.1:3000",
]
extra_origins = os.getenv("ALLOWED_ORIGINS", "")
if extra_origins:
  allowed_origins.extend([origin.strip() for origin in extra_origins.split(",") if origin.strip()])

app.add_middleware(
  CORSMiddleware,
  allow_origins=allowed_origins,
  allow_origin_regex=r"https://.*\.vercel\.app",
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


class KPRequest(BaseModel):
  user_input: str
  character: Dict[str, Any]
  chat_history: List[Dict[str, str]]
  api_key: str
  current_scene: str = "arrival_village"


class KPResult(BaseModel):
  response: str
  current_scene: str
  character: Optional[Dict[str, Any]] = None


@app.post("/api/kp/response", response_model=KPResult)
async def api_kp_response(payload: KPRequest):
  try:
    logger = get_logger()
    if not logger:
      init_logger(payload.character.get("name", "Investigator"), enable_print_capture=True)

    log_message("user", payload.user_input, payload.current_scene)

    result = get_kp_response(
      user_input=payload.user_input,
      character=payload.character,
      chat_history=payload.chat_history,
      api_key=payload.api_key,
      current_scene=payload.current_scene,
    )

    new_scene = result.get("current_scene", payload.current_scene)
    log_message("assistant", result["response"], new_scene)

    return KPResult(
      response=result["response"],
      current_scene=new_scene,
      character=result.get("character"),
    )
  except Exception as exc:
    raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/logs/download")
async def api_download_log(character: str):
  try:
    logger = get_logger()

    log_file = None
    if logger and logger.log_file:
      log_file = logger.log_file
    else:
      log_dir = os.path.join(os.getcwd(), "logs")
      if not os.path.exists(log_dir):
        raise HTTPException(status_code=404, detail="Logs directory not found")
      candidates = [
        os.path.join(log_dir, name)
        for name in os.listdir(log_dir)
        if name.lower().endswith(".md") and character.lower() in name.lower()
      ]
      if not candidates:
        raise HTTPException(status_code=404, detail="Log file not found for character")
      candidates.sort(key=os.path.getmtime, reverse=True)
      log_file = candidates[0]

    return FileResponse(
      log_file,
      filename=os.path.basename(log_file),
      media_type="text/markdown",
    )
  except HTTPException:
    raise
  except Exception as exc:
    raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/health")
async def api_health():
  return {"status": "ok"}


if __name__ == "__main__":
  import uvicorn

  uvicorn.run(app, host="0.0.0.0", port=8000)

