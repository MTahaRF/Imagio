"""
server.py — Imagio FastAPI Backend
===================================
Single endpoint:  POST /generate
  Request  : { "topic": "...", "lang_code": "en" }
  Response : video/mp4 file (bytes, served from memory)

Run with:
    uvicorn server:app --reload --host 0.0.0.0 --port 8000
"""

import os
import sys
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("imagio.server")

# Ensure the Imagio package root is on the path
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from pipeline import run_pipeline
from src.languages import list_languages

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Imagio API",
    description="Generates animated educational videos from a text prompt.",
    version="1.0.0",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
# Use wildcard for development — lock this down to specific origins in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # covers all localhost variants, ports, and IPs
    allow_credentials=False,      # must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread pool so the long-running pipeline doesn't block the event loop
_executor = ThreadPoolExecutor(max_workers=2)

# ── Schemas ────────────────────────────────────────────────────────────────────
class GenerateRequest(BaseModel):
    topic: str
    lang_code: str = "en"

# ── Endpoints ──────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    logger.info("GET / — health check")
    return {"status": "ok", "message": "Imagio API is running."}


@app.get("/languages")
def get_languages():
    """Returns the list of supported languages."""
    logger.info("GET /languages")
    return list_languages()


@app.post("/generate")
async def generate_video(req: GenerateRequest):
    """
    Runs the full Imagio pipeline and returns the generated MP4 as raw bytes.

    ── Key design decisions ────────────────────────────────────────────────────
    1. Pipeline runs in a ThreadPoolExecutor (non-blocking to the event loop).
    2. We READ the video into memory BEFORE letting the pipeline clean up the
       file. This avoids the race condition where clean_up=True deletes the
       file before FileResponse finishes streaming it.
    3. We use asyncio.get_running_loop() — get_event_loop() is deprecated in
       Python 3.10+ and raises a DeprecationWarning.
    4. Response time can be 1-5 minutes — the client must use a long timeout.
    """
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    logger.info(f"POST /generate  topic={topic!r}  lang={req.lang_code!r}")

    # ── Run pipeline in thread pool ────────────────────────────────────────────
    loop = asyncio.get_running_loop()   # ← fix: get_event_loop() is deprecated

    try:
        video_path: str | None = await loop.run_in_executor(
            _executor,
            lambda: run_pipeline(
                topic=topic,
                lang_code=req.lang_code,
                clean_up=False,         # ← fix: we manage cleanup ourselves below
            ),
        )
    except Exception as exc:
        logger.exception(f"Pipeline raised an exception: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline error: {exc}",
        )

    logger.info(f"Pipeline returned: {video_path!r}")

    if not video_path or not os.path.exists(video_path):
        logger.error("Pipeline returned no video path or file does not exist.")
        raise HTTPException(
            status_code=422,
            detail=(
                "Pipeline failed to produce a video. "
                "The topic may have been rejected as off-topic, or a render error occurred. "
                "Check the server logs for details."
            ),
        )

    # ── Read into memory FIRST, then clean up the file ────────────────────────
    # FileResponse streams from disk, which races with cleanup deletion.
    # Reading bytes here is safe — video is typically 5-30 MB.
    logger.info(f"Reading video into memory: {video_path}")
    with open(video_path, "rb") as f:
        video_bytes = f.read()

    logger.info(f"Video loaded: {len(video_bytes) / 1024:.1f} KB")


    filename = os.path.basename(video_path)
    logger.info(f"Sending video response: {filename}")

    return Response(
        content=video_bytes,
        media_type="video/mp4",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
            "Content-Length": str(len(video_bytes)),
        },
    )