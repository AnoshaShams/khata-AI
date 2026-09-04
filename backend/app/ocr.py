"""
Photo -> Parsed Transaction(s), in one Qwen2-VL call.

Per CONTRACTS.md: the OCR path does NOT go through the Extracted-Text contract.
Qwen2-VL reads the handwritten ledger photo (mixed Urdu/English, messy) and
outputs the Parsed Transaction shape directly. This module owns that call and
the JSON-safety net around it.

IMPORTANT: this must only ever be called from the backend. The DashScope key
must never be shipped to the browser (no VITE_-prefixed key, no calling this
endpoint's underlying API directly from React).
"""
import base64
import json
import re
from typing import List

from openai import OpenAI, APIStatusError

from app.config import settings
from app.schemas import ParsedTransaction

_client = OpenAI(api_key=settings.dashscope_api_key, base_url=settings.dashscope_base_url)

SYSTEM_PROMPT = """You are reading a photo of a handwritten Pakistani shopkeeper's ledger (khata).
The handwriting may mix Urdu script, Roman Urdu, and English on the same line or page.
Common words you will see: "udhaar"/"udhar" (credit given to a customer), "wapas"/"jama"/"paid"
(payment received), customer names, amounts in rupees (may be written as "500", "5 sau", "Rs 500").

Extract EVERY transaction line you can find. For each transaction, output:
- customer_name: the person's name as written (transliterate Urdu script to Roman Urdu if needed)
- amount: a number (rupees). If genuinely ambiguous (e.g. a smudged digit), make your best single
  guess but lower confidence is expected — do not refuse to output a number.
- type: "credit" if the shopkeeper GAVE the customer goods/money on credit (udhaar diya),
        "payment" if the customer PAID something back (udhaar wapas, jama, paid)
- item: what was bought/sold, if mentioned, else null

Output ONLY a JSON array, no prose, no markdown fences. Example:
[{"customer_name": "Aslam", "amount": 500, "type": "credit", "item": "atta"},
 {"customer_name": "Bilal", "amount": 200, "type": "payment", "item": null}]

If you cannot read anything usable on the page, output: []
"""


def _extract_json_array(raw: str) -> list:
    """Model sometimes wraps output in ```json fences despite instructions. Strip defensively."""
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    return json.loads(cleaned)


def extract_transactions_from_photo(image_bytes: bytes, mime_type: str = "image/jpeg") -> List[ParsedTransaction]:
    """
    Takes raw photo bytes, returns a list of ParsedTransaction (confirmed=False).
    Raises ValueError with the raw model output attached if parsing fails, so the
    caller can log it / surface a "couldn't read this photo, try again" message
    instead of crashing.
    """
    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64_image}"

    try:
        response = _client.chat.completions.create(
            model=settings.qwen_vl_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": data_url}},
                        {"type": "text", "text": "Extract all transactions from this ledger photo."},
                    ],
                },
            ],
            temperature=0.1,  # low temperature: this is extraction, not creative writing
        )
    except APIStatusError as e:
        if e.status_code == 403:
            raise ValueError(
                "This model's free quota has run out (AllocationQuota.FreeTierOnly). "
                "Check the Free Quota page in Model Studio — you'll need to either "
                "wait for reissue or switch to a different model's remaining quota."
            ) from e
        raise ValueError(f"OCR API call failed: {e}") from e

    raw = response.choices[0].message.content or "[]"

    try:
        items = _extract_json_array(raw)
    except (json.JSONDecodeError, AttributeError) as e:
        raise ValueError(f"OCR model did not return valid JSON. Raw output: {raw!r}") from e

    transactions = []
    for item in items:
        try:
            transactions.append(
                ParsedTransaction(
                    customer_name=item.get("customer_name", "Unknown"),
                    amount=float(item.get("amount", 0)),
                    type=item.get("type", "credit"),
                    item=item.get("item"),
                    confirmed=False,
                )
            )
        except (ValueError, TypeError):
            # One bad row shouldn't nuke the whole extraction — skip it, the review
            # UI will just show fewer rows than lines on the page for this photo.
            continue

    return transactions
