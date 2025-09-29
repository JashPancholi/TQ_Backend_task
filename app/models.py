import uuid
import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .database import Base


# Defines the User model, which maps to the "users" table in the database.
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    wallet_balance = Column(Integer, nullable=False, default=100)
    role = Column(String, default="user", nullable=False)  # For role-based access


# Defines the Item model for the "items" table.
class Item(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False)
    price = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False)


# Defines the Transaction model to log all purchases and credits in the "transactions" table.
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Foreign keys establish relationships to the users and items tables.
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=True) # Nullable for non-item transactions (e.g., admin credits).
    amount = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    type = Column(String, nullable=False, default="purchase") # e.g., 'purchase' or 'credit'