import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import models, database
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# For password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# For JWT creation
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# This is the dependency that will be used in protected endpoints.
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the JWT to get its payload.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # The 'sub' (subject) of the token is the username we stored during login.
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        # If the token is invalid (bad signature, expired, etc.), raise an error.
        raise credentials_exception

    # Fetch the user from the database using the username from the token.
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        # If no user is found in the DB for that token, it's invalid.
        raise credentials_exception
    
    # Return the user object, making it available in the endpoint.
    return user

# Add this new function
def get_current_admin_user(current_user: models.User = Depends(get_current_user)):
    """
    Dependency that checks if the current user's role is 'admin'.
    If not, it raises a 403 Forbidden error.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have privileges to access this resource."
        )
    return current_user