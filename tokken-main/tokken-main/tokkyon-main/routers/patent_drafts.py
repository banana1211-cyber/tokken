"""
明細書管理API
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import PatentDraft

router = APIRouter(prefix="/api/patent-drafts", tags=["patent_drafts"])


class PatentDraftCreate(BaseModel):
    project_id: str
    version: int = 1
    generated_by: str = "ai"
    content: Optional[str] = None


class PatentDraftUpdate(BaseModel):
    content: Optional[str] = None
    generated_by: Optional[str] = None


@router.get("/")
def list_drafts(project_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(PatentDraft)
    if project_id:
        query = query.filter(PatentDraft.project_id == project_id)
    return query.all()


@router.post("/")
def create_draft(req: PatentDraftCreate, db: Session = Depends(get_db)):
    draft = PatentDraft(
        project_id=req.project_id,
        version=req.version,
        generated_by=req.generated_by,
        content=req.content
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft


@router.get("/{draft_id}")
def get_draft(draft_id: str, db: Session = Depends(get_db)):
    draft = db.query(PatentDraft).filter(PatentDraft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="明細書が見つかりません")
    return draft


@router.patch("/{draft_id}")
def update_draft(draft_id: str, req: PatentDraftUpdate, db: Session = Depends(get_db)):
    draft = db.query(PatentDraft).filter(PatentDraft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="明細書が見つかりません")
    if req.content is not None:
        draft.content = req.content
    if req.generated_by is not None:
        draft.generated_by = req.generated_by
    db.commit()
    db.refresh(draft)
    return draft


@router.delete("/{draft_id}")
def delete_draft(draft_id: str, db: Session = Depends(get_db)):
    draft = db.query(PatentDraft).filter(PatentDraft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="明細書が見つかりません")
    db.delete(draft)
    db.commit()
    return {"success": True}
