# Locked Contracts — KhataAI

Do not change these without a `[CONTRACT]` tag in your commit AND telling the other
person first. Both input paths (OCR and voice) must produce the same shape below.

---

## 1. Extracted-Text Contract
**Owner: Anosha (voice path only — see note below)**
**Consumed by: Mariam's Parser**

```json
{
  "text": "string",
  "source": "voice",
  "language_mode": "urdu" | "english",
  "confidence": 0.0,
  "timestamp": "ISO-8601 string"
}
```

> **[CONTRACT] Update**: This contract now applies to the **voice path only**. The OCR
> path no longer uses it — Qwen2-VL does extraction + structuring in a single call and
> outputs the Parsed Transaction Contract directly (see below). Only Whisper transcripts
> (which are unstructured text) still need to pass through a separate parse step.

- `text`: raw transcribed speech from Whisper.
- Previously this also covered OCR output as raw text — no longer true. OCR now skips
  straight to Contract 2.

## 2. Parsed Transaction Contract
**Owner: Mariam — produced directly by Qwen2-VL for OCR path, or by Parser for voice path**
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

Both input paths converge here regardless of how they got here:
- **OCR path**: Photo → Qwen2-VL (single call, via backend proxy — key stays server-side,
  never exposed to the browser) → this shape, directly.
- **Voice path**: Audio → Whisper → Extracted-Text Contract (above) → Parser → this shape.

This is what makes the Confirmation Loop and TTS summary source-agnostic — they only ever
see this one shape, never caring which input path produced it.

---

## Change Log
- `[CONTRACT]` Extracted-Text contract narrowed to voice-only. OCR path now produces
  the Parsed Transaction contract directly via Qwen2-VL, since it does extraction +
  structuring in one call. OCR key must be called from the backend, never the browser
  directly (VITE_-prefixed keys get bundled into client JS and exposed publicly).
- `[CONTRACT]` Transcript contract renamed to Extracted-Text contract, added `source`
  field, to support merged OCR-core + voice-secondary scope (hard requirement per
  hackathon submission — see AGENTS.md scope-change note).