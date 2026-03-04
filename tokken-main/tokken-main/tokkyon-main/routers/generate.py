"""
Generate Router - 明細書生成エンドポイント
"""
import json
import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from services.llm_service import LLMService
from services.github_client import GitHubClient
from services.patent_generator import PatentGenerator
from logging_config import logger
from database import get_db
from models import Project, PatentDraft, HearingSheet

DATA_DIR = Path(__file__).parent.parent / "data"


router = APIRouter(prefix="/api", tags=["generate"])

github_client = GitHubClient()
patent_generator = PatentGenerator()


class GenerateRequest(BaseModel):
    repo_url: str
    applicant: str = "出願人"
    llm_provider: str = "openai"  # "openai" or "lmstudio"
    project_id: Optional[str] = None  # ヒアリングシート取得用


class CommentRequest(BaseModel):
    author: str
    text: str
    selection_start: int = 0
    selection_end: int = 0
    selected_text: str = ""


class ReplyRequest(BaseModel):
    author: str
    text: str


class ResolveRequest(BaseModel):
    resolved: bool = True


class SaveVersionRequest(BaseModel):
    content: str


@router.get("/patents")
async def list_patents(q: Optional[str] = None):
    """生成済み明細書の一覧を返す"""
    patents = []
    if DATA_DIR.exists():
        for path in DATA_DIR.glob("*.json"):
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                patents.append({
                    "id": data.get("id", path.stem),
                    "repo_url": data.get("repo_url", ""),
                    "created_at": data.get("created_at", ""),
                    "updated_at": data.get("updated_at", ""),
                    "comment_count": len(data.get("comments", [])),
                    "project_id": data.get("project_id")
                })
            except Exception:
                continue

    if q:
        patents = [p for p in patents if q.lower() in p["repo_url"].lower()]

    patents.sort(key=lambda p: p["created_at"], reverse=True)
    return patents


@router.post("/generate")
async def generate_patent(request: GenerateRequest, db: Session = Depends(get_db)):
    """リポジトリURLから特許明細書を生成"""
    
    logger.info(f"=== 明細書生成開始 ===")
    logger.info(f"リポジトリURL: {request.repo_url}")
    logger.info(f"出願人: {request.applicant}")
    logger.info(f"LLMプロバイダー: {request.llm_provider}")
    
    try:
        # リポジトリ解析
        logger.info("リポジトリ解析中...")
        repo_info = await github_client.analyze_repository(request.repo_url)
        logger.debug(f"リポジトリ情報: {repo_info.get('name')}, 言語: {repo_info.get('language')}")
        logger.info("リポジトリ解析完了")

        # ヒアリングシートを取得してrepo_infoに追加
        hearing_data = None
        if request.project_id:
            sheet = (
                db.query(HearingSheet)
                .filter(HearingSheet.project_id == request.project_id)
                .order_by(HearingSheet.updated_at.desc())
                .first()
            )
            if sheet:
                hearing_data = {
                    "patent_name": sheet.patent_name,
                    "problem_to_solve": sheet.problem_to_solve,
                    "existing_tech_problems": sheet.existing_tech_problems,
                    "composition": sheet.composition,
                    "features": sheet.features,
                }
                repo_info["hearing"] = hearing_data
                logger.info("ヒアリングシートをプロンプトに追加")

        # LLMで明細書生成
        logger.info(f"LLM ({request.llm_provider}) で明細書生成中...")
        llm = LLMService(provider=request.llm_provider)
        content = llm.generate_patent_spec(repo_info)
        logger.info(f"明細書生成完了 (文字数: {len(content)})")
        
        # 図面HTML追加
        logger.info("図面HTML生成中...")
        figures = patent_generator.generate_figures_html(repo_info)
        full_content = content + figures
        logger.info("図面HTML生成完了")
        
        # 保存
        patent_id = str(uuid.uuid4())[:8]
        logger.info(f"保存中... (ID: {patent_id})")
        patent = patent_generator.save_patent(patent_id, full_content, request.repo_url)
        logger.info(f"=== 明細書生成完了 (ID: {patent_id}) ===")

        # DBにPatentDraftを登録（既存プロジェクトがあればそこに紐付け）
        try:
            if request.project_id:
                # 既存プロジェクトに紐付ける
                linked_project_id = request.project_id
            else:
                # 新規プロジェクトを作成
                project = Project(
                    github_repo_url=request.repo_url,
                    customer_name=repo_info.get("name"),
                    status="draft"
                )
                db.add(project)
                db.flush()
                linked_project_id = project.id

            draft = PatentDraft(
                id=patent_id,
                project_id=linked_project_id,
                version=1,
                generated_by="ai",
                content=full_content
            )
            db.add(draft)
            db.commit()

            # JSONにproject_idを追記
            patent_generator.update_project_id(patent_id, linked_project_id)
        except Exception as e:
            logger.warning(f"DB登録スキップ: {e}")
            db.rollback()
            linked_project_id = None

        return {
            "success": True,
            "patent_id": patent_id,
            "project_id": linked_project_id,
            "content": full_content
        }
        
    except Exception as e:
        logger.error(f"エラー発生: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patent/{patent_id}")
