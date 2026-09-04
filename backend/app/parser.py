"""
Voice path only: Extracted-Text contract (from Anosha's Whisper transcript) ->
Parsed Transaction contract. The OCR path does NOT use this — Qwen2-VL handles
extraction+structuring in one call (see ocr.py).

Anosha's Confirmation Loop can build against this from Day 1 using a stub
transcript matching schemas.ExtractedText, before her real STT is wired up.
"""
import json
import re

from openai import OpenAI, APIStatusError

from app.config import settings
from app.schemas import ExtractedText, ParsedTransaction

_client = OpenAI(api_key=settings.dashscope_api_key, base_url=settings.dashscope_base_url)

SYSTEM_PROMPT = """You parse a spoken transcript from a Pakistani shopkeeper into a single
structured transaction. The transcript may be in Urdu (transliterated), English, or a
natural mix of both within one sentence (e.g. "Aslam ko paanch sau ka udhaar diya").

Vocabulary:
- "udhaar diya"/"credit diya"/"udhar de diya" = credit given -> type "credit"
- "wapas kiya"/"jama karwaya"/"paid"/"paisa de gaya" = payment received -> type "payment"
- Numbers may be spoken as words ("paanch sau" = 500, "do hazar" = 2000) or digits.

Output ONLY one JSON object, no prose, no markdown fences:
{"customer_name": "string", "amount": number, "type": "credit"|"payment", "item": "string or null"}

If the transcript is too unclear to extract a transaction at all, output:
{"customer_name": null, "amount": null, "type": null, "item": null}
"""


def _extract_json_object(raw: str) -> dict:
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    return json.loads(cleaned)


def parse_transcript(extracted: ExtractedText) -> ParsedTransaction | None:
    """
    Returns a ParsedTransaction, or None if the model couldn't extract anything
    usable (caller should surface this as "didn't catch that, try again" rather
    than silently guessing).
    """
    try:
        response = _client.chat.completions.create(
            model=settings.qwen_text_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Language mode: {extracted.language_mode}\nTranscript: {extracted.text}",
                },
            ],
            temperature=0.1,
        )
    except APIStatusError as e:
        if e.status_code == 403:
            raise ValueError(
                "This model's free quota has run out (AllocationQuota.FreeTierOnly)."
            ) from e
        raise ValueError(f"Parser API call failed: {e}") from e

    raw = response.choices[0].message.content or "{}"

    try:
        data = _extract_json_object(raw)
    except (json.JSONDecodeError, AttributeError):
        return None

    if not data.get("customer_name") or data.get("amount") is None or not data.get("type"):
        return None

    try:
        return ParsedTransaction(
            customer_name=data["customer_name"],
            amount=float(data["amount"]),
            type=data["type"],
            item=data.get("item"),
            confirmed=False,
        )
    except (ValueError, TypeError):
        return None
