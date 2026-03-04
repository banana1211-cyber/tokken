"""
LLM Service - OpenAI / LMStudio 切り替え対応
"""
import asyncio
import os
from openai import OpenAI
from dotenv import load_dotenv

import config

load_dotenv()


class LLMService:
    """LLMプロバイダー抽象化クラス"""

    def __init__(self, provider: str = None):
        self.provider = provider or config.LLM_PROVIDER

        if self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY が設定されていません。環境変数を確認してください。")
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-5"
        elif self.provider == "lmstudio":
            self.client = OpenAI(base_url=config.LMSTUDIO_URL, api_key="lm-studio")
            self.model = "local-model"
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

    async def generate_patent_spec(self, repo_info: dict) -> str:
        """リポジトリ情報から特許明細書を生成"""

        prompt = self._build_prompt(repo_info)

        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model,
            messages=[
                {"role": "system", "content": "あなたは弁理士補助エンジニアです。日本特許庁(JPO)形式の特許明細書を生成します。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )

        content = response.choices[0].message.content.strip()
        if content.startswith("```html"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()

    def _build_prompt(self, repo_info: dict) -> str:
        """明細書生成プロンプトを構築"""

        return f"""以下のリポジトリ情報を基に、日本特許庁(JPO)形式の特許明細書をHTML形式で生成してください。

【リポジトリ情報】
- リポジトリ名: {repo_info.get('name', 'Unknown')}
- 説明: {repo_info.get('description', 'なし')}
- 主要言語: {repo_info.get('language', 'Unknown')}

【README内容】
{repo_info.get('readme', 'なし')}

【ファイル構成】
{repo_info.get('structure', 'なし')}

【出力形式】
以下の章構成でHTMLを生成してください。各章は <section class="patent-section" id="section-N"> タグで囲んでください。

1. 【発明の名称】
2. 【技術分野】
3. 【背景技術】
4. 【発明が解決しようとする課題】
5. 【課題を解決するための手段】
6. 【発明の効果】
7. 【図面の簡単な説明】(図1〜図3)
8. 【発明を実施するための形態】
9. 【符号の説明】
10. 【特許請求の範囲】(請求項1〜N)
11. 【要約書】

HTMLのみを出力してください。説明やマークダウンは不要です。
"""
