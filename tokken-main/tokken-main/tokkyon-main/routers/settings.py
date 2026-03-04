"""
設定管理 API ルーター
"""
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI

from logging_config import logger
import config

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingsRequest(BaseModel):
    llm_provider: str
    lmstudio_url: str


class TestRequest(BaseModel):
    provider: str
    lmstudio_url: str = "http://localhost:1234/v1"


@router.get("")
async def get_settings():
    """現在の設定を取得"""
    return {
        "llm_provider": config.LLM_PROVIDER,
        "lmstudio_url": config.LMSTUDIO_URL,
    }


@router.post("")
async def save_settings(req: SettingsRequest):
    """設定を保存（ランタイム中のみ有効）"""
    logger.info(f"設定保存リクエスト: provider={req.llm_provider}, url={req.lmstudio_url}")

    if req.llm_provider not in ["openai", "lmstudio"]:
        logger.warning(f"無効なプロバイダー: {req.llm_provider}")
        raise HTTPException(status_code=400, detail="Invalid LLM provider")

    config.LLM_PROVIDER = req.llm_provider
    config.LMSTUDIO_URL = req.lmstudio_url
    logger.info("設定を保存しました")
    return {"success": True, "message": "設定を保存しました"}


@router.post("/test")
async def test_connection(req: TestRequest):
    """LLM接続テスト"""
    logger.info(f"接続テスト開始: provider={req.provider}")

    try:
        if req.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY が未設定")
                return {"success": False, "message": "OPENAI_API_KEY が設定されていません"}

            logger.debug("OpenAI APIに接続中...")
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            logger.info("OpenAI 接続成功")
            return {"success": True, "message": "OpenAI 接続成功 (モデル: gpt-4o)"}

        elif req.provider == "lmstudio":
            logger.debug(f"LMStudio ({req.lmstudio_url}) に接続中...")
            client = OpenAI(base_url=req.lmstudio_url, api_key="lm-studio")
            models = client.models.list()
            model_names = [m.id for m in models.data]
            if model_names:
                logger.info(f"LMStudio 接続成功 (モデル: {model_names[0]})")
                return {"success": True, "message": f"LMStudio 接続成功 (モデル: {model_names[0]})"}
            else:
                logger.info("LMStudio 接続成功 (モデルなし)")
                return {"success": True, "message": "LMStudio 接続成功 (モデルなし)"}

        else:
            logger.warning(f"不明なプロバイダー: {req.provider}")
            return {"success": False, "message": "不明なプロバイダー"}

    except Exception as e:
        logger.error(f"接続エラー: {str(e)}", exc_info=True)
        return {"success": False, "message": f"接続エラー: {str(e)}"}
