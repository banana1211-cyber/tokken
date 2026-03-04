"""
Tokkyon - 特許明細書自動生成Webアプリ
"""
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from routers.generate import router as generate_router
from routers.settings import router as settings_router
from routers.users import router as users_router
from routers.projects import router as projects_router
from routers.patent_drafts import router as patent_drafts_router
from routers.hearing_sheets import router as hearing_sheets_router
from routers.files import router as files_router
from routers.comments import router as comments_router
from database import engine
import models

models.Base.metadata.create_all(bind=engine)

# アプリ初期化
app = FastAPI(
    title="Tokkyon",
    description="GitHubリポジトリから特許明細書を自動生成",
    version="1.0.0"
)

# CORS設定
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイル・テンプレート
BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# ルーター登録
app.include_router(generate_router)
app.include_router(settings_router)
app.include_router(users_router)
app.include_router(projects_router)
app.include_router(patent_drafts_router)
app.include_router(hearing_sheets_router)
app.include_router(files_router)
app.include_router(comments_router)


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "ok"}


@app.get("/")
async def index(request: Request):
    """トップページ"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/settings")
async def settings_page(request: Request):
    """設定ページ"""
    return templates.TemplateResponse("settings.html", {"request": request})


@app.get("/editor/{patent_id}")
async def editor(request: Request, patent_id: str):
    """明細書エディタページ"""
    return templates.TemplateResponse("editor.html", {"request": request, "patent_id": patent_id})


@app.get("/case-list")
async def case_list(request: Request):
    """案件一覧ページ"""
    return templates.TemplateResponse("case_list.html", {"request": request})


@app.get("/project/{project_id}")
async def project_detail(request: Request, project_id: str):
    """案件詳細ページ"""
    return templates.TemplateResponse("project_detail.html", {"request": request, "project_id": project_id})


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
