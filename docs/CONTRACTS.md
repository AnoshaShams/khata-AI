# Locked Contracts — KhataAI

Do not change these without a `[CONTRACT]` tag in your commit AND telling the other
person first. Both input paths (OCR and voice) must produce the same shape below.

---

## 1. Extracted-Text Contract
**Owner: Mariam (OCR path) + Anosha (voice path) — both produce this shape**
**Consumed by: Mariam's Parser**

```json
{
  "text": "string",
  "source": "ocr" | "voice",
  "language_mode": "urdu" | "english",
  "confidence": 0.0,
  "timestamp": "ISO-8601 string"
}
```

- `text`: raw extracted text — from OCR on a photo, or from STT on spoken audio.
- `source`: which input path produced this. Parser can use this to tune extraction
  (e.g. handwriting OCR text tends to be noisier/shorter than transcribed speech).
- Previously this was called the "Transcript contract" and only had voice fields —
  it is now source-agnostic. `[CONTRACT]` change from original BolKhata docs.

## 2. Parsed Transaction Contract
**Owner: Mariam (Parser) — unchanged from original**
**Consumed by: Anosha (Confirmation Loop, TTS summary)**

```json
{
  "customer_name": "string",
  "amount": 0,
  "type": "credit" | "payment",
  "item": "string",
  "confirmed": false
}
```

No changes to this contract — it stays identical regardless of whether the transaction
originated from a photo or from voice. This is intentional: it's what lets both input
paths share one parser and one confirmation loop.

---

## Change Log
- `[CONTRACT]` Transcript contract renamed to Extracted-Text contract, added `source`
  field, to support merged OCR-core + voice-secondary scope (hard requirement per
  hackathon submission — see AGENTS.md scope-change note).