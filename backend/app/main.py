from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db import init_db, get_session, save_transaction
from app.ocr import extract_transactions_from_photo
from app.parser import parse_transcript
from app.schemas import ExtractedText, ParsedTransaction, ConfirmedTransactionIn
from app.dashboard import get_dashboard
from app.reminders import get_pending_reminders
from app.trust_score import compute_trust_score
from app.stt import transcribe_audio
from app.tts import synthesize_speech
from fastapi.responses import Response

app = FastAPI(title="KhataAI API")

# Dev-friendly CORS — tighten origins before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


# --- OCR path: photo -> Parsed Transaction(s), directly (see ocr.py + CONTRACTS.md) ---
@app.post("/ledger/upload", response_model=list[ParsedTransaction])
async def upload_ledger_photo(file: UploadFile = File(...)):
    image_bytes = await file.read()
    try:
        transactions = extract_transactions_from_photo(image_bytes, mime_type=file.content_type or "image/jpeg")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Couldn't read this photo clearly. {e}")
    if not transactions:
        raise HTTPException(status_code=422, detail="No transactions found in this photo. Try a clearer photo.")
    return transactions


# --- Voice path: transcript -> Parsed Transaction (see parser.py + CONTRACTS.md) ---
@app.post("/ledger/parse-voice", response_model=ParsedTransaction)
def parse_voice(extracted: ExtractedText):
    try:
        result = parse_transcript(extracted)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if result is None:
        raise HTTPException(status_code=422, detail="Couldn't parse that transcript into a transaction. Try again.")
    return result


# --- Confirmation: shopkeeper accepted/edited a transaction -> write to ledger ---
@app.post("/ledger/confirm")
def confirm_transaction(payload: ConfirmedTransactionIn, db: Session = Depends(get_session)):
    txn = save_transaction(
        db,
        business_id=payload.business_id,
        customer_name=payload.customer_name,
        type_=payload.type,
        amount=payload.amount,
        item=payload.item,
        source=payload.source,
    )
    return {"status": "saved", "transaction_id": txn.id, "balance_after": txn.balance_after}


# --- Dashboard ---
@app.get("/ledger/{business_id}")
def dashboard(business_id: str, db: Session = Depends(get_session)):
    return get_dashboard(db, business_id)


# --- Trust score ---
@app.get("/score/{business_id}")
def score(business_id: str, db: Session = Depends(get_session)):
    return compute_trust_score(db, business_id)


# --- Reminders ---
@app.get("/reminders/{business_id}")
def reminders(business_id: str, db: Session = Depends(get_session)):
    return get_pending_reminders(db, business_id)


# --- Voice path, step 1: audio -> Extracted-Text contract (see stt.py + CONTRACTS.md) ---
@app.post("/voice/transcribe", response_model=ExtractedText)
async def transcribe_voice(file: UploadFile = File(...), language_mode: str = Form("urdu")):
    audio_bytes = await file.read()
    try:
        extracted = transcribe_audio(audio_bytes, filename=file.filename or "recording.wav",
                                      language_mode=language_mode)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Couldn't transcribe that audio. {e}")
    return extracted

# --- Voice path, combined: audio -> Parsed Transaction, in one call ---
# This is what the Confirmation Loop's frontend should call — chains
# transcribe_audio() and parse_transcript() so the frontend only needs one
# request to go from "shopkeeper spoke" to "here's the transaction to confirm."
@app.post("/voice/process", response_model=ParsedTransaction)
async def process_voice(file: UploadFile = File(...), language_mode: str = Form("urdu")):
    audio_bytes = await file.read()
    try:
        extracted = transcribe_audio(audio_bytes, filename=file.filename or "recording.wav",
                                      language_mode=language_mode)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Couldn't transcribe that audio. {e}")

    try:
        result = parse_transcript(extracted)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Transcribed OK, but couldn't parse a transaction from it. {e}")
    if result is None:
        raise HTTPException(status_code=422, detail="Transcribed OK, but no transaction could be parsed. Try again.")
    return result

# --- TTS: text -> spoken audio, used for the Spoken Daily Summary (see tts.py) ---
@app.post("/voice/speak")
def speak_text(text: str = Form(...), voice: str | None = Form(None)):
    try:
        audio_bytes = synthesize_speech(text, voice=voice)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    # Adjust media_type if the model returns a different audio format (check
    # the Model Studio page for cosyvoice-v3-plus's actual output format).
    return Response(content=audio_bytes, media_type="audio/mpeg")