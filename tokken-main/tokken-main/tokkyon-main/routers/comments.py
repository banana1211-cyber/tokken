"""
コメント管理API - DB連携
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Comment

router = APIRouter(prefix="/api/comments", tags=["comments"])


class CommentCreate(BaseModel):
    draft_id: str
    text: str
    selected_text: Optional[str] = None
    selection_start: int = 0
    selection_end: int = 0
    parent_comment_id: Optional[str] = None
    author: Optional[str] = "弁理士"


class CommentResolve(BaseModel):
    resolved: bool = True


def _serialize(comment: Comment, replies: list) -> dict:
    return {
        "id": comment.id,
        "draft_id": comment.draft_id,
        "text": comment.text,
        "selected_text": comment.selected_text,
        "selection_start": comment.selection_start,
        "selection_end": comment.selection_end,
        "resolved": comment.resolved,
        "created_at": comment.created_at.isoformat() if comment.created_at else None,
        "author": comment.user_id or "弁理士",
        "replies": [
            {
                "id": r.id,
                "text": r.text,
                "author": r.user_id or "担当者",
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in replies
        ],
    }


@router.get("/")
def list_comments(draft_id: Optional[str] = None, db: Session = Depends(get_db)):
    """明細書に紐づくコメント一覧（返信含む）"""
    query = db.query(Comment).filter(Comment.parent_comment_id == None)
    if draft_id:
        query = query.filter(Comment.draft_id == draft_id)
    comments = query.order_by(Comment.created_at.asc()).all()

    result = []
    for c in comments:
        replies = (
            db.query(Comment)
            .filter(Comment.parent_comment_id == c.id)
            .order_by(Comment.created_at.asc())
            .all()
        )
        result.append(_serialize(c, replies))
    return result


@router.post("/")
def create_comment(req: CommentCreate, db: Session = Depends(get_db)):
    """コメントまたは返信を投稿"""
    comment = Comment(
        draft_id=req.draft_id,
        text=req.text,
        selected_text=req.selected_text,
        selection_start=req.selection_start,
        selection_end=req.selection_end,
        parent_comment_id=req.parent_comment_id,
        user_id=req.author,  # ログインなしのため名前をuser_idに仮格納
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {"success": True, "id": comment.id}


@router.patch("/{comment_id}/resolve")
def resolve_comment(comment_id: str, req: CommentResolve, db: Session = Depends(get_db)):
    """コメントを解決済み/未解決に切り替え"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="コメントが見つかりません")
    comment.resolved = req.resolved
    db.commit()
    return {"success": True}


@router.delete("/{comment_id}")
def delete_comment(comment_id: str, db: Session = Depends(get_db)):
    """コメント削除"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="コメントが見つかりません")
    db.delete(comment)
    db.commit()
    return {"success": True}
