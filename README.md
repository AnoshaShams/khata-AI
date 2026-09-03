# KhataAI

AI-powered digital ledger for shopkeepers who currently track sales, credit (udhaar),
and stock by hand.

## What it does

- **Photo → structured ledger**: Shopkeeper photographs a handwritten ledger page. OCR
  extracts the text, an LLM parses it into structured transactions (customer, amount,
  type, item), and it's saved to a per-customer digital ledger.
- **Voice input (secondary mode)**: Shopkeeper can also speak a transaction naturally
  ("Aslam ko paanch sau ka udhaar diya") — transcribed, parsed the same way, read back
  for confirmation, saved.
- **Udhaar (credit) reminders**: Nudges shopkeepers about outstanding customer credit.
- **Trust score**: Simple heuristic score based on udhaar payment history.
- **Voice-based stock nudges**: Flags low-stock items mentioned in spoken transactions.

## Why

Most shopkeepers in Pakistan track sales and credit in a paper *khata* (ledger) — no
digital record, no reminders, no way to reconstruct data if the notebook is lost or
damaged. KhataAI digitizes this with minimal behavior change: photograph or speak, don't
manually type or learn a new system.

## Tech stack

- OCR: Azure AI Vision (Read API)
- STT: OpenAI Whisper API
- Parsing: LLM-based structured extraction
- Frontend: React
- Backend: Python (FastAPI)

## Project structure

```
khataAI/
├── src/            # application code
├── docs/           # planning docs, contracts, dev protocol
└── README.md       # you are here
```

See `docs/CONTRACTS.md` for the data contracts between modules, and `docs/AGENTS.md`
for the development workflow.

## Team

- **Mariam** — OCR integration, Transaction Parser, Ledger Data Store, Dashboard,
  Udhaar Reminders, Trust Score
- **Anosha** — Voice/STT input, Confirmation Loop, Spoken Daily Summary (TTS),
  Voice-based Stock Nudges

## Status

Built for the Alibaba Cloud AI Hackathon Pakistan 2026. 3-day build sprint (in progress).

## Running locally

1. Clone the repo and copy `.env.example` to `.env`, filling in your own API keys
   (OpenAI, Azure Vision) — never commit `.env`.
2. Backend (Python/FastAPI):
   ```
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
3. Frontend (React):
   ```
   cd frontend
   npm install
   npm start
   ```

(Steps will be updated as the actual folder structure and dependencies are finalized.)