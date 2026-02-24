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


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
