# app/schemas.py
from pydantic import BaseModel
import uuid

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