import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    dashscope_api_key: str = os.getenv("DASHSCOPE_API_KEY", "")
    # No safe universal default here — this is a per-workspace dedicated domain,
    # not a generic Alibaba Cloud URL. Must come from your own .env.
    dashscope_base_url: str = os.getenv("DASHSCOPE_BASE_URL", "")
    qwen_vl_model: str = os.getenv("QWEN_VL_MODEL", "qwen3.7-plus")
    qwen_text_model: str = os.getenv("QWEN_TEXT_MODEL", "qwen3.7-plus")
    # Anosha's track — not consumed by ocr.py/parser.py, kept here so config.py
    # is the one shared place both of you read model settings from.
    qwen_audio_asr_model: str = os.getenv("QWEN_AUDIO_ASR_MODEL", "qwen-audio-3.0-asr-flash")
    qwen_audio_tts_model: str = os.getenv("QWEN_AUDIO_TTS_MODEL", "qwen-audio-3.0-tts-flash")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./khata.db")


settings = Settings()

if not settings.dashscope_api_key:
    print("[WARN] DASHSCOPE_API_KEY is not set. OCR and parser calls will fail.")
if not settings.dashscope_base_url:
    print("[WARN] DASHSCOPE_BASE_URL is not set. Copy it from your Model Studio API-Key page.")
