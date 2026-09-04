import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadLedgerPhoto } from "../lib/api";

export default function UploadPage() {
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
      navigate("/review", { state: { transactions } });
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
    <div className="content">
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
