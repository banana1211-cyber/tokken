"""
Generate Router - 明細書生成エンドポイント
"""
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.llm_service import LLMService
from services.github_client import GitHubClient
from services.patent_generator import PatentGenerator
from logging_config import logger


router = APIRouter(prefix="/api", tags=["generate"])

github_client = GitHubClient()
patent_generator = PatentGenerator()


class GenerateRequest(BaseModel):
    repo_url: str
    applicant: str = "出願人"
    llm_provider: str = "openai"  # "openai" or "lmstudio"


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


@router.post("/generate")
async def generate_patent(request: GenerateRequest):
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
        
        return {
            "success": True,
            "patent_id": patent_id,
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


@router.patch("/patent/{patent_id}/comment/{comment_id}/resolve")
async def resolve_comment(patent_id: str, comment_id: str, request: ResolveRequest):
    """コメントを解決済み/未解決に変更"""
    
    success = patent_generator.resolve_comment(patent_id, comment_id, request.resolved)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return {"success": True}
