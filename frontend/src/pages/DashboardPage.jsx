import { useEffect, useState } from "react";
import { getDashboard, DEMO_BUSINESS_ID } from "../lib/api";

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [status, setStatus] = useState("loading"); // loading | ready | error

  useEffect(() => {
    getDashboard(DEMO_BUSINESS_ID)
      .then((d) => {
        setData(d);
        setStatus("ready");
      })
      .catch(() => setStatus("error"));
  }, []);

  if (status === "loading") {
    return (
      <div className="content">
        <div className="state-message">Loading khata…</div>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="content">
        <div className="state-message">
          <strong>Couldn't load the khata</strong>
          Check that the backend is running and try again.
        </div>
      </div>
    );
  }

  const { customers, total_outstanding_udhaar, recent_transactions, cash_flow_summary } = data;

  return (
    <div className="content">
      <div className="summary-banner">
        <p className="summary-banner__label">Total outstanding udhaar</p>
        <p className="summary-banner__value">Rs {total_outstanding_udhaar.toLocaleString()}</p>
      </div>

      <SectionLabel>Customers</SectionLabel>
      {customers.length === 0 ? (
        <div className="state-message">
          <strong>No customers yet</strong>
          Photograph a khata page to add your first entries.
        </div>
      ) : (
        <div className="ledger-list" style={{ marginBottom: "var(--space-6)" }}>
          {customers.map((c) => (
            <div className="ledger-row" key={c.customer_id}>
              <div>
                <div className="ledger-row__name">{c.name}</div>
                <div className="ledger-row__meta">
                  {c.balance > 0 ? "Owes the shop" : c.balance < 0 ? "Credit balance" : "Settled"}
                </div>
              </div>
              <div className={`ledger-row__amount ${c.balance > 0 ? "amount--due" : c.balance < 0 ? "amount--paid" : ""}`}>
                Rs {Math.abs(c.balance).toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      )}

      <SectionLabel>This period</SectionLabel>
      <div className="ledger-list" style={{ marginBottom: "var(--space-6)" }}>
        <div className="ledger-row">
          <div className="ledger-row__name">Udhaar given</div>
          <div className="ledger-row__amount amount--due">
            Rs {cash_flow_summary.credit_given_recent.toLocaleString()}
          </div>
        </div>
        <div className="ledger-row">
          <div className="ledger-row__name">Payments received</div>
          <div className="ledger-row__amount amount--paid">
            Rs {cash_flow_summary.payments_received_recent.toLocaleString()}
          </div>
        </div>
      </div>

      <SectionLabel>Recent entries</SectionLabel>
      {recent_transactions.length === 0 ? (
        <div className="state-message">No entries recorded yet.</div>
      ) : (
        <div className="ledger-list">
          {recent_transactions.map((t) => (
            <div className="ledger-row" key={t.id}>
              <div>
                <div className="ledger-row__name">{t.customer_name}</div>
                <div className="ledger-row__meta">
                  {t.item ? `${t.item} · ` : ""}
                  {t.source === "photo" ? "from photo" : t.source === "voice" ? "from voice" : "manual"}
                </div>
              </div>
              <div className={`ledger-row__amount ${t.type === "credit" ? "amount--due" : "amount--paid"}`}>
                {t.type === "credit" ? "+" : "−"} Rs {t.amount.toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function SectionLabel({ children }) {
  return (
    <p style={{ fontSize: 13, fontWeight: 600, color: "var(--ink-faint)", margin: "0 0 var(--space-2)" }}>
      {children}
    </p>
  );
}
