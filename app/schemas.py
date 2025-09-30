from pydantic import BaseModel
import uuid
import datetime

# User Schemas
class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: uuid.UUID
    username: str
    wallet_balance: int

    class Config:
        from_attributes = True

# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str

# Item Schemas
class ItemBase(BaseModel):
    name: str
    price: int
    stock: int

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

# Wallet Schemas
class WalletSpend(BaseModel):
    amount: int

class Transaction(BaseModel):
    id: uuid.UUID
    item_id: uuid.UUID | None # Use | None for optional fields
    amount: int
    timestamp: datetime.datetime
    type: str

    class Config:
        from_attributes = True

class TransactionHistory(BaseModel):
    transactions: list[Transaction]

class AdminItemCreate(BaseModel):
    name: str
    price: int
    stock: int

class AdminCreditWallet(BaseModel):
    user_id: uuid.UUID
    amount: int