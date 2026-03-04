"""
ヒアリングシート管理API
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from database import get_db
from models import HearingSheet

router = APIRouter(prefix="/api/hearing-sheets", tags=["hearing_sheets"])


class HearingSheetCreate(BaseModel):
    project_id: str
    patent_name: Optional[str] = None
    problem_to_solve: Optional[str] = None
    existing_tech_problems: Optional[str] = None
    composition: Optional[str] = None
    features: Optional[str] = None
    deadline: Optional[datetime] = None


class HearingSheetUpdate(BaseModel):
    patent_name: Optional[str] = None
    problem_to_solve: Optional[str] = None
    existing_tech_problems: Optional[str] = None
    composition: Optional[str] = None
    features: Optional[str] = None
    deadline: Optional[datetime] = None


@router.get("/")
def list_sheets(project_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(HearingSheet)
    if project_id:
        query = query.filter(HearingSheet.project_id == project_id)
    return query.all()


@router.post("/")
def create_sheet(req: HearingSheetCreate, db: Session = Depends(get_db)):
    sheet = HearingSheet(
        project_id=req.project_id,
        patent_name=req.patent_name,
        problem_to_solve=req.problem_to_solve,
        existing_tech_problems=req.existing_tech_problems,
        composition=req.composition,
        features=req.features,
        deadline=req.deadline
    )
    db.add(sheet)
    db.commit()
    db.refresh(sheet)
    return sheet


@router.get("/{sheet_id}")
def get_sheet(sheet_id: str, db: Session = Depends(get_db)):
    sheet = db.query(HearingSheet).filter(HearingSheet.id == sheet_id).first()
    if not sheet:
        raise HTTPException(status_code=404, detail="ヒアリングシートが見つかりません")
    return sheet


@router.patch("/{sheet_id}")
def update_sheet(sheet_id: str, req: HearingSheetUpdate, db: Session = Depends(get_db)):
    sheet = db.query(HearingSheet).filter(HearingSheet.id == sheet_id).first()
    if not sheet:
        raise HTTPException(status_code=404, detail="ヒアリングシートが見つかりません")
    for field, value in req.model_dump(exclude_none=True).items():
        setattr(sheet, field, value)
    db.commit()
    db.refresh(sheet)
    return sheet


@router.delete("/{sheet_id}")
def delete_sheet(sheet_id: str, db: Session = Depends(get_db)):
    sheet = db.query(HearingSheet).filter(HearingSheet.id == sheet_id).first()
    if not sheet:
        raise HTTPException(status_code=404, detail="ヒアリングシートが見つかりません")
    db.delete(sheet)
    db.commit()
    return {"success": True}
