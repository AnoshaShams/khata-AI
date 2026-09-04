import { useEffect, useState } from "react";
import { getTrustScore, DEMO_BUSINESS_ID } from "../lib/api";

export default function ScorePage() {
  const [data, setData] = useState(null);
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    getTrustScore(DEMO_BUSINESS_ID)
      .then((d) => {
        setData(d);
        setStatus("ready");
      })
      .catch(() => setStatus("error"));
  }, []);

  if (status === "loading") {
    return (
      <div className="content">
        <div className="state-message">Calculating…</div>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="content">
        <div className="state-message">
          <strong>Couldn't load the trust score</strong>
          Check that the backend is running and try again.
        </div>
      </div>
    );
  }

  if (data.score === null) {
    return (
      <div className="content">
        <div className="state-message">
          <strong>Not enough data yet</strong>
          Record a few transactions first — the score builds from ledger history.
        </div>
      </div>
    );
  }

  return (
    <div className="content">
      <div className="score-badge">
        <div className={`score-badge__ring score-badge__ring--${data.band}`}>
          <span className="score-badge__value">{data.score}</span>
        </div>
        <span className="score-badge__band">{data.band} trust</span>
      </div>

      <p className="badge-note">{data.note}</p>

      <p style={{ fontSize: 13, fontWeight: 600, color: "var(--ink-faint)", margin: "var(--space-6) 0 var(--space-2)" }}>
        How this is calculated
      </p>

      {data.factors.map((f) => (
        <div className="factor-row" key={f.name}>
          <p className="factor-row__name">{f.name}</p>
          <p className="factor-row__detail">{f.detail}</p>
        </div>
      ))}
    </div>
  );
}
