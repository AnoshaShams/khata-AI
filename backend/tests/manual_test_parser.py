"""
Not a pytest suite — a quick manual check against a curated phrase set, per
docs/development-flow.md and docs/concepts.md Section 10 ("no time for a
formal eval harness, use a curated set instead").

Run with: python -m tests.manual_test_parser
(needs DASHSCOPE_API_KEY set in your .env)
"""
import datetime

from app.parser import parse_transcript
from app.schemas import ExtractedText

CURATED_PHRASES = [
    ("Aslam ko paanch sau ka udhaar diya", "urdu"),
    ("Bilal ne do sau wapas kiya", "urdu"),
    ("Sold rice worth 300 to Kareem on credit", "english"),
    ("Fatima paid back 1000 rupees", "english"),
    ("Ahmed ko atta diya udhaar pe, teen sau rupay", "urdu"),
    ("Customer Zeeshan gave 500 payment", "english"),
    ("Sara ko chai patti udhaar di, do sau", "urdu"),
    ("Kareem returned 150", "english"),
    ("Yasir ne pura paisa jama karwa diya, paanch sau", "urdu"),
    ("Gave 2000 credit to Hassan for flour", "english"),
]

if __name__ == "__main__":
    passed, failed = 0, 0
    for text, mode in CURATED_PHRASES:
        extracted = ExtractedText(
            text=text,
            language_mode=mode,
            confidence=0.9,
            timestamp=datetime.datetime.utcnow().isoformat(),
        )
        result = parse_transcript(extracted)
        status = "OK  " if result else "FAIL"
        if result:
            passed += 1
            print(f"[{status}] '{text}' -> {result.model_dump()}")
        else:
            failed += 1
            print(f"[{status}] '{text}' -> could not parse")
    print(f"\n{passed}/{len(CURATED_PHRASES)} parsed successfully.")
