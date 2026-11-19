"""
DocuSpeak – TTS Engine
Converts text to speech using edge-tts (Microsoft Azure Neural voices).
Supports 40+ languages with multiple AI voice options per language.
"""
from __future__ import annotations
import asyncio
import io
import re
import tempfile
import pathlib
import uuid
from typing import Optional

import edge_tts

# ── Voice catalogue ──────────────────────────────────────────────────────────
# Format: "Language (Region)" -> list of (voice_short_name, display_name)
VOICE_CATALOGUE: dict[str, list[dict]] = {
    "English (US)": [
        {"id": "en-US-JennyNeural",    "name": "Jenny (Female)"},
        {"id": "en-US-GuyNeural",      "name": "Guy (Male)"},
        {"id": "en-US-AriaNeural",     "name": "Aria (Female)"},
        {"id": "en-US-DavisNeural",    "name": "Davis (Male)"},
        {"id": "en-US-AmberNeural",    "name": "Amber (Female)"},
        {"id": "en-US-AnaNeural",      "name": "Ana (Female, Child)"},
    ],
    "English (UK)": [
        {"id": "en-GB-SoniaNeural",    "name": "Sonia (Female)"},
        {"id": "en-GB-RyanNeural",     "name": "Ryan (Male)"},
        {"id": "en-GB-LibbyNeural",    "name": "Libby (Female)"},
    ],
    "English (India)": [
        {"id": "en-IN-NeerjaNeural",   "name": "Neerja (Female)"},
        {"id": "en-IN-PrabhatNeural",  "name": "Prabhat (Male)"},
    ],
    "Hindi": [
        {"id": "hi-IN-SwaraNeural",    "name": "Swara (Female)"},
        {"id": "hi-IN-MadhurNeural",   "name": "Madhur (Male)"},
    ],
    "French": [
        {"id": "fr-FR-DeniseNeural",   "name": "Denise (Female)"},
        {"id": "fr-FR-HenriNeural",    "name": "Henri (Male)"},
    ],
    "German": [
        {"id": "de-DE-KatjaNeural",    "name": "Katja (Female)"},
        {"id": "de-DE-ConradNeural",   "name": "Conrad (Male)"},
    ],
    "Spanish (Spain)": [
        {"id": "es-ES-ElviraNeural",   "name": "Elvira (Female)"},
        {"id": "es-ES-AlvaroNeural",   "name": "Alvaro (Male)"},
    ],
    "Spanish (Mexico)": [
        {"id": "es-MX-DaliaNeural",    "name": "Dalia (Female)"},
        {"id": "es-MX-JorgeNeural",    "name": "Jorge (Male)"},
    ],
    "Chinese (Mandarin)": [
        {"id": "zh-CN-XiaoxiaoNeural", "name": "Xiaoxiao (Female)"},
        {"id": "zh-CN-YunxiNeural",    "name": "Yunxi (Male)"},
        {"id": "zh-CN-XiaohanNeural",  "name": "Xiaohan (Female)"},
    ],
    "Japanese": [
        {"id": "ja-JP-NanamiNeural",   "name": "Nanami (Female)"},
        {"id": "ja-JP-KeitaNeural",    "name": "Keita (Male)"},
    ],
    "Korean": [
        {"id": "ko-KR-SunHiNeural",    "name": "SunHi (Female)"},
        {"id": "ko-KR-InJoonNeural",   "name": "InJoon (Male)"},
    ],
    "Arabic": [
        {"id": "ar-SA-ZariyahNeural",  "name": "Zariyah (Female)"},
        {"id": "ar-SA-HamedNeural",    "name": "Hamed (Male)"},
    ],
    "Portuguese (Brazil)": [
        {"id": "pt-BR-FranciscaNeural","name": "Francisca (Female)"},
        {"id": "pt-BR-AntonioNeural",  "name": "Antonio (Male)"},
    ],
    "Russian": [
        {"id": "ru-RU-SvetlanaNeural", "name": "Svetlana (Female)"},
        {"id": "ru-RU-DmitryNeural",   "name": "Dmitry (Male)"},
    ],
    "Italian": [
        {"id": "it-IT-ElsaNeural",     "name": "Elsa (Female)"},
        {"id": "it-IT-DiegoNeural",    "name": "Diego (Male)"},
    ],
    "Dutch": [
        {"id": "nl-NL-ColetteNeural",  "name": "Colette (Female)"},
        {"id": "nl-NL-MaartenNeural",  "name": "Maarten (Male)"},
    ],
    "Polish": [
        {"id": "pl-PL-ZofiaNeural",    "name": "Zofia (Female)"},
        {"id": "pl-PL-MarekNeural",    "name": "Marek (Male)"},
    ],
    "Turkish": [
        {"id": "tr-TR-EmelNeural",     "name": "Emel (Female)"},
        {"id": "tr-TR-AhmetNeural",    "name": "Ahmet (Male)"},
    ],
    "Swedish": [
        {"id": "sv-SE-SofieNeural",    "name": "Sofie (Female)"},
        {"id": "sv-SE-MattiasNeural",  "name": "Mattias (Male)"},
    ],
    "Norwegian": [
        {"id": "nb-NO-PernilleNeural", "name": "Pernille (Female)"},
        {"id": "nb-NO-FinnNeural",     "name": "Finn (Male)"},
    ],
    "Danish": [
        {"id": "da-DK-ChristelNeural", "name": "Christel (Female)"},
        {"id": "da-DK-JeppeNeural",    "name": "Jeppe (Male)"},
    ],
    "Finnish": [
        {"id": "fi-FI-SelmaNeural",    "name": "Selma (Female)"},
        {"id": "fi-FI-HarriNeural",    "name": "Harri (Male)"},
    ],
    "Greek": [
        {"id": "el-GR-AthinaNeural",   "name": "Athina (Female)"},
        {"id": "el-GR-NestorasNeural", "name": "Nestoras (Male)"},
    ],
    "Hebrew": [
        {"id": "he-IL-HilaNeural",     "name": "Hila (Female)"},
        {"id": "he-IL-AvriNeural",     "name": "Avri (Male)"},
    ],
    "Thai": [
        {"id": "th-TH-PremwadeeNeural","name": "Premwadee (Female)"},
        {"id": "th-TH-NiwatNeural",    "name": "Niwat (Male)"},
    ],
    "Vietnamese": [
        {"id": "vi-VN-HoaiMyNeural",   "name": "HoaiMy (Female)"},
        {"id": "vi-VN-NamMinhNeural",  "name": "NamMinh (Male)"},
    ],
    "Indonesian": [
        {"id": "id-ID-GadisNeural",    "name": "Gadis (Female)"},
        {"id": "id-ID-ArdiNeural",     "name": "Ardi (Male)"},
    ],
    "Malay": [
        {"id": "ms-MY-YasminNeural",   "name": "Yasmin (Female)"},
        {"id": "ms-MY-OsmanNeural",    "name": "Osman (Male)"},
    ],
    "Tamil": [
        {"id": "ta-IN-PallaviNeural",  "name": "Pallavi (Female)"},
        {"id": "ta-IN-ValluvarNeural", "name": "Valluvar (Male)"},
    ],
    "Telugu": [
        {"id": "te-IN-ShrutiNeural",   "name": "Shruti (Female)"},
        {"id": "te-IN-MohanNeural",    "name": "Mohan (Male)"},
    ],
    "Bengali": [
        {"id": "bn-IN-TanishaaNeural", "name": "Tanishaa (Female)"},
        {"id": "bn-IN-BashkarNeural",  "name": "Bashkar (Male)"},
    ],
    "Ukrainian": [
        {"id": "uk-UA-PolinaNeural",   "name": "Polina (Female)"},
        {"id": "uk-UA-OstapNeural",    "name": "Ostap (Male)"},
    ],
    "Romanian": [
        {"id": "ro-RO-AlinaNeural",    "name": "Alina (Female)"},
        {"id": "ro-RO-EmilNeural",     "name": "Emil (Male)"},
    ],
    "Hungarian": [
        {"id": "hu-HU-NoemiNeural",    "name": "Noemi (Female)"},
        {"id": "hu-HU-TamasNeural",    "name": "Tamas (Male)"},
    ],
    "Czech": [
        {"id": "cs-CZ-VlastaNeural",   "name": "Vlasta (Female)"},
        {"id": "cs-CZ-AntoninNeural",  "name": "Antonin (Male)"},
    ],
    "Slovak": [
        {"id": "sk-SK-ViktoriaNeural", "name": "Viktoria (Female)"},
        {"id": "sk-SK-LukasNeural",    "name": "Lukas (Male)"},
    ],
    "Catalan": [
        {"id": "ca-ES-JoanaNeural",    "name": "Joana (Female)"},
        {"id": "ca-ES-EnricNeural",    "name": "Enric (Male)"},
    ],
}


