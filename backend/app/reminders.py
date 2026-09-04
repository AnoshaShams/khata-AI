"""
Udhaar Reminders. Per AGENTS.md: if there's no time to wire a real WhatsApp
send, draft the message and stub the send step — demo as "ready to connect,"
never fake it as actually delivered.
"""
from sqlalchemy.orm import Session

from app.db import Customer, ReminderDraft

OVERDUE_THRESHOLD = 0  # any positive balance is "outstanding" for v1; tune later


def draft_message(customer_name: str, amount: float) -> str:
    # Kept short, polite, natural — not a robotic field dump. Roman Urdu default;
    # swap for Urdu script if/when the language toggle applies to outbound messages.
    return (
        f"Salam {customer_name} bhai/baji, aap ka Rs {amount:.0f} udhaar abhi pending hai. "
        f"Jab mumkin ho ada kar dijiye ga, shukriya."
    )


def get_pending_reminders(db: Session, business_id: str) -> list[dict]:
    customers = (
        db.query(Customer)
        .filter(Customer.business_id == business_id, Customer.balance > OVERDUE_THRESHOLD)
        .all()
    )

    results = []
    for c in customers:
        message = draft_message(c.name, c.balance)
        draft = ReminderDraft(customer_id=c.id, message=message, sent=False)
        db.add(draft)
        results.append({
            "customer_id": c.id,
            "customer_name": c.name,
            "outstanding_amount": round(c.balance, 2),
            "drafted_message": message,
            "send_status": "not_sent",  # honest: WhatsApp send is stubbed for hackathon scope
        })
    db.commit()
    return results
