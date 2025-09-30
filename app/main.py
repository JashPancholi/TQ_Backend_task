from fastapi import FastAPI, Depends
from . import models
from .database import engine, SessionLocal
from .routers import auth, wallet, items, admin
from sqlalchemy.orm import Session

# This creates the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Pre-populate items on startup
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    # Check if items already exist
    if db.query(models.Item).count() == 0:
        items_to_add = [
            models.Item(name="Book", price=50, stock=20),
            models.Item(name="Pen", price=10, stock=100),
            models.Item(name="Laptop", price=80, stock=5)
        ]
        db.add_all(items_to_add)
        db.commit()
    db.close()

app.include_router(auth.router)
app.include_router(wallet.router)
app.include_router(items.router)
app.include_router(admin.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the TQ Tech Backend API"}