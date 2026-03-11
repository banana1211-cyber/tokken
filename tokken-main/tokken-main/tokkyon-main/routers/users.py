"""
ユーザー管理API
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from database import get_db
from models import User

router = APIRouter(prefix="/api/users", tags=["users"])


class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    role: str = "client"


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None


@router.get("/")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.post("/")
def create_user(req: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="このメールアドレスは既に登録されています")
    user = User(email=req.email, password=req.password, name=req.name, role=req.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    return user


@router.patch("/{user_id}")
def update_user(user_id: str, req: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    if req.name:
        user.name = req.name
    if req.role:
        user.role = req.role
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    db.delete(user)
    db.commit()
    return {"success": True}