async def get_patent(patent_id: str):
    """明細書を取得"""
    
    patent = patent_generator.get_patent(patent_id)
    if not patent:
        raise HTTPException(status_code=404, detail="Patent not found")
    
    return patent


@router.post("/patent/{patent_id}/comment")
async def add_comment(patent_id: str, request: CommentRequest):
    """コメントを追加"""
    
    comment = patent_generator.add_comment(patent_id, request.model_dump())
    if not comment:
        raise HTTPException(status_code=404, detail="Patent not found")
    
    return {"success": True, "comment": comment}


@router.post("/patent/{patent_id}/comment/{comment_id}/reply")
async def add_reply(patent_id: str, comment_id: str, request: ReplyRequest):
    """コメントに返信"""
    
    reply = patent_generator.add_reply(patent_id, comment_id, request.model_dump())
    if not reply:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return {"success": True, "reply": reply}


@router.patch("/patent/{patent_id}/content")
async def save_version(patent_id: str, request: SaveVersionRequest, db: Session = Depends(get_db)):
    """編集内容を保存し、新バージョンをDBに記録"""

    updated = patent_generator.update_content(patent_id, request.content)
    if not updated:
        raise HTTPException(status_code=404, detail="Patent not found")

    # 既存の最新バージョン番号を取得してインクリメント
    try:
        first_draft = db.query(PatentDraft).filter(PatentDraft.id == patent_id).first()
        project_id = first_draft.project_id if first_draft else None

        latest = (
            db.query(PatentDraft)
            .filter(PatentDraft.project_id == project_id)
            .order_by(PatentDraft.version.desc())
            .first()
        ) if project_id else first_draft
        next_version = (latest.version + 1) if latest else 2

        new_draft = PatentDraft(
            project_id=project_id,
            version=next_version,
            generated_by="manual",
            content=request.content
        )
        db.add(new_draft)
        db.commit()
        db.refresh(new_draft)
    except Exception as e:
        logger.warning(f"バージョン記録スキップ: {e}")
        db.rollback()

    return {"success": True}


@router.get("/patent/{patent_id}/versions")
async def get_versions(patent_id: str, db: Session = Depends(get_db)):
    """明細書のバージョン一覧を返す"""

    drafts = (
        db.query(PatentDraft)
        .filter(
            (PatentDraft.id == patent_id) |
            (PatentDraft.project_id.in_(
                db.query(PatentDraft.project_id).filter(PatentDraft.id == patent_id)
            ))
        )
        .order_by(PatentDraft.version.asc())
        .all()
    )
    return [
        {
            "id": d.id,
            "version": d.version,
            "generated_by": d.generated_by,
            "created_at": d.created_at.isoformat() if d.created_at else None
        }
        for d in drafts
    ]


@router.patch("/patent/{patent_id}/comment/{comment_id}/resolve")
async def resolve_comment(patent_id: str, comment_id: str, request: ResolveRequest):
    """コメントを解決済み/未解決に変更"""
    
    success = patent_generator.resolve_comment(patent_id, comment_id, request.resolved)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return {"success": True}
