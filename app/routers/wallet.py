from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid # Make sure uuid is imported
from .. import schemas, models, security, database
from typing import List

router = APIRouter(
    prefix="/wallet",
    tags=["Wallet"]
)

def process_wallet_debit(db: Session, user: models.User, amount: int, item_id: uuid.UUID | None = None):
    """
    This is the core logic for debiting a user's wallet.
    It checks for funds, deducts the amount, and logs the transaction.
    This function can be imported and used by any part of the application.
    """
    #Input Validation: 
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Debit amount must be positive.")

    #Fetch Fresh Data: Gets the most current user data from the database to avoid race conditions.
    db_user = db.query(models.User).filter(models.User.id == user.id).first()

    #Prevents the balance from going negative.
    if db_user.wallet_balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    #Subtracts the amount from the user's balance.
    db_user.wallet_balance -= amount

    #Creates a new record in the transactions table.
    debit_transaction = models.Transaction(
        user_id=db_user.id,
        item_id=item_id,  # This will be an ID if it's an item purchase, or None for general spending
        amount=amount,
        type="purchase" if item_id else "spend"  # Sets the transaction type accordingly
    )
    db.add(debit_transaction)
    
    # 6. Return the Updated User: The calling function is responsible for committing the changes.
    return db_user

@router.post("/spend")
def spend_from_wallet(spend_data: schemas.WalletSpend, db: Session = Depends(database.get_db), current_user: models.User = Depends(security.get_current_user)):
    """
    API endpoint for a user to spend an arbitrary amount from their wallet.
    This now acts as a simple wrapper around our core debit logic.
    """
    updated_user = process_wallet_debit(db=db, user=current_user, amount=spend_data.amount)
    
    db.commit() # Commit the transaction here

    return {"message": "Amount spent successfully", "new_balance": updated_user.wallet_balance}


@router.get("/balance")
def get_wallet_balance(current_user: models.User = Depends(security.get_current_user)):
    return {"username": current_user.username, "balance": current_user.wallet_balance}

 # Add List to your imports at the top


@router.get("/transactions", response_model=List[schemas.Transaction])
def get_transaction_history(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Retrieves the transaction history for the currently authenticated user,
    ordered from newest to oldest.
    """
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    ).order_by(models.Transaction.timestamp.desc()).all()

    return transactions