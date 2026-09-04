"""
Trust Score. Per AGENTS.md: "bank-ready credit score" is explicitly OUT of
scope for this build — this is a simple, explainable heuristic. Say so plainly
to judges: v1 heuristic, roadmap item for a real scoring model.

Score is 0-100, built from three legible factors so it's never a black box.
"""
from sqlalchemy.orm import Session

from app.db import Customer, Transaction


def compute_trust_score(db: Session, business_id: str) -> dict:
    customers = db.query(Customer).filter(Customer.business_id == business_id).all()
    all_txns = db.query(Transaction).filter(Transaction.business_id == business_id).all()

    if not all_txns:
        return {
            "business_id": business_id,
            "score": None,
            "band": "insufficient_data",
            "factors": [],
            "note": "Heuristic v1 score — not a bank-grade credit score.",
        }

    total_credit_given = sum(t.amount for t in all_txns if t.type == "credit")
    total_paid_back = sum(t.amount for t in all_txns if t.type == "payment")

    # Factor 1: repayment rate (of everything ever given on credit, how much came back)
    repayment_rate = (total_paid_back / total_credit_given) if total_credit_given > 0 else 1.0
    repayment_rate = min(repayment_rate, 1.0)

    # Factor 2: outstanding ratio (lower is better — less of the book is unpaid)
    outstanding = sum(c.balance for c in customers if c.balance > 0)
    outstanding_ratio = (outstanding / total_credit_given) if total_credit_given > 0 else 0.0
    outstanding_score = max(0.0, 1.0 - outstanding_ratio)

    # Factor 3: activity (more recorded transactions = more signal to trust)
    activity_score = min(len(all_txns) / 30, 1.0)  # 30+ txns = full marks for v1

    weights = {"repayment_rate": 0.5, "outstanding_ratio": 0.3, "activity": 0.2}
    raw_score = (
        repayment_rate * weights["repayment_rate"]
        + outstanding_score * weights["outstanding_ratio"]
        + activity_score * weights["activity"]
    )
    score_0_100 = round(raw_score * 100)

    band = "low" if score_0_100 < 40 else "medium" if score_0_100 < 75 else "high"

    return {
        "business_id": business_id,
        "score": score_0_100,
        "band": band,
        "factors": [
            {"name": "Udhaar repayment rate", "weight": weights["repayment_rate"],
             "detail": f"{repayment_rate * 100:.0f}% of credit given has been repaid"},
            {"name": "Outstanding udhaar ratio", "weight": weights["outstanding_ratio"],
             "detail": f"Rs {outstanding:.0f} currently outstanding across all customers"},
            {"name": "Ledger activity", "weight": weights["activity"],
             "detail": f"{len(all_txns)} transactions recorded"},
        ],
        "note": "Heuristic v1 score — not a bank-grade credit score.",
    }
