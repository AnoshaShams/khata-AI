import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { confirmTransaction, DEMO_BUSINESS_ID } from "../lib/api";

export default function ReviewPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const incoming = location.state?.transactions;
  // Which input path produced these transactions — defaults to "photo" so
  // the existing OCR flow (which doesn't pass this yet) keeps working
  // unchanged. Voice flow passes source: "voice" explicitly.
  const sourceType = location.state?.source || "photo";

  // Give every row a stable local id + local edit state + accepted/discarded state.
  const [rows, setRows] = useState(() =>
    (incoming || []).map((t, i) => ({
      localId: `${i}-${t.customer_name}`,
      customer_name: t.customer_name,
      amount: t.amount,
      type: t.type,
      item: t.item || "",
      accepted: true, // default: shown as accepted, shopkeeper can uncheck
      discarded: false,
    }))
  );
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState("");

  if (!incoming || incoming.length === 0) {
    return (
      <div className="content">
        <div className="state-message">
          <strong>Nothing to review</strong>
          Go back and photograph a ledger page first.
        </div>
      </div>
    );
  }

  function updateRow(localId, field, value) {
    setRows((prev) =>
      prev.map((r) => (r.localId === localId ? { ...r, [field]: value } : r))
    );
  }

  function toggleAccept(localId) {
    setRows((prev) =>
      prev.map((r) => (r.localId === localId ? { ...r, accepted: !r.accepted } : r))
    );
  }

  function discardRow(localId) {
    setRows((prev) =>
      prev.map((r) => (r.localId === localId ? { ...r, discarded: true } : r))
    );
  }

  async function handleSaveAll() {
    const toSave = rows.filter((r) => r.accepted && !r.discarded);
    if (toSave.length === 0) return;

    setSaving(true);
    setSaveError("");
    try {
      // Sequential, not Promise.all — a partial failure should still leave
      // earlier rows saved rather than an all-or-nothing batch.
      for (const row of toSave) {
        await confirmTransaction({
          businessId: DEMO_BUSINESS_ID,
          customerName: row.customer_name,
          amount: parseFloat(row.amount),
          type: row.type,
          item: row.item,
          source: sourceType,
        });
      }
      navigate("/dashboard");
    } catch (err) {
      setSaveError("Some entries didn't save. Please try again.");
    } finally {
      setSaving(false);
    }
  }

  const visibleRows = rows.filter((r) => !r.discarded);
  const acceptedCount = visibleRows.filter((r) => r.accepted).length;

  return (
    <div className="content">
      <p style={{ color: "var(--ink-soft)", fontSize: 14, marginBottom: "var(--space-4)" }}>
        {visibleRows.length} entries found. Check each one, fix anything that's wrong, then save.
      </p>

      {visibleRows.map((row) => (
        <div className="review-row" key={row.localId}>
          <div className="review-row__top">
            <span className={`review-row__type-pill pill--${row.type}`}>
              {row.type === "credit" ? "Udhaar given" : "Payment received"}
            </span>
          </div>

          <div className="review-row__fields">
            <div className="field">
              <label htmlFor={`name-${row.localId}`}>Customer</label>
              <input
                id={`name-${row.localId}`}
                type="text"
                value={row.customer_name}
                onChange={(e) => updateRow(row.localId, "customer_name", e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor={`amount-${row.localId}`}>Amount (Rs)</label>
              <input
                id={`amount-${row.localId}`}
                type="number"
                inputMode="decimal"
                value={row.amount}
                onChange={(e) => updateRow(row.localId, "amount", e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor={`type-${row.localId}`}>Type</label>
              <select
                id={`type-${row.localId}`}
                value={row.type}
                onChange={(e) => updateRow(row.localId, "type", e.target.value)}
              >
                <option value="credit">Udhaar given</option>
                <option value="payment">Payment received</option>
              </select>
            </div>
            <div className="field">
              <label htmlFor={`item-${row.localId}`}>Item (optional)</label>
              <input
                id={`item-${row.localId}`}
                type="text"
                value={row.item}
                onChange={(e) => updateRow(row.localId, "item", e.target.value)}
              />
            </div>
          </div>

          <div className="review-row__actions">
            <button
              className={`icon-btn icon-btn--accept ${row.accepted ? "is-active" : ""}`}
              onClick={() => toggleAccept(row.localId)}
            >
              {row.accepted ? "✓ Will be saved" : "Mark correct"}
            </button>
            <button className="icon-btn icon-btn--discard" onClick={() => discardRow(row.localId)}>
              Discard
            </button>
          </div>
        </div>
      ))}

      {saveError && (
        <p style={{ color: "var(--due)", fontSize: 14, margin: "var(--space-3) 0" }}>{saveError}</p>
      )}

      <div style={{ marginTop: "var(--space-5)" }}>
        <button
          className="btn btn--primary btn--full"
          onClick={handleSaveAll}
          disabled={saving || acceptedCount === 0}
        >
          {saving ? "Saving…" : `Save ${acceptedCount} entr${acceptedCount === 1 ? "y" : "ies"} to khata`}
        </button>
      </div>
    </div>
  );
}