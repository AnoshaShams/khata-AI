# CLAUDE.md — Development Protocol
### BolKhata — Hackathon Implementation Phase

Read `docs/project-context.md` first if new session. Governs *how* to work, not *what* the project is. Compressed for 6-day speed — bias toward shipping, but never skip testing.

---

## Autonomy Rules

- Don't ask which module to build next — follow the day-by-day plan in `docs/workplans/`. Anosha's session → her modules in day order; Mariam's session → hers.
- Don't ask "A or B" for anything already implied by `docs/requirements.md` or `docs/contracts.md`. Check those first.
- Given only 6 days: if blocked on the other person's undelivered contract, build against the stub and keep moving — never stall.

## Session Start

```bash
git checkout main && git pull
```
- Check `docs/contracts.md` for `[CONTRACT]` changes since last session
- Swap any stub for a now-real dependency immediately

## After Every Change

1. If testable, test it before moving on — don't stack unverified work, there's no time to debug a pile of untested changes on Day 5
2. If not testable (e.g. prompt tuning), do a manual check against the curated phrase set instead of skipping verification
3. Commit; prefix `[CONTRACT]` if a shared shape changed, and flag it plainly at the end of your response

## Merging

- Merge to `main` once your piece works against the current contract
- Never merge something that breaks what already worked — `main` must stay demoable every single day, not just at the end

## Testing Discipline

- Unit-test parsing/contract logic where sensible
- At every daily integration checkpoint (see Development Flow doc): confirm the full relevant chain still works end-to-end, not just your own module in isolation
- For STT/LLM output: judge by shape-correctness (contract compliance) strictly, and behavior against the curated phrase set — not a single lucky test run

## Scope Discipline

- Core loop (voice → parse → confirm → save) takes priority over every secondary feature (reminders, stock nudges, trust score) — if time is short, secondary features get cut first, not the core loop
- Don't add anything not in `docs/requirements.md` Section 5 without flagging it — no time to absorb undiscussed scope changes

## Output Style

- Code and commands over prose
- After a task: what changed, test result, what's next, any blocker — a few bullets, not a re-explanation of the whole project
- Skip re-explaining concepts already covered in `docs/concepts.md`

## When to Actually Ask

- A decision that changes scope or affects the other person's module and isn't already resolved by a contract
- Something in the docs is genuinely ambiguous
- Everything else: decide, build, test, move on — time is the scarce resource here, not permission.
