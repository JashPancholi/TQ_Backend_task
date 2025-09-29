# app/routers/wallet.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models, security, database

# Router for handling all wallet-related operations.
router = APIRouter(
    prefix="/wallet",
    tags=["Wallet"]
)


# Retrieves the balance for the currently authenticated user.
@router.get("/balance")
def get_wallet_balance(current_user: models.User = Depends(security.get_current_user)):
    return {"username": current_user.username, "balance": current_user.wallet_balance}


# Deducts a specified amount from the authenticated user's wallet.
@router.post("/spend")
def spend_from_wallet(spend_data: schemas.WalletSpend, db: Session = Depends(database.get_db), current_user: models.User = Depends(security.get_current_user)):
    # Basic input validation.
    if spend_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Spend amount must be positive.")

    # Get the user from the DB to ensure data is current, then check for sufficient funds.
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if user.wallet_balance < spend_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Update the balance and commit the change to the database.
    user.wallet_balance -= spend_data.amount
    db.commit()

    return {"message": "Amount spent successfully", "new_balance": user.wallet_balance}