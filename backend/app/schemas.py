"""
Schemas mirror docs/CONTRACTS.md exactly. If you change a shape here,
you MUST update CONTRACTS.md in the same commit and prefix the commit
message with [CONTRACT], then tell Anosha before she pulls.
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field


# --- Contract 1: Extracted-Text Contract (voice path ONLY, per CONTRACT update) ---
class ExtractedText(BaseModel):
    text: str
    source: Literal["voice"] = "voice"
    language_mode: Literal["urdu", "english"]
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: str  # ISO-8601


# --- Contract 2: Parsed Transaction Contract ---
# Produced directly by Qwen2-VL for the OCR path, or by the text-parser for the voice path.
# Consumed by Anosha's Confirmation Loop / TTS summary.
class ParsedTransaction(BaseModel):
    customer_name: str
    amount: float
    type: Literal["credit", "payment"]
    item: Optional[str] = None
    confirmed: bool = False


# --- Internal (backend-only, not in CONTRACTS.md): what the confirmation loop
# sends back once the shopkeeper accepts/edits a transaction, plus which
# business/customer it belongs to. This is Mariam-side only, Anosha doesn't
# need to know this shape beyond calling POST /ledger/confirm.
class ConfirmedTransactionIn(BaseModel):
    business_id: str
    customer_name: str
    amount: float
    type: Literal["credit", "payment"]
    item: Optional[str] = None
    source: Literal["photo", "voice", "manual"] = "manual"
