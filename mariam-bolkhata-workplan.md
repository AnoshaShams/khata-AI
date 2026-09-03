# Work Plan — Mariam
### BolKhata — Understanding + Acting Side

---

## Module Ownership (shared — same in both files)

| Module | Owner | Depends on | Unlocks |
|---|---|---|---|
| STT Integration | Anosha | Contracts only | Transaction Parser, Confirmation Loop |
| Confirmation Loop | Anosha | Transaction Parser contract (stub OK first) | Ledger writes |
| Spoken Daily Summary (TTS) | Anosha | Ledger Store | — |
| Voice-based Stock Nudges | Anosha | STT | Stock flag display |
| Transaction Parser (LLM) | **Mariam** | STT transcript contract | Confirmation Loop, Ledger Store |
| Ledger Data Store | **Mariam** | Transaction Parser | Dashboard, Reminders, Summary, Trust Score |
| Dashboard / Ledger View | **Mariam** | Ledger Store | — |
| Udhaar Reminders | **Mariam** | Ledger Store | — |
| Trust Score | **Mariam** | Ledger Store | — |

**Your modules: Transaction Parser (LLM), Ledger Data Store, Dashboard/Ledger View, Udhaar Reminders, Trust Score.**

You have more modules than Anosha, but they're lighter individually once the core parser is working — the parser is your one genuinely hard piece, matching Anosha's STT reliability challenge on her side.

---

## Before You Start

- **Transcript contract** (Anosha owns): `{text, language_mode, confidence, timestamp}` — you consume this
- **Parsed transaction contract** (you own): `{customer_name, amount, type, item, confirmed}` — Anosha's Confirmation Loop consumes this

You don't need Anosha's real STT to start — build against a stub (hardcoded transcript matching the contract) from Day 1.

---

## Day 1 — Setup

- [ ] Set up your LLM access (whatever backend — free-tier API or hackathon-provided credits)
- [ ] Design the transaction-parsing prompt: transcript in, structured JSON out (`customer_name, amount, type, item`)
- [ ] Test against a handful of hand-written example transcripts (both Urdu and English mode phrasing) — build against a stub transcript, don't wait for Anosha's real STT

## Day 2 — Parser Functional

- [ ] Harden the parser against realistic phrasing variety — different ways of saying the same transaction type, mixed Urdu/English words within a mode
- [ ] Handle edge cases: ambiguous amounts, missing customer names, unclear transaction type — decide what happens (e.g. flag as low-confidence, ask for clarification) rather than guessing silently
- [ ] **Deliverable Anosha needs from you:** a working parser function — transcript in, parsed transaction contract out. She can build the Confirmation Loop against a stub of this from Day 1, but needs the real thing by end of Day 2.

## Day 3 — Ledger Store + First Integration

- [ ] Build the Ledger Data Store: customers table, transactions table, running balance calculation
- [ ] Wire confirmed transactions (from Anosha's Confirmation Loop) into the store — your first real integration point
- [ ] Build a basic (unstyled) dashboard view showing a customer's ledger
- [ ] Test the full voice → parse → confirm → save loop end-to-end with Anosha

## Day 4 — Reminders + Toggle

- [ ] Build udhaar reminder detection: flag overdue balances, draft a polite Urdu WhatsApp message per customer
- [ ] Build the interface language toggle (Urdu script / Roman Urdu / English) — affects your dashboard's labels primarily
- [ ] Coordinate with Anosha on stock-flag display (her detection, your dashboard surface for it)

## Day 5 — Trust Score + Polish + Full Testing

- [ ] Build the trust score calculation (simple reliability metric per customer based on repayment pattern)
- [ ] Polish the dashboard/ledger UI — large text, low-literacy-friendly, phone-frame styled
- [ ] Run the curated phrase set (Requirements Doc Section 11) through the full pipeline repeatedly with Anosha, fix parser issues as they surface

## Day 6 — Demo Rehearsal

- [ ] Rehearse your part of the live demo (dashboard walkthrough, reminder draft, trust score) against the curated scenario
- [ ] Final bug-fix buffer

---

## What You're Waiting On From Anosha

- Transcript contract implementation (her Day 1-2) — blocks testing your parser against real voice input; use a stub until then
- Confirmation Loop (her Day 3) — blocks the full end-to-end demo flow

## What Anosha Is Waiting On From You

- Parsed transaction contract implementation (your Day 1-2) — blocks her real Confirmation Loop integration
- Ledger Store (your Day 3) — blocks her real save-and-summary integration

You're the critical path for the confirmation loop and daily summary being able to work against real data — keep the parser and ledger store deliverables on schedule.
