# Development Flow
### BolKhata — Git, Setup & Session Workflow (6-Day Hackathon)

Compressed relative to a longer-timeline project — daily integration checkpoints instead of multi-week phases, since there's no time to recover from late-discovered integration issues.

---

## 1. Repo Structure

```
bolkhata/
├── backend/
│   ├── stt/                 # Anosha
│   ├── confirmation/        # Anosha
│   ├── tts_summary/         # Anosha
│   ├── stock_nudges/        # Anosha
│   ├── parser/               # Mariam
│   ├── ledger_store/         # Mariam
│   ├── reminders/            # Mariam
│   └── trust_score/          # Mariam
├── frontend/                 # shared — voice UI (Anosha), ledger/dashboard UI (Mariam)
├── docs/
│   ├── contracts.md
│   ├── requirements.md
│   └── workplans/
└── README.md
```

## 2. Branching Strategy (Simplified for 6 Days)

```
main                — always working, always demoable
├── anosha/stt
├── anosha/confirmation
├── anosha/summary-tts
├── anosha/stock-nudges
├── mariam/parser
├── mariam/ledger-store
├── mariam/reminders
└── mariam/trust-score
```

No multi-week phase-integration branches needed — merge directly to `main` once your piece works against the current contract, but **never merge something that breaks what's already working**. With only 6 days, `main` staying demoable at all times matters more than usual.

## 3. Commits & Contract Changes

- Short present-tense commit messages
- Prefix `[CONTRACT]` if you change a shared shape in `docs/contracts.md` — announce to the other person before pushing, not after. With this little time, a silent contract break costs you a day you don't have.

## 4. Setup & Requirements

| Tool | Purpose |
|---|---|
| Python 3.11+ | Backend (FastAPI) |
| Node.js 20+ | Frontend (React) |
| Groq / Alibaba Cloud account | STT + LLM calls |
| Git + GitHub | Version control |
| `.env` (never committed) | API keys — each of you use your own or shared hackathon-provided credentials |

```bash
git clone <repo-url> && cd bolkhata
cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd ../frontend && npm install
cp .env.example .env   # fill in your keys
```

## 5. Session Start Checklist

1. `git checkout main && git pull`
2. Skim `docs/contracts.md` for `[CONTRACT]` changes since last session
3. `git checkout yourname/your-module && git merge main`
4. If something you're waiting on has landed, swap your stub for the real thing now

## 6. Session End Checklist

1. Commit and push your branch
2. If working, merge to `main` — don't let work sit unmerged overnight, 6 days is too short for a backlog of unmerged branches
3. Update your workplan checklist
4. Flag any blocker to the other person before signing off, especially anything that affects tomorrow's integration point

## 7. Daily Integration Points

| Day | Integration checkpoint |
|---|---|
| Day 2 | Anosha's transcript output ↔ Mariam's parser input — confirm the real (non-stub) connection works |
| Day 3 | Full voice → parse → confirm → save loop, end-to-end, for the first time |
| Day 4 | Reminders, stock nudges, summary, language toggle all merged and working together |
| Day 5 | Full pipeline tested against the curated phrase set, UI polished |
| Day 6 | Final rehearsal build — no new features, only fixes |

## 8. Flow Diagram

```
 ANOSHA                                              MARIAM
   │                                                    │
   ▼                                                    ▼
anosha/stt (real STT, Day 1-2)              mariam/parser (stub transcript, Day 1-2)
   │                                                    │
   └──────────────► Day 2 integration ◄──────────────────┘
              (real transcript → real parser)
                            │
   ┌────────────────────────┴────────────────────────┐
   ▼                                                    ▼
anosha/confirmation                          mariam/ledger-store
   │                                                    │
   └──────────────► Day 3 integration ◄──────────────────┘
        (full voice → parse → confirm → save loop)
                            │
   ┌────────────────────────┴────────────────────────┐
   ▼                                                    ▼
anosha/stock-nudges, summary-tts             mariam/reminders, lang-toggle
   │                                                    │
   └──────────────► Day 4 integration ◄──────────────────┘
                            │
                     Day 5: UI polish +
                  full curated-phrase testing
                            │
                     Day 6: rehearsal only
                            │
                            ▼
                      main (demo build)
```
