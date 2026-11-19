"""
DocuSpeak – FastAPI Backend
Endpoints:
  POST /parse          – upload file → returns extracted text
  POST /synthesize     – text + voice options → returns MP3 audio
  POST /convert        – upload file + voice options → returns MP3 directly
  GET  /voices         – returns full voice catalogue
  GET  /health         – health check
  GET  /preview        – returns first N chars of parsed text (for preview)
"""
from __future__ import annotations
import io
import os
import uuid
import base64
import asyncio
import pathlib
import tempfile
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from document_parser import parse_document
from tts_engine import synthesize_async, get_voice_catalogue

app = FastAPI(
    title="DocuSpeak API",
    description="Document-to-Audio conversion backend",
    version="1.0.0",
)

# Allow all origins for local Flutter web app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── /health ──────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "service": "DocuSpeak API v1.0"}


# ── /voices ──────────────────────────────────────────────────────────────────
@app.get("/voices")
def voices():
    return get_voice_catalogue()


# ── /parse ───────────────────────────────────────────────────────────────────
@app.post("/parse")
async def parse_endpoint(file: UploadFile = File(...)):
    """
    Upload a document; returns its extracted text.
    The text is VERBATIM – no AI rewriting.
    """
    data = await file.read()
    if not data:
        raise HTTPException(400, "Uploaded file is empty.")
    try:
        text = parse_document(file.filename or "upload", data)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(422, str(exc))
    char_count = len(text)
    word_count = len(text.split())
    return {
        "filename": file.filename,
        "char_count": char_count,
        "word_count": word_count,
        "text": text,
    }


# ── /synthesize ──────────────────────────────────────────────────────────────
@app.post("/synthesize")
async def synthesize_endpoint(
    text:     str = Form(...),
    voice_id: str = Form("en-US-JennyNeural"),
    rate:     str = Form("+0%"),
    pitch:    str = Form("+0Hz"),
):
    """
    Convert raw text to MP3.
    Returns audio/mpeg stream.
    """
    if not text.strip():
        raise HTTPException(400, "text is empty.")
    try:
        audio = await synthesize_async(text, voice_id, rate, pitch)
    except Exception as exc:
        raise HTTPException(500, f"TTS error: {exc}")
    return StreamingResponse(
        io.BytesIO(audio),
        media_type="audio/mpeg",
        headers={"Content-Disposition": 'attachment; filename="speech.mp3"'},
    )


# ── /convert (one-shot: parse + synthesize) ───────────────────────────────────
@app.post("/convert")
async def convert_endpoint(
    file:     UploadFile = File(...),
    voice_id: str = Form("en-US-JennyNeural"),
    rate:     str = Form("+0%"),
    pitch:    str = Form("+0Hz"),
    start:    int = Form(0),      # character offset to start from
    end:      int = Form(-1),     # character offset to end at (-1 = full)
):
    """
    Upload a file + voice params → download MP3 directly.
    Optionally pass start/end to read only a portion of the document.
    """
    data = await file.read()
    if not data:
        raise HTTPException(400, "Uploaded file is empty.")
    try:
        text = parse_document(file.filename or "upload", data)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(422, str(exc))

    # Slice if requested
    if end == -1:
        slice_text = text[start:]
    else:
        slice_text = text[start:end]

    if not slice_text.strip():
        raise HTTPException(400, "Selected text range is empty.")

    try:
        audio = await synthesize_async(slice_text, voice_id, rate, pitch)
    except Exception as exc:
        raise HTTPException(500, f"TTS error: {exc}")

    safe_name = pathlib.Path(file.filename or "output").stem + ".mp3"
    return StreamingResponse(
        io.BytesIO(audio),
        media_type="audio/mpeg",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )


# ── /preview ─────────────────────────────────────────────────────────────────
@app.post("/preview")
async def preview_endpoint(
    file:  UploadFile = File(...),
    chars: int = Form(500),
):
    """Parse document and return first *chars* characters for preview."""
    data = await file.read()
    if not data:
        raise HTTPException(400, "Uploaded file is empty.")
    try:
        text = parse_document(file.filename or "upload", data)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(422, str(exc))
    return {
        "preview": text[:chars],
        "total_chars": len(text),
        "total_words": len(text.split()),
    }


# ── /synthesize_b64 (for Flutter web workaround) ─────────────────────────────
@app.post("/synthesize_b64")
async def synthesize_b64_endpoint(
    text:     str = Form(...),
    voice_id: str = Form("en-US-JennyNeural"),
    rate:     str = Form("+0%"),
    pitch:    str = Form("+0Hz"),
):
    """Same as /synthesize but returns base64-encoded MP3 in JSON (for web)."""
    if not text.strip():
        raise HTTPException(400, "text is empty.")
    try:
        audio = await synthesize_async(text, voice_id, rate, pitch)
    except Exception as exc:
        raise HTTPException(500, f"TTS error: {exc}")
    b64 = base64.b64encode(audio).decode("utf-8")
    return JSONResponse({"audio_b64": b64, "mime": "audio/mpeg"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
