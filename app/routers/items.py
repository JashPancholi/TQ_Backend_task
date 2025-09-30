from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from typing import List
from .. import schemas, models, security, database
from .wallet import process_wallet_debit 

router = APIRouter(
    prefix="/items",
    tags=["Items"]
)

@router.get("/", response_model=List[schemas.Item])
def list_items(db: Session = Depends(database.get_db)):
    items = db.query(models.Item).all()
    return items

@router.post("/buy/{item_id}")
def buy_item(item_id: uuid.UUID, db: Session = Depends(database.get_db), current_user: models.User = Depends(security.get_current_user)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.stock <= 0:
        raise HTTPException(status_code=400, detail="Item out of stock")

    # Instead of manually changing the balance, we call our new reusable function.
    try:
        updated_user = process_wallet_debit(db=db, user=current_user, amount=item.price, item_id=item.id)
    except HTTPException as e:
        raise e

    # Decrement the item's stock
    item.stock -= 1
    
    # Commit all changes together (user balance, transaction log, and item stock)
    db.commit()
    db.refresh(updated_user) # Refresh the user object to get the latest state

    return {
        "message": f"Successfully purchased {item.name}",
        "new_balance": updated_user.wallet_balance,
        "item_stock_left": item.stock
    }