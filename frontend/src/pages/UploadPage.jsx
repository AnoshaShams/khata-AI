import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadLedgerPhoto, processVoice } from "../lib/api";

export default function UploadPage() {
  const [mode, setMode] = useState("photo"); // "photo" | "voice"

  return (
    <div className="content">
      <div className="mode-toggle">
        <button
          className={`mode-toggle__btn ${mode === "photo" ? "is-active" : ""}`}
          onClick={() => setMode("photo")}
        >
          Photo
        </button>
        <button
          className={`mode-toggle__btn ${mode === "voice" ? "is-active" : ""}`}
          onClick={() => setMode("voice")}
        >
          Voice
        </button>
      </div>

      {mode === "photo" ? <PhotoUpload /> : <VoiceRecord />}
    </div>
  );
}

// --- Photo mode: unchanged from the original OCR flow ---
function PhotoUpload() {
  const inputRef = useRef(null);
  const [status, setStatus] = useState("idle"); // idle | uploading | error
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();

  async function handleFile(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    setStatus("uploading");
    setErrorMessage("");
    try {
      const transactions = await uploadLedgerPhoto(file);
      navigate("/review", { state: { transactions, source: "photo" } });
    } catch (err) {
      setStatus("error");
      setErrorMessage(
        err.status === 422
          ? err.message
          : "Couldn't reach the server. Check your connection and try again."
      );
    }
  }

  return (
    <div className="upload-hero">
      <div className="upload-hero__icon">
        <CameraIconLarge />
      </div>
      <h1>Photograph the khata page</h1>
      <p>
        Take a clear, well-lit photo of the ledger page. KhataAI reads handwritten
        Urdu, English, or mixed entries and turns them into a digital record.
      </p>

      <button
        className="btn btn--primary btn--full"
        onClick={() => inputRef.current?.click()}
        disabled={status === "uploading"}
      >
        {status === "uploading" ? "Reading the page…" : "Take or choose a photo"}
      </button>

      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden-input"
        onChange={handleFile}
      />

      {status === "error" && (
        <p style={{ color: "var(--due)", marginTop: "var(--space-4)", fontSize: 14 }}>
          {errorMessage}
        </p>
      )}
    </div>
  );
}

// --- Voice mode: secondary input path — record, send to /voice/process, review ---
function VoiceRecord() {
  const [status, setStatus] = useState("idle"); // idle | recording | processing | error
  const [errorMessage, setErrorMessage] = useState("");
  const [languageMode, setLanguageMode] = useState("urdu"); // "urdu" | "english"
  const [elapsedSec, setElapsedSec] = useState(0);

  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);
  const navigate = useNavigate();

  async function startRecording() {
    setErrorMessage("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = () => {
        stream.getTracks().forEach((track) => track.stop());
        handleRecordingComplete();
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setStatus("recording");
      setElapsedSec(0);
      timerRef.current = setInterval(() => setElapsedSec((s) => s + 1), 1000);
    } catch (err) {
      setStatus("error");
      setErrorMessage("Couldn't access the microphone. Check your browser's permission settings.");
    }
  }

  function stopRecording() {
    clearInterval(timerRef.current);
    mediaRecorderRef.current?.stop();
  }

  async function handleRecordingComplete() {
    setStatus("processing");
    const blob = new Blob(chunksRef.current, { type: "audio/webm" });
    const audioFile = new File([blob], "recording.webm", { type: "audio/webm" });

    try {
      const transaction = await processVoice(audioFile, languageMode);
      // /voice/process returns a single transaction — ReviewPage expects an
      // array (a photo can have several entries; a spoken one has exactly one).
      navigate("/review", { state: { transactions: [transaction], source: "voice" } });
    } catch (err) {
      setStatus("error");
      setErrorMessage(
        err.status === 422
          ? err.message
          : "Couldn't reach the server. Check your connection and try again."
      );
    }
  }

  return (
    <div className="upload-hero">
      <div className="upload-hero__icon">
        <MicIconLarge />
      </div>
      <h1>Speak the transaction</h1>
      <p>
        Say what happened naturally — for example, "Aslam ko paanch sau ka udhaar diya."
        KhataAI will transcribe it and turn it into a digital record.
      </p>

      <div className="lang-toggle">
        <button
          className={`lang-toggle__btn ${languageMode === "urdu" ? "is-active" : ""}`}
          onClick={() => setLanguageMode("urdu")}
          disabled={status === "recording" || status === "processing"}
        >
          اردو
        </button>
        <button
          className={`lang-toggle__btn ${languageMode === "english" ? "is-active" : ""}`}
          onClick={() => setLanguageMode("english")}
          disabled={status === "recording" || status === "processing"}
        >
          English
        </button>
      </div>

      {status === "idle" || status === "error" ? (
        <button className="btn btn--primary btn--full" onClick={startRecording}>
          Tap to record
        </button>
      ) : status === "recording" ? (
        <button className="btn btn--primary btn--full is-recording" onClick={stopRecording}>
          Recording… {elapsedSec}s — tap to stop
        </button>
      ) : (
        <button className="btn btn--primary btn--full" disabled>
          Processing…
        </button>
      )}

      {status === "error" && (
        <p style={{ color: "var(--due)", marginTop: "var(--space-4)", fontSize: 14 }}>
          {errorMessage}
        </p>
      )}
    </div>
  );
}

function CameraIconLarge() {
  return (
    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--paper)" strokeWidth="1.8">
      <path d="M4 8h3l1.5-2h7L17 8h3a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z" />
      <circle cx="12" cy="13" r="3.5" />
    </svg>
  );
}

function MicIconLarge() {
  return (
    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--paper)" strokeWidth="1.8">
      <rect x="9" y="2" width="6" height="12" rx="3" />
      <path d="M5 10v1a7 7 0 0 0 14 0v-1" />
      <path d="M12 18v3" />
      <path d="M8 21h8" />
    </svg>
  );
}