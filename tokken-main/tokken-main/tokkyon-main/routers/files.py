"""
添付ファイル管理API
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import File

router = APIRouter(prefix="/api/files", tags=["files"])


class FileCreate(BaseModel):
    project_id: str
    file_name: str
    file_url: str
    type: str = "reference"


@router.get("/")
def list_files(project_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(File)
    if project_id:
        query = query.filter(File.project_id == project_id)
    return query.all()


@router.post("/")
def create_file(req: FileCreate, db: Session = Depends(get_db)):
    file = File(
        project_id=req.project_id,
        file_name=req.file_name,
        file_url=req.file_url,
        type=req.type
    )
    db.add(file)
    db.commit()
    db.refresh(file)
    return file


@router.get("/{file_id}")
def get_file(file_id: str, db: Session = Depends(get_db)):
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")
    return file


@router.delete("/{file_id}")
def delete_file(file_id: str, db: Session = Depends(get_db)):
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")
    db.delete(file)
    db.commit()
    return {"success": True}
