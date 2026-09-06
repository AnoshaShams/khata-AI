"""
Text-to-speech: turns a text summary into spoken audio bytes.
This is Anosha's module — used for the Spoken Daily Summary feature.

Uses cosyvoice-v3-plus via the native `dashscope` SDK (NOT the openai client).

CORRECTION LOG (2026-09-06): earlier version of this file briefly switched to
qwen-audio-3.0-tts-flash after finding a code sample under the wrong tab on
Model Studio's docs page (Qwen-Audio-TTS tab, not CosyVoice tab). The CosyVoice
tab's own sample confirms cosyvoice-v3-plus works fine with a system voice
(e.g. "longanyang") in the Singapore/international region — the Beijing-only
voice-cloning restriction only applies to the newer cosyvoice-v3.5-plus/flash
variants, not v3-plus. Reverted back to the originally assigned model.

Confirmed from Model Studio docs (2026-09-06), CosyVoice tab, Singapore region:
    import dashscope
    from dashscope.audio.tts_v2 import *
    dashscope.api_key = os.environ.get('DASHSCOPE_API_KEY')
    dashscope.base_websocket_api_url = 'wss://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/api-ws/v1/inference'
    model = "cosyvoice-v3-flash"  # or cosyvoice-v3-plus — same voice list applies
    voice = "longanyang"
    synthesizer = SpeechSynthesizer(model=model, voice=voice)
    audio = synthesizer.call("some text")

STILL TO VERIFY:
- Whether "longanyang" actually supports Urdu and/or English well — the doc
  explicitly says voices differ in language support. Check the CosyVoice
  voice list on Model Studio for one confirmed to handle Urdu/English before
  the demo, and set QWEN_AUDIO_TTS_VOICE in .env accordingly.
"""

import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer

from app.config import settings

dashscope.api_key = settings.dashscope_api_key

# Same workspace host as the ASR endpoint, different path — this is the
# native WebSocket inference endpoint for the Singapore region.
_ws_host = settings.dashscope_base_url.replace("/compatible-mode/v1", "")
dashscope.base_websocket_api_url = _ws_host.replace("https://", "wss://") + "/api-ws/v1/inference"


def synthesize_speech(text: str, voice: str | None = None) -> bytes:
    """
    Converts text into speech audio.

    Args:
        text: the text to speak (e.g. a daily summary sentence).
        voice: voice/speaker ID. Falls back to QWEN_AUDIO_TTS_VOICE from .env,
            or "longanyang" (the doc's example) as a last resort — verify this
            voice actually supports Urdu/English before relying on it in the
            demo; check Model Studio's CosyVoice voice list for a better fit
            if needed.

    Returns:
        Raw audio bytes (MP3 format, per the model's documented example).

    Raises:
        ValueError if text is empty or the API returns no audio.
    """
    if not text or not text.strip():
        raise ValueError("Cannot synthesize speech from empty text.")

    voice_id = voice or getattr(settings, "qwen_audio_tts_voice", None) or "longanyang"

    synthesizer = SpeechSynthesizer(model=settings.qwen_audio_tts_model, voice=voice_id)
    audio_bytes = synthesizer.call(text)

    if not audio_bytes:
        raise ValueError("TTS call returned no audio data.")

    return audio_bytes