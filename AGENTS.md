# AGENTS.md — Development Protocol
### KhataAI — Hackathon Implementation Phase (3 Days Left)

Read `docs/project-context.md` first if new session. Governs *how* to work, not *what* the project is.

> **[CONTRACT] SCOPE CHANGE — read this before touching old docs.**
> The original `.md` docs in this repo (dated Aug 22–27) describe a **voice-only** project
> called BolKhata. That is NOT what was submitted to the hackathon. The actual submission
> is **KhataAI**: photo of a handwritten ledger → OCR → LLM extraction → structured
> transaction → dashboard, with voice as a **secondary** input mode (not primary).
> Treat the old docs as reference for the parser/confirmation/ledger logic only —
> ignore anything in them that assumes voice is the sole or primary input.

---

## Autonomy Rules

- Don't ask which module to build next — follow the day-by-day plan below.
- Don't ask "A or B" for anything already implied by `docs/requirements.md` or this file's
  contracts section. Check those first.
- Only 3 days left. If blocked on the other person's undelivered contract, build against
  the stub and keep moving — never stall.

## Module Ownership (updated for merged scope)

- **Mariam**: OCR integration (photo → raw text), Transaction Parser (LLM), Ledger Data
  Store, Dashboard/Ledger View, Udhaar Reminders, Trust Score (simplified/heuristic — not
  "bank-ready" in this timeframe)
- **Anosha**: Voice input as secondary mode (STT), Confirmation Loop (shared by both input
  paths), Spoken Daily Summary (TTS), Voice-based Stock Nudges

## The Key Design Decision

Both input paths (photo-OCR and voice-STT) feed the **same parser and the same
confirmation loop**. The only difference is what produces the raw `text` field. Do not
build two separate parsing or confirmation pipelines — that is not finishable in 3 days
and is not necessary.

```
Photo → OCR ──┐
              ├─→ {text, source, language_mode, confidence, timestamp} → Parser → Confirm → Save
Voice → STT ──┘
```

## Session Start

```bash
git checkout main && git pull
```
- Check this file's contracts section for `[CONTRACT]` changes since last session
- Swap any stub for a now-real dependency immediately

## After Every Change

1. If testable, test it before moving on — don't stack unverified work.
2. If not testable (e.g. prompt tuning), do a manual check against the curated phrase/photo
   set instead of skipping verification.
3. Commit; prefix `[CONTRACT]` if a shared shape changed, and flag it plainly at the end of
   your response.

## Merging

- Merge to `main` once your piece works against the current contract.
- Never merge something that breaks what already worked — `main` must stay demoable every
  single day, not just at the end.

## Testing Discipline

- Unit-test parsing/contract logic where sensible.
- At every daily integration checkpoint: confirm the full relevant chain still works
  end-to-end, not just your own module in isolation.
- For OCR/STT/LLM output: judge by shape-correctness (contract compliance) strictly, and
  behavior against the curated test set — not a single lucky run.

## Scope Discipline (3-day reality)

- Priority order if time runs short: (1) OCR → parse → confirm → save core loop,
  (2) voice as secondary input mode, (3) udhaar reminders, (4) simplified trust score,
  (5) stock nudges. Cut from the bottom, never the top.
- "Bank-ready credit score" is out of scope for 3 days — build a simple rule-based score
  and say so plainly to judges (v1 heuristic, roadmap item for real scoring).
- WhatsApp reminders: if there isn't time to wire real WhatsApp delivery, build the
  reminder logic and stub the send step — demo it as "ready to connect," don't fake it as
  working.
- Don't add anything not already agreed without flagging it first — no time to absorb
  undiscussed scope changes.

## Output Style

- Code and commands over prose.
- After a task: what changed, test result, what's next, any blocker — a few bullets, not a
  re-explanation of the whole project.

## When to Actually Ask

- A decision that changes scope or affects the other person's module and isn't already
  resolved by a contract.
- Something in the docs is genuinely ambiguous.
- Everything else: decide, build, test, move on.