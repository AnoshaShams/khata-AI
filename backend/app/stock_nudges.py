"""
Voice-based Stock Nudges (FR8, per original spec): detect spoken mentions of
an item running out — e.g. "chini khatam ho gayi" (sugar ran out) — and log a
flag so the shopkeeper gets reminded to restock.

This is a separate, standalone detector from parser.py's transaction parsing.
A spoken utterance might be a transaction, a stock mention, both, or neither —
this module only answers "does this text mention something running out, and
if so, what?"

Mirrors parser.py's exact calling pattern (same OpenAI-compatible client,
same model, same JSON-extraction approach) since it's proven to work.
"""
import json
import re

from openai import OpenAI, APIStatusError

from app.config import settings
from app.schemas import ExtractedText

_client = OpenAI(api_key=settings.dashscope_api_key, base_url=settings.dashscope_base_url)

SYSTEM_PROMPT = """You check a spoken transcript from a Pakistani shopkeeper for a mention
that an item/product has run out or is running low. The transcript may be in Urdu
(transliterated), English, or a natural mix of both.

Vocabulary for "ran out"/"finished"/"low stock":
- "khatam ho gaya"/"khatam ho gayi" = finished/ran out
- "kam reh gaya"/"kam reh gayi" = running low
- "stock nahi hai"/"stock khatam" = no stock

This may appear alone ("Chini khatam ho gayi") or alongside an unrelated transaction
mention in the same sentence — only extract the stock-related part if present.

Output ONLY one JSON object, no prose, no markdown fences:
{"item": "string"}

If there is NO mention of an item running out or low, output:
{"item": null}
"""


def _extract_json_object(raw: str) -> dict:
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    return json.loads(cleaned)


def detect_stock_mention(extracted: ExtractedText) -> str | None:
    """
    Returns the item name if the transcript mentions something running out or
    low, otherwise None. Does not raise on "no mention found" — that's a
    normal, expected result, not an error. Raises ValueError only on an
    actual API failure.
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
        raise ValueError(f"Stock-check API call failed: {e}") from e

    raw = response.choices[0].message.content or "{}"

    try:
        data = _extract_json_object(raw)
    except (json.JSONDecodeError, AttributeError):
        return None

    item = data.get("item")
    if not item or not isinstance(item, str):
        return None
    return item.strip()