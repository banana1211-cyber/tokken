"""
アプリケーション設定
環境変数で管理する設定値
"""
import os
from dotenv import load_dotenv

load_dotenv()

# LLM設定
# プロバイダー: "openai" または "lmstudio"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

# LMStudio URL (LLM_PROVIDER="lmstudio" の場合に使用)
LMSTUDIO_URL = os.getenv("LMSTUDIO_URL", "http://localhost:1234/v1")
