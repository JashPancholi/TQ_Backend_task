from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models, security, database

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(security.get_current_admin_user)] # This protects all routes in this file!
)

@router.post("/items", response_model=schemas.Item)
def add_new_item(item_data: schemas.AdminItemCreate, db: Session = Depends(database.get_db)):
    """
    Admin-only endpoint to add a new item to the store.
    """
    new_item = models.Item(**item_data.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.post("/wallet/credit")
def credit_user_wallet(credit_data: schemas.AdminCreditWallet, db: Session = Depends(database.get_db)):
    """
    Admin-only endpoint to credit a user's wallet and log the transaction.
    """
    if credit_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Credit amount must be positive.")

    user_to_credit = db.query(models.User).filter(models.User.id == credit_data.user_id).first()
    if not user_to_credit:
        raise HTTPException(status_code=404, detail="User not found.")

    # Add the amount to the user's balance
    user_to_credit.wallet_balance += credit_data.amount

    # Log this action as a 'credit' transaction
    credit_transaction = models.Transaction(
        user_id=user_to_credit.id,
        amount=credit_data.amount,
        type="credit"
    )
    db.add(credit_transaction)
    db.commit()
    db.refresh(user_to_credit)

    return {
        "message": "Wallet credited successfully.",
        "user": user_to_credit.username,
        "new_balance": user_to_credit.wallet_balance
    }