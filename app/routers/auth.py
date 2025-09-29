# app/routers/auth.py

# Import necessary modules from FastAPI, SQLAlchemy, and our local files.
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from .. import schemas, models, security, database

# Create a router to group authentication-related endpoints.
router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


# Endpoint for new user registration.
@router.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Check if a user with the same username already exists to enforce uniqueness.
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hash the user's plain-text password before storing it for security.
    hashed_password = security.get_password_hash(user.password)
    new_user = models.User(username=user.username, password_hash=hashed_password)

    # Add the new user to the database session, commit it, and refresh the instance.
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Endpoint for user login, which returns a JWT access token upon successful authentication.
@router.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Find the user by username and then verify their provided password against the stored hash.
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # If authentication is successful, create a new JWT access token.
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username, "user_id": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}