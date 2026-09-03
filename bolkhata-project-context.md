# BolKhata — Project Context
### Master Onboarding Document — Hackathon Build

Paste this at the start of a new session for full context.

---

## 1. The Project, In One Paragraph

BolKhata is a voice-first, Urdu-native AI bookkeeping assistant for shopkeepers who currently keep handwritten paper ledgers (khata). Instead of typing transactions into an app — the friction point that's kept them off every existing digital khata app (Khatabook, DigiKhata, Mobikhata, CreditBook) — they just speak naturally: *"Aslam ko paanch sau ka udhaar diya"* (Gave Aslam 500 rupees on credit). The app transcribes, extracts structured transaction data, reads it back for confirmation, and builds the ledger automatically — including tracking who owes what (udhaar/credit), nudging about overdue payments, flagging low stock from spoken mentions, and reading back a spoken daily summary on request.

## 2. Who's Building This

Hackathon team: **Anosha** (voice I/O side) and **Mariam** (understanding + acting side). 6-day build window, Aug 22–27, 2026. Idea and initial scoping developed by Anosha; this documentation adapts the same structure/style used on a separate two-person project (Agent Security Red-Team Toolkit) for consistency across projects.

## 3. Why This Idea

Every existing competitor still requires typing or photographing something — the apps digitized the notebook, not the act of writing in it. This removes that barrier entirely for a genuinely excluded user group (older, less tech-literate, or too busy shopkeepers), with a concrete downstream benefit (fewer missed udhaar payments, better inventory awareness) rather than being "another digital ledger." Fluent Urdu understanding is load-bearing, not decorative — this can't be built well without understanding real Urdu/English code-switching and informal money talk.

## 4. Why This Fits a Hackathon

- **Impact:** real financial-inclusion story, not just a cool demo
- **Creative AI use:** voice → structured data → confirmation loop → proactive agent behavior (reminders, nudges), not a chatbot wrapper
- **Practical viability:** buildable in 6 days
- **Demo strength:** the app talking back (spoken summary) and self-correcting live (confirmation loop) are strong, visual moments for judges — this project needs to look good live, not just work in principle

## 5. Current Status

- [x] Idea and differentiation locked
- [x] Feature list defined
- [x] Language handling decided (Section 8)
- [x] Tech stack decided
- [x] Work split decided
- [ ] Not yet started: actual build

## 6. System Architecture (Simplified)

```
  Shopkeeper (voice) ──► STT (Groq Whisper / Alibaba Cloud ASR)
                                │
                                ▼
                     Transaction Parser (LLM)
                    (extracts who / amount / type)
                                │
                                ▼
                      Confirmation Loop
              ("Aslam — 500 rupay udhaar — sahi hai?")
                                │
                     confirmed  ▼
                        Ledger Data Store
                       /        |         \
                      ▼         ▼          ▼
                Dashboard   Udhaar        Voice-based
                (ledger     Reminders     Stock Nudges
                 view)      (WhatsApp
                             draft)
                                │
                                ▼
                      Spoken Daily Summary (TTS)
```

## 7. Scope — v1 (Hackathon MVP) Features

- Voice-to-ledger entry (Urdu or English mode)
- Confirmation loop before saving
- Simple, large-text ledger view per customer
- Proactive udhaar reminders (drafted WhatsApp message)
- Voice-based stock nudges ("sugar khatam ho gaya" → low-stock flag)
- Spoken daily summary on request ("aaj ka hisab batao")
- Udhaar trust score (secondary, byproduct feature)
- Interface language toggle: Urdu script / Roman Urdu / English
- Voice input toggle: Urdu mode / English mode (tolerant of natural code-mixing within a mode, not full simultaneous code-switch detection)

## 8. Language Handling (Important — Read This)

- **Interface language** (menus/buttons/labels): toggle between Urdu script, Roman Urdu, English — pure localization.
- **Voice input**: shopkeeper picks Urdu mode or English mode before/while speaking — NOT automatic bilingual detection. Deliberately simpler and more reliable for a 6-day build than open code-switching detection.
- **Within a chosen mode**, natural mixing should still be tolerated (e.g. saying "credit" inside an Urdu sentence) — normal speech, handled by the parsing layer being forgiving, not by the STT engine detecting two languages at once.
- **Spoken AI responses**: match whichever voice mode is active.

## 9. Module Ownership

| Module | Owner | Depends on |
|---|---|---|
| STT Integration | Anosha | Contracts only |
| Confirmation Loop | Anosha | Transaction Parser contract |
| Spoken Daily Summary (TTS) | Anosha | Ledger Store |
| Voice-based Stock Nudges | Anosha | STT + simple parsing |
| Transaction Parser (LLM) | Mariam | STT transcript contract |
| Ledger Data Store | Mariam | Transaction Parser contract |
| Dashboard / Ledger View | Mariam | Ledger Data Store |
| Udhaar Reminders | Mariam | Ledger Data Store |
| Trust Score | Mariam | Ledger Data Store |

Anosha owns the voice I/O side (getting speech in and spoken responses out reliably); Mariam owns the understanding + acting side (turning transcripts into structured data and building the product around it). Both own one genuinely hard AI piece — Anosha: STT reliability; Mariam: LLM transaction parsing accuracy.

## 10. Core Contracts

```json
// Transcript (Anosha's STT → Mariam's Parser)
{"text": "...", "language_mode": "urdu|english", "confidence": 0.0, "timestamp": "..."}

// Parsed transaction (Mariam's Parser → Confirmation Loop / Ledger Store)
{"customer_name": "...", "amount": 0, "type": "sale|credit_given|payment_received|expense|stock_update", "item": "...", "confirmed": false}

// Ledger entry (Ledger Store → Dashboard / Reminders / Summary)
{"id": "...", "customer_name": "...", "type": "...", "amount": 0, "timestamp": "...", "balance_after": 0}
```

## 11. Tech Stack

- Backend: Python (FastAPI)
- Frontend: React web app, styled as a phone-frame UI for demo reliability (no device/emulator risk on stage)
- STT: Groq Whisper or Alibaba Cloud ASR (hackathon compute partner)
- TTS: whichever free/available service pairs with your STT choice — confirm early, don't leave to Day 5
- Storage: lightweight — SQLite or Firebase, nothing elaborate needed for a demo dataset

## 12. Companion Documents

1. **Requirements Document** — functional/non-functional requirements, architecture, data model, risks, day-by-day roadmap
2. **Anosha's Workplan** — her modules, day-by-day
3. **Mariam's Workplan** — her modules, day-by-day
4. **Development Flow** — git workflow, setup, session checklists
5. **Concepts & Theory** — STT/code-switching, LLM extraction, confirmation loop design, TTS, low-literacy UI, examples

## 13. Instructions for Claude Reading This

Treat scope as decided — don't re-litigate the idea. Help with implementation, debugging, and refining modules within this architecture. Given the 6-day window, bias toward shipping something that works end-to-end and demos well over building every stretch feature — if a request threatens the timeline, say so plainly rather than just building it.
