"""
Ledger Data Store. SQLite for the hackathon build — no need for anything
heavier at this scope. Three tables: customers, transactions, reminders.

Balance convention: a customer's `balance` is what THEY owe the shopkeeper.
- type="credit" (shopkeeper gave goods/credit) -> balance increases
- type="payment" (customer paid back) -> balance decreases
"""
import datetime
import uuid

from sqlalchemy import create_engine, Column, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from app.config import settings

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    balance = Column(Float, default=0.0)  # what this customer owes

    transactions = relationship("Transaction", back_populates="customer")


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String, index=True, nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    type = Column(String, nullable=False)  # "credit" | "payment"
    amount = Column(Float, nullable=False)
    item = Column(String, nullable=True)
    source = Column(String, nullable=False, default="manual")  # "photo" | "voice" | "manual"
    balance_after = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    customer = relationship("Customer", back_populates="transactions")


class ReminderDraft(Base):
    __tablename__ = "reminders"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    message = Column(String, nullable=False)
    drafted_at = Column(DateTime, default=datetime.datetime.utcnow)
    sent = Column(Boolean, default=False)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_or_create_customer(db, business_id: str, name: str) -> Customer:
    customer = (
        db.query(Customer)
        .filter(Customer.business_id == business_id, Customer.name == name)
        .first()
    )
    if customer:
        return customer
    customer = Customer(business_id=business_id, name=name, balance=0.0)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def save_transaction(db, business_id: str, customer_name: str, type_: str, amount: float,
                      item: str | None, source: str) -> Transaction:
    customer = get_or_create_customer(db, business_id, customer_name)

    if type_ == "credit":
        customer.balance += amount
    elif type_ == "payment":
        customer.balance -= amount

    txn = Transaction(
        business_id=business_id,
        customer_id=customer.id,
        type=type_,
        amount=amount,
        item=item,
        source=source,
        balance_after=customer.balance,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn
