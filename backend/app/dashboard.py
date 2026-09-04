"""
Dashboard / Ledger View — aggregates transactions into what the shopkeeper
(and the demo) actually looks at: per-customer balances + overall cash flow.
"""
import datetime

from sqlalchemy.orm import Session

from app.db import Customer, Transaction


def get_dashboard(db: Session, business_id: str) -> dict:
    customers = db.query(Customer).filter(Customer.business_id == business_id).all()

    customer_rows = []
    total_outstanding = 0.0
    for c in customers:
        customer_rows.append({
            "customer_id": c.id,
            "name": c.name,
            "balance": round(c.balance, 2),  # positive = they owe the shop
        })
        if c.balance > 0:
            total_outstanding += c.balance

    txns = (
        db.query(Transaction)
        .filter(Transaction.business_id == business_id)
        .order_by(Transaction.created_at.desc())
        .limit(50)
        .all()
    )
    recent = [
        {
            "id": t.id,
            "customer_name": next((c.name for c in customers if c.id == t.customer_id), "Unknown"),
            "type": t.type,
            "amount": t.amount,
            "item": t.item,
            "source": t.source,
            "balance_after": t.balance_after,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in txns
    ]

    total_sales_period = sum(t.amount for t in txns if t.type == "credit")
    total_payments_period = sum(t.amount for t in txns if t.type == "payment")

    return {
        "business_id": business_id,
        "customers": sorted(customer_rows, key=lambda r: r["balance"], reverse=True),
        "total_outstanding_udhaar": round(total_outstanding, 2),
        "recent_transactions": recent,
        "cash_flow_summary": {
            "credit_given_recent": round(total_sales_period, 2),
            "payments_received_recent": round(total_payments_period, 2),
        },
        "generated_at": datetime.datetime.utcnow().isoformat(),
    }
