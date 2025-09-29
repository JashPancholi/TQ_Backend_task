# app/routers/items.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from typing import List

from .. import schemas, models, security, database

# Router for listing and purchasing items.
router = APIRouter(
    prefix="/items",
    tags=["Items"]
)


# Fetches and returns a list of all available items.
@router.get("/", response_model=List[schemas.Item])
def list_items(db: Session = Depends(database.get_db)):
    items = db.query(models.Item).all()
    return items


# Allows an authenticated user to purchase an item.
@router.post("/buy/{item_id}")
def buy_item(item_id: uuid.UUID, db: Session = Depends(database.get_db), current_user: models.User = Depends(security.get_current_user)):
    # Find the requested item in the database.
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Perform validation checks for stock and user's balance.
    if item.stock <= 0:
        raise HTTPException(status_code=400, detail="Item out of stock")

    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if user.wallet_balance < item.price:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Perform the transaction: update user balance and item stock.
    user.wallet_balance -= item.price
    item.stock -= 1

    # Log the purchase in the transactions table.
    new_transaction = models.Transaction(
        user_id=user.id,
        item_id=item.id,
        amount=item.price,
        type="purchase"
    )
    db.add(new_transaction)
    
    # Commit all changes to the database atomically.
    db.commit()
    db.refresh(user)

    return {
        "message": f"Successfully purchased {item.name}",
        "new_balance": user.wallet_balance,
        "item_stock_left": item.stock
    }