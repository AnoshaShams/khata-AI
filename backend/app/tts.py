"""
Text-to-speech: turns a text summary into spoken audio bytes.
This is Anosha's module — used for the Spoken Daily Summary feature.

Uses cosyvoice-v3-plus via DashScope.

IMPORTANT — verify before relying on this in the demo:
Two different call patterns exist across Alibaba's docs/SDKs for CosyVoice:
  1. An OpenAI-compatible `/v1/audio/speech`-style call (like OpenAI's own TTS API).
  2. The native DashScope `SpeechSynthesizer` SDK pattern (dashscope package).
This file implements option 1 (OpenAI-compatible) since it matches the pattern
Mariam is already using for OCR/parsing (an OpenAI client pointed at
DASHSCOPE_BASE_URL). Open the Model Studio page for cosyvoice-v3-plus and check
its code sample — if it's actually the `dashscope` SDK pattern instead, swap this
implementation for that (install `dashscope`, use `SpeechSynthesizer.call(...)`).
"""

from openai import OpenAI

from app.config import settings

_client = OpenAI(
    api_key=settings.dashscope_api_key,
    base_url=settings.dashscope_base_url,
)


def synthesize_speech(text: str, voice: str | None = None) -> bytes:
    """
    Converts text into speech audio.

    Args:
        text: the text to speak (e.g. a daily summary sentence).
        voice: optional voice/speaker ID, if CosyVoice's Model Studio page shows
            one is required. Leave None to use the model's default.

    Returns:
        Raw audio bytes (format depends on the model — check the Model Studio
        page; commonly WAV or MP3). Save to a file or stream directly to the
        frontend as a response.

    Raises:
        ValueError if text is empty.
    """
    if not text or not text.strip():
        raise ValueError("Cannot synthesize speech from empty text.")

    kwargs = {
        "model": settings.qwen_audio_tts_model,
        "input": text,
    }
    if voice:
        kwargs["voice"] = voice

    response = _client.audio.speech.create(**kwargs)

    # openai-python's speech.create() returns a response object with audio bytes
    # accessible via .content in recent SDK versions. If this errors, check
    # whether the installed openai package version expects
    # `.stream_to_file(path)` or `.read()` instead — adjust accordingly.
    return response.content
