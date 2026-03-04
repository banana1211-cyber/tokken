"""
案件管理API
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Project

router = APIRouter(prefix="/api/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    user_id: str
    github_repo_url: Optional[str] = None
    customer_name: str
    status: str = "draft"


class ProjectUpdate(BaseModel):
    github_repo_url: Optional[str] = None
    customer_name: Optional[str] = None
    status: Optional[str] = None


@router.get("/")
def list_projects(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Project)
    if status:
        query = query.filter(Project.status == status)
    return query.all()


@router.post("/")
def create_project(req: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(
        user_id=req.user_id,
        github_repo_url=req.github_repo_url,
        customer_name=req.customer_name,
        status=req.status
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}")
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="案件が見つかりません")
    return project


@router.patch("/{project_id}")
def update_project(project_id: str, req: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="案件が見つかりません")
    if req.github_repo_url is not None:
        project.github_repo_url = req.github_repo_url
    if req.customer_name is not None:
        project.customer_name = req.customer_name
    if req.status is not None:
        project.status = req.status
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="案件が見つかりません")
    db.delete(project)
    db.commit()
    return {"success": True}
