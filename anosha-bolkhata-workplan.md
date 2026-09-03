# Work Plan — Anosha
### BolKhata — Voice I/O Side

---

## Module Ownership (shared — same in both files)

| Module | Owner | Depends on | Unlocks |
|---|---|---|---|
| STT Integration | **Anosha** | Contracts only | Transaction Parser, Confirmation Loop |
| Confirmation Loop | **Anosha** | Transaction Parser contract (stub OK first) | Ledger writes |
| Spoken Daily Summary (TTS) | **Anosha** | Ledger Store | — |
| Voice-based Stock Nudges | **Anosha** | STT | Stock flag display |
| Transaction Parser (LLM) | Mariam | STT transcript contract | Confirmation Loop, Ledger Store |
| Ledger Data Store | Mariam | Transaction Parser | Dashboard, Reminders, Summary, Trust Score |
| Dashboard / Ledger View | Mariam | Ledger Store | — |
| Udhaar Reminders | Mariam | Ledger Store | — |
| Trust Score | Mariam | Ledger Store | — |

**Your modules: STT Integration, Confirmation Loop, Spoken Daily Summary (TTS), Voice-based Stock Nudges.**

---

## Before You Start

Lock with Mariam before Day 1 build starts:
- **Transcript contract** (you own): `{text, language_mode, confidence, timestamp}` — Mariam's parser consumes this
- **Parsed transaction contract** (Mariam owns): `{customer_name, amount, type, item, confirmed}` — you consume this in the Confirmation Loop

---

## Day 1 — Setup

- [ ] Set up Groq Whisper or Alibaba Cloud ASR access, test a basic transcription call
- [ ] Confirm your TTS option alongside your STT choice — don't leave this until later
- [ ] Produce transcript output in the exact contract shape
- [ ] Test with a handful of both Urdu-mode and English-mode sample phrases

## Day 2 — STT Functional

- [ ] Build the language-mode toggle (Urdu/English) at the input level — determines which STT config gets used
- [ ] Test transcription accuracy on realistic mixed phrases within a single mode (e.g. Urdu mode with "credit" inside a sentence)
- [ ] **Deliverable Mariam needs from you:** a working transcription function — audio in, transcript contract out. She can build against a stub of this from Day 1, but needs the real thing by end of Day 2 to integrate for real.

## Day 3 — Confirmation Loop + First Integration

- [ ] Build the confirmation read-back: takes a parsed transaction (Mariam's output), phrases it naturally in the active voice mode, gets a yes/no/correction response
- [ ] Wire confirmed transactions through to the Ledger Store (Mariam's module) — your first real integration point
- [ ] Test the full voice → parse → confirm → save loop end-to-end with at least 3 phrases

## Day 4 — Stock Nudges + Summary

- [ ] Build stock-nudge detection: recognize spoken "X khatam ho gaya" style phrases, log a stock flag
- [ ] Build spoken daily summary: pull from Ledger Store, generate a short summary, speak it back via TTS
- [ ] Test both against realistic phrases, in both language modes

## Day 5 — Polish + Full Testing

- [ ] Polish the voice-interaction UI (mic button, listening state, confirmation display) — a core part of what judges will actually watch
- [ ] Run your curated phrase set (Requirements Doc Section 11) through the full pipeline repeatedly, fix parser/STT issues as they surface
- [ ] Coordinate with Mariam on any remaining integration rough edges

## Day 6 — Demo Rehearsal

- [ ] Rehearse your part of the live demo against the curated phrase set, not improvised speech
- [ ] Have a backup (pre-recorded audio clip) ready in case live mic/STT fails on stage
- [ ] Final bug-fix buffer

---

## What You're Waiting On From Mariam

- Parsed transaction contract implementation (her Day 2) — blocks your real Confirmation Loop integration; use a stub until then
- Ledger Store (her Day 3) — blocks your real save-and-summary integration

## What Mariam Is Waiting On From You

- Transcript contract implementation (your Day 1-2) — blocks her real parser testing against real audio
- Confirmation Loop (your Day 3) — blocks the full end-to-end demo flow

You're the critical path for her being able to test against real voice input rather than typed placeholder text — keep the STT deliverable on schedule.
