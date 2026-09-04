import { useEffect, useState } from "react";
import { getReminders, DEMO_BUSINESS_ID } from "../lib/api";

export default function RemindersPage() {
  const [reminders, setReminders] = useState([]);
  const [status, setStatus] = useState("loading");
  const [copiedId, setCopiedId] = useState(null);

  useEffect(() => {
    getReminders(DEMO_BUSINESS_ID)
      .then((data) => {
        setReminders(data);
        setStatus("ready");
      })
      .catch(() => setStatus("error"));
  }, []);

  function handleCopy(id, message) {
    navigator.clipboard?.writeText(message);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 1500);
  }

  if (status === "loading") {
    return (
      <div className="content">
        <div className="state-message">Checking outstanding udhaar…</div>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="content">
        <div className="state-message">
          <strong>Couldn't load reminders</strong>
          Check that the backend is running and try again.
        </div>
      </div>
    );
  }

  if (reminders.length === 0) {
    return (
      <div className="content">
        <div className="state-message">
          <strong>Nothing overdue</strong>
          All customer balances are settled.
        </div>
      </div>
    );
  }

  return (
    <div className="content">
      <p style={{ color: "var(--ink-soft)", fontSize: 14, marginBottom: "var(--space-4)" }}>
        Drafted reminders for customers with outstanding udhaar. Sending isn't wired up to
        WhatsApp yet — copy the message to send it yourself for now.
      </p>

      {reminders.map((r) => (
        <div className="reminder-card" key={r.customer_id}>
          <p className="reminder-card__name">{r.customer_name}</p>
          <p className="reminder-card__amount">Rs {r.outstanding_amount.toLocaleString()} outstanding</p>
          <p className="reminder-card__message">{r.drafted_message}</p>
          <div className="reminder-card__actions">
            <button
              className="btn btn--ghost"
              style={{ flex: 1, padding: "10px" }}
              onClick={() => handleCopy(r.customer_id, r.drafted_message)}
            >
              {copiedId === r.customer_id ? "Copied" : "Copy message"}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
