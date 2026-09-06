"""
Speech-to-text: turns recorded audio into the Extracted-Text contract shape
(see docs/CONTRACTS.md). This is Anosha's module — voice input path.

Uses qwen-audio-3.0-asr-flash via DashScope's native HTTP API.

IMPORTANT: per Alibaba's own docs, this specific model "does not support SDK
calls" — so this uses raw HTTP via `requests`, NOT the openai client (unlike
Mariam's ocr.py/parser.py, which use the OpenAI-compatible endpoint for
qwen3.7-plus — that's a different endpoint/model family, this one is separate).

Confirmed from Model Studio docs (2026-09-06):
  Endpoint: https://{workspace}.ap-southeast-1.maas.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation
  Headers: Authorization: Bearer <key>, Content-Type: application/json, X-DashScope-SSE: disable
  Body: {"model", "input": {"messages": [...]}, "parameters": {"format", "sample_rate"}}

STILL TO VERIFY (not confirmed from docs seen so far):
- Whether `input_audio.data` accepts a base64 data URL (data:<mime>;base64,<data>)
  or ONLY a public audio URL. The example shown used a URL placeholder. If base64
  fails, check the "Audio specifications" page linked from the same doc for the
  actual accepted input types — you may need to upload the audio somewhere
  temporarily and pass its URL instead.
- The exact response JSON shape for a successful call — adjust `_parse_response`
  below once you see a real 200 response.
"""

import base64
import datetime
import requests

from app.config import settings
from app.schemas import ExtractedText

# Derived from DASHSCOPE_BASE_URL by stripping the "/compatible-mode/v1" suffix
# used for the OpenAI-compatible text/vision models, then pointing at the
# native multimodal-generation path this ASR model actually requires.
_ASR_ENDPOINT = settings.dashscope_base_url.replace("/compatible-mode/v1", "") + \
    "/api/v1/services/aigc/multimodal-generation/generation"


def _guess_format(filename: str) -> str:
    """Returns the short format string this API expects (e.g. 'wav', 'mp3')."""
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else "wav"
    # Per the doc's example, plain short extension strings are expected here
    # (not full MIME types) — adjust if Audio specifications says otherwise.
    return ext if ext in ("wav", "mp3", "m4a", "webm", "ogg", "opus") else "wav"


def _call_asr(audio_bytes: bytes, filename: str) -> dict:
    b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
    fmt = _guess_format(filename)
    mime = {
        "wav": "audio/wav", "mp3": "audio/mpeg", "m4a": "audio/mp4",
        "webm": "audio/webm", "ogg": "audio/ogg", "opus": "audio/opus",
    }.get(fmt, "audio/wav")
    data_url = f"data:{mime};base64,{b64_audio}"

    payload = {
        "model": settings.qwen_audio_asr_model,
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {"data": data_url},
                        }
                    ],
                }
            ]
        },
        "parameters": {
            "format": fmt,
            "sample_rate": "16000",
        },
    }
    headers = {
        "Authorization": f"Bearer {settings.dashscope_api_key}",
        "Content-Type": "application/json",
        "X-DashScope-SSE": "disable",
    }

    resp = requests.post(_ASR_ENDPOINT, headers=headers, json=payload, timeout=30)

    if resp.status_code != 200:
        raise ValueError(
            f"ASR API returned {resp.status_code}: {resp.text[:500]}"
        )

    return resp.json()


def _parse_response(response_json: dict) -> str:
    """
    Extracts the transcript text from the response.
    Confirmed shape (from a real successful call, 2026-09-06):
    the transcript is at response_json["output"]["text"] (also duplicated at
    the top level as response_json["text"]).
    """
    text = None
    if isinstance(response_json.get("output"), dict):
        text = response_json["output"].get("text")
    if not text:
        text = response_json.get("text")
    if not text:
        raise ValueError(f"Unexpected ASR response shape: {response_json!r}")
    return text.strip()


def transcribe_audio(audio_bytes: bytes, filename: str = "recording.wav",
                      language_mode: str = "urdu") -> ExtractedText:
    """
    Main entry point for the voice input path.

    Returns:
        ExtractedText matching docs/CONTRACTS.md — ready to POST to
        /ledger/parse-voice.

    Raises:
        ValueError if the audio can't be transcribed (API error, empty result).
    """
    response_json = _call_asr(audio_bytes, filename)
    text = _parse_response(response_json)

    if not text:
        raise ValueError("Got an empty transcript — audio may be silent or unclear.")

    return ExtractedText(
        text=text,
        source="voice",
        language_mode=language_mode,
        confidence=1.0,  # placeholder — replace if response includes a real value
        timestamp=datetime.datetime.utcnow().isoformat() + "Z",
    )