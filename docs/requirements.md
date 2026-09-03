# BolKhata — Requirements Document
### Hackathon Build (6 Days)

**Team:** Anosha & Mariam
**Note on scope:** deliberately compressed relative to a longer-timeline project — sections that matter less under time pressure (elaborate monitoring, historical analytics) are trimmed or omitted; sections that matter more under demo pressure (reliability, risks, day-by-day roadmap) are expanded.

---

## 1. Executive Summary

BolKhata is a voice-first Urdu/English bookkeeping assistant that lets shopkeepers speak transactions naturally instead of typing. It transcribes speech, extracts structured transaction data via LLM, confirms it back to the user, maintains a per-customer ledger, and proactively supports the shopkeeper with udhaar reminders, stock nudges, and spoken summaries.

## 2. Problem Statement

Digital khata apps exist (Khatabook, DigiKhata, Mobikhata, CreditBook) but all still require typing or photographing — a barrier for shopkeepers who are older, less tech-literate, or too busy serving customers. This excludes a large population from digital bookkeeping despite years of these apps being available.

## 3. Goals

- Working end-to-end voice → structured ledger pipeline
- A confirmation loop that catches misheard input before it corrupts the ledger
- A genuinely demoable, good-looking UI — this is being shown live to judges, not just described
- At least one "wow" live moment: the app talking back (spoken summary) or self-correcting (confirmation loop)

## 4. Success Metrics

| Metric | Target |
|---|---|
| End-to-end voice-to-ledger flow works live | Must-have, no exceptions |
| Transaction parsing accuracy on rehearsed phrase set | High enough that confirmation loop rarely needs correction in the demo set |
| Confirmation loop catches a deliberately-introduced misheard example | Yes, as a demo beat |
| Spoken daily summary works on request | Yes |
| UI is presentable on a projector/laptop, not placeholder styling | Yes |

## 5. Functional Requirements

- FR1: Accept voice input in Urdu mode or English mode (user-selected)
- FR2: Transcribe speech to text
- FR3: Parse transcript into structured transaction data (customer, amount, type)
- FR4: Read back the parsed transaction for confirmation before saving
- FR5: On confirmation, write to the ledger store; on rejection, allow correction/retry
- FR6: Display a per-customer ledger view (large text, low-literacy-friendly)
- FR7: Detect overdue udhaar balances and draft a polite Urdu WhatsApp reminder message
- FR8: Detect spoken low-stock mentions and log a stock flag/reminder
- FR9: On request, generate and speak back a daily summary (total sales, credit given, top debtor)
- FR10: Maintain a simple per-customer trust score based on repayment consistency
- FR11: Support interface language toggle (Urdu script / Roman Urdu / English)

## 6. Non-Functional Requirements

- NFR1: Voice-to-confirmation round trip should feel fast enough for a live demo (a few seconds, not tens of seconds)
- NFR2: UI must render reliably on stage — favor a web app over anything requiring device/emulator setup
- NFR3: Zero/low budget — use free-tier or hackathon-provided (Alibaba Cloud) services only
- NFR4: Graceful handling of a misheard/failed transcription — don't crash, prompt for retry

## 7. System Architecture

See Project Context doc, Section 6, for the diagram — same architecture, referenced here to avoid duplication.

## 8. Data Model (Simplified)

- **customers** — id, name, current_balance, trust_score
- **transactions** — id, customer_id, type, amount, item, timestamp
- **stock_flags** — id, item, flagged_at, resolved (bool)
- **reminders_drafted** — id, customer_id, message, drafted_at

## 9. API Reference (Core Endpoints)

| Endpoint | Method | Purpose |
|---|---|---|
| `/transcribe` | POST | Audio in, transcript contract out |
| `/parse` | POST | Transcript in, parsed transaction out |
| `/confirm` | POST | Confirmed transaction → writes to ledger |
| `/ledger/{customer_id}` | GET | Customer ledger view |
| `/summary/today` | GET | Today's spoken/text summary |
| `/reminders` | GET | List of overdue customers + drafted messages |
| `/stock-flags` | GET | Current low-stock flags |

## 10. AI Components

- **STT:** Groq Whisper or Alibaba Cloud ASR, language-mode-pinned (not auto-detect)
- **Transaction Parser:** LLM call with structured output (JSON mode / function calling) — transcript in, `{customer_name, amount, type, item}` out
- **Confirmation phrasing:** LLM or template-based read-back in the active voice mode's language
- **TTS:** for confirmation read-back and daily summary
- **Reminder drafting:** LLM call — overdue customer + amount in, polite Urdu WhatsApp message out

## 11. Evaluation Approach (Realistic for 6 Days)

No time for formal precision/recall validation. Instead:
- Build a curated set of ~15-20 realistic Urdu/English phrases (including a few deliberately ambiguous ones) and test the parser against them repeatedly during Days 3-5
- Rehearse the live demo against this same curated set — reduces risk of an embarrassing mishear in front of judges while still proving the capability genuinely works
- Track informally which phrases fail and fix the parser prompt iteratively, rather than building a formal eval harness

## 12. Security & Privacy Notes

- Transaction and customer data involves names and financial amounts — even for a demo, don't use real people's real financial data; use invented demo personas
- Voice recordings: don't retain them longer than needed for transcription during the demo/build
- No need for elaborate auth/security given hackathon scope, but don't hardcode secrets/API keys into committed code

## 13. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Live mic/STT fails in front of judges | Rehearse with curated phrases; have a backup pre-recorded audio fallback path |
| Code-mixed speech confuses the parser | Let the LLM parsing layer (not the STT layer) absorb most of this tolerance; test explicitly with mixed phrases |
| Judges' wifi is bad, cloud STT/LLM calls fail | Test an offline-ish fallback if feasible, or have a recorded demo video as backup |
| UI looks unfinished under time pressure | Prioritize UI polish explicitly on Day 5 — don't treat it as a "final hour" afterthought |
| Scope creep (trust score, stock nudges, etc. eating core-feature time) | Core voice→ledger→confirmation loop must work before any secondary feature gets time |

## 14. Day-by-Day Roadmap

| Day | Focus |
|---|---|
| Day 1 | Setup, contracts locked, environments running, first STT test, first LLM parsing test |
| Day 2 | STT integration functional; transaction parser functional (against stubs of each other) |
| Day 3 | Confirmation loop + ledger store + basic dashboard; first real integration |
| Day 4 | Reminders, stock nudges, daily summary TTS; language toggles; second integration checkpoint |
| Day 5 | UI polish (phone-frame styling), trust score, full end-to-end testing with curated phrase set |
| Day 6 | Demo rehearsal, bug-fix buffer, pitch prep |

## 15. Milestones

- **M1 (end Day 1):** contracts locked, both environments running
- **M2 (end Day 3):** one full voice→confirm→ledger cycle works end-to-end, even if rough
- **M3 (end Day 4):** all core features present, even if not polished
- **M4 (end Day 5):** demo-ready build, styled UI, tested against curated phrase set
- **M5 (end Day 6):** rehearsed, reliable live demo
