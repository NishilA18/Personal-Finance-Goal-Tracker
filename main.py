from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./finance.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    target_amount = Column(Float)
    current_amount = Column(Float, default=0.0)
    deadline = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    amount = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Pydantic Schemas
class GoalCreate(BaseModel):
    name: str
    target_amount: float
    deadline: str  # ISO format date

class GoalResponse(BaseModel):
    id: int
    name: str
    target_amount: float
    current_amount: float
    deadline: datetime
    progress: float

class TransactionCreate(BaseModel):
    description: str
    amount: float

class TransactionResponse(BaseModel):
    id: int
    description: str
    amount: float
    date: datetime

# FastAPI App
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.post("/api/goals/", response_model=GoalResponse)
def create_goal(goal: GoalCreate, db: Session = Depends(get_db)):
    db_goal = Goal(
        name=goal.name,
        target_amount=goal.target_amount,
        deadline=datetime.fromisoformat(goal.deadline)
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

@app.get("/api/goals/", response_model=list[GoalResponse])
def get_goals(db: Session = Depends(get_db)):
    goals = db.query(Goal).all()
    return [{
        "id": g.id,
        "name": g.name,
        "target_amount": g.target_amount,
        "current_amount": g.current_amount,
        "deadline": g.deadline,
        "progress": (g.current_amount / g.target_amount * 100) if g.target_amount > 0 else 0
    } for g in goals]

@app.post("/api/transactions/", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    db_txn = Transaction(**transaction.dict())
    db.add(db_txn)
    db.commit()
    db.refresh(db_txn)
    return db_txn

@app.get("/api/transactions/", response_model=list[TransactionResponse])
def get_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).order_by(Transaction.date.desc()).all()

@app.get("/api/summary/")
def get_summary(db: Session = Depends(get_db)):
    total_saved = db.query(Transaction).with_entities(func.sum(Transaction.amount)).scalar() or 0
    goals = db.query(Goal).all()
    return {
        "total_saved": total_saved,
        "goals_count": len(goals),
        "nearest_goal": min([(g.deadline - datetime.utcnow()).days for g in goals]) if goals else None
    }

# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
