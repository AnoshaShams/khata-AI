# Concepts & Theory
### BolKhata — Background Knowledge

Read once before Day 1, reference per-module as needed.

---

## 1. The Voice-to-Ledger Loop (Why a Confirmation Step Matters)

```
Speech ──► STT (text, imperfect) ──► LLM parse (structured, imperfect) ──► Confirm ──► Save
```

Two imperfect steps stack: STT can mishear a name or number, and the parser can misclassify a transaction type. Without a confirmation step, both kinds of errors silently corrupt the ledger — exactly the kind of failure that would destroy trust with a real shopkeeper (and be embarrassing live in front of judges). The confirmation loop isn't a UX flourish — it's the mechanism that makes the whole pipeline trustworthy despite two unreliable steps in a row.

## 2. Language Mode vs. Automatic Language Detection

```
Simpler (what you're building):
  User picks "Urdu mode" or "English mode" ──► STT configured for that language only

Harder (what you're deliberately NOT building):
  STT tries to detect and juggle both languages within one utterance automatically
```

Automatic code-switch detection is a genuinely hard, actively-researched problem in speech AI — most STT models are trained cleanly on one language and stumble on switching mid-utterance. Pinning the mode ahead of time sidesteps this while still supporting real bilingual usage (just not within a single sentence's language *detection* — natural word-mixing within a mode, like saying "credit" in an Urdu sentence, is still fine and expected).

## 3. Structured Extraction from Speech (LLM Parsing)

The parser's job: take messy transcribed text and produce clean structured data.

```
Input transcript:  "Aslam ko paanch sau ka udhaar diya"
Output:            {
                      "customer_name": "Aslam",
                      "amount": 500,
                      "type": "credit_given",
                      "item": null
                    }
```

Use structured output mode (JSON mode / function calling, whichever your LLM provider supports) rather than asking for free text and regex-parsing it — far more reliable, and avoids a whole class of parsing bugs.

## 4. Handling Ambiguity and Low Confidence

Real speech won't always parse cleanly:

```
Input transcript:  "us ko kuch paisa diya tha"  (gave him/her some money)
Problem:            No clear amount, ambiguous "us ko" (who?)
```

Decide upfront what happens here — options: (a) the confirmation step explicitly asks for the missing piece ("Kitna paisa?" / "How much?"), or (b) flag as low-confidence and let the shopkeeper correct manually. Don't let the parser silently guess a number — a wrong silent guess is worse than an obvious question back.

## 5. Confirmation Loop Design

```
Parsed:    {customer_name: "Aslam", amount: 500, type: "credit_given"}
Read-back: "Aslam — 500 rupay udhaar — sahi hai?"
User:      "haan" (yes) ──► save
           "nahi" (no)  ──► discard, prompt to repeat
```

Keep the read-back short and in the same natural phrasing style the shopkeeper would use themselves — not a robotic recitation of field names. This is also one of your best live-demo moments: it visibly shows the system checking itself rather than blindly trusting a black box.

## 6. Text-to-Speech for Spoken Responses

Used in two places: confirmation read-back, and the daily summary. Keep generated speech short — a long spoken paragraph is a worse UX (and a worse demo beat) than a few natural sentences. For the summary specifically:

```
"Aaj kul teen sau rupay ki sale hui, do sau rupay ka udhaar diya gaya,
sab se zyada udhaar Aslam par hai."
(Today: 300 rupees in sales, 200 rupees given on credit,
Aslam owes the most.)
```

## 7. Low-Literacy UI Design Principles

- Large text, high contrast, minimal menu depth
- Icons/voice over dense text where possible
- The core action (speak a transaction) should be the most prominent, obvious thing on screen — not buried in a settings-heavy interface
- This matters for the judges too, incidentally — a clean, obviously-purposeful UI reads as more polished than a cluttered dashboard, regardless of audience

## 8. Financial Data Handling (Even for a Demo)

You're modeling real financial relationships (who owes whom money) — even with invented demo personas, treat the data model like it matters: don't hardcode secrets, don't over-retain voice recordings past what's needed for transcription, and use clearly fictional names/numbers for any live or recorded demo rather than anyone's real information.

## 9. Testing Under Time Pressure

No time for a formal evaluation harness. Practical approach:
- Build one curated list of ~15-20 realistic phrases across both language modes, including a couple of deliberately ambiguous ones
- Run this same list repeatedly as you iterate — this is both your testing method and your demo rehearsal script
- Fix the parser/STT prompt when a phrase in this set fails, rather than chasing every conceivable phrasing — the goal is a reliable demo, not exhaustive robustness

## 10. Contracts as Interfaces (Quick Recap)

Same principle as any two-person build: a contract is an agreed data shape between two pieces of code that don't need to know how the other works internally.

```
Anosha's STT  ──produces──►  {text, language_mode, confidence, timestamp}  ──consumed by──►  Mariam's Parser
```

This is what lets both of you build in parallel on Day 1 against stubs, rather than waiting on each other — critical when you only have 6 days total.