# ── TTS helpers ───────────────────────────────────────────────────────────────
_CHUNK_LIMIT = 4000   # edge-tts handles ~5k chars; stay conservative

def _split_text(text: str, limit: int = _CHUNK_LIMIT) -> list[str]:
    """Split text into sentence-boundary chunks under *limit* chars."""
    sentences = re.split(r'(?<=[.!?…])\s+', text)
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 > limit:
            if current:
                chunks.append(current.strip())
            current = sentence
        else:
            current = (current + " " + sentence).strip()
    if current:
        chunks.append(current.strip())
    return chunks or [text]


async def _synthesize_chunk(text: str, voice: str, rate: str, pitch: str) -> bytes:
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    buf = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])
    return buf.getvalue()


async def synthesize_async(
    text: str,
    voice_id: str = "en-US-JennyNeural",
    rate: str = "+0%",
    pitch: str = "+0Hz",
) -> bytes:
    """
    Convert *text* to MP3 audio bytes using the specified edge-tts voice.
    *rate*  example values: "+20%", "-10%", "+0%"
    *pitch* example values: "+5Hz", "-10Hz", "+0Hz"
    """
    if not text.strip():
        raise ValueError("No text to synthesise.")

    chunks = _split_text(text)
    if len(chunks) == 1:
        return await _synthesize_chunk(text, voice_id, rate, pitch)

    # Synthesise all chunks concurrently then concatenate raw MP3
    tasks = [_synthesize_chunk(c, voice_id, rate, pitch) for c in chunks]
    results = await asyncio.gather(*tasks)
    return b"".join(results)


def synthesize(
    text: str,
    voice_id: str = "en-US-JennyNeural",
    rate: str = "+0%",
    pitch: str = "+0Hz",
) -> bytes:
    """Synchronous wrapper around synthesize_async."""
    return asyncio.run(synthesize_async(text, voice_id, rate, pitch))


def get_voice_catalogue() -> dict:
    return VOICE_CATALOGUE
