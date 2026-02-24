"""
GitHub Client - PAT認証でリポジトリを解析
"""
import os
import base64
import httpx
from dotenv import load_dotenv

load_dotenv()


class GitHubClient:
    """GitHub API連携クラス"""
    
    def __init__(self):
        self.pat = os.getenv("GITHUB_PAT")
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if self.pat:
            self.headers["Authorization"] = f"Bearer {self.pat}"
    
    async def analyze_repository(self, repo_url: str) -> dict:
        """リポジトリを解析して情報を取得"""
        
        # URLからowner/repoを抽出
        owner, repo = self._parse_repo_url(repo_url)
        
        async with httpx.AsyncClient() as client:
            # リポジトリ基本情報
            repo_info = await self._get_repo_info(client, owner, repo)
            
            # README取得
            readme = await self._get_readme(client, owner, repo)
            
            # ファイル構成取得
            structure = await self._get_structure(client, owner, repo)
            
            return {
                "name": repo_info.get("name", "Unknown"),
                "description": repo_info.get("description", ""),
                "language": repo_info.get("language", "Unknown"),
                "readme": readme,
                "structure": structure
            }
    
    def _parse_repo_url(self, url: str) -> tuple:
        """GitHub URLからowner/repoを抽出"""
        # https://github.com/owner/repo or owner/repo
        url = url.replace("https://github.com/", "")
        url = url.replace("http://github.com/", "")
        url = url.rstrip("/")
        
        parts = url.split("/")
        if len(parts) >= 2:
            return parts[0], parts[1]
        raise ValueError(f"Invalid repository URL: {url}")
    
    async def _get_repo_info(self, client: httpx.AsyncClient, owner: str, repo: str) -> dict:
        """リポジトリ基本情報を取得"""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        response = await client.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        return {}
    
    async def _get_readme(self, client: httpx.AsyncClient, owner: str, repo: str) -> str:
        """READMEを取得"""
        url = f"{self.base_url}/repos/{owner}/{repo}/readme"
        response = await client.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("content", "")
            # Base64デコード
            try:
                return base64.b64decode(content).decode("utf-8")
            except Exception:
                return ""
        return ""
    
    async def _get_structure(self, client: httpx.AsyncClient, owner: str, repo: str, path: str = "", depth: int = 0) -> str:
        """ファイル構成を取得（最大2階層）"""
        if depth > 2:
            return ""
        
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        response = await client.get(url, headers=self.headers)
        
        if response.status_code != 200:
            return ""
        
        items = response.json()
        if not isinstance(items, list):
            return ""
        
        lines = []
        indent = "  " * depth
        
        for item in items[:20]:  # 最大20件
            name = item.get("name", "")
            item_type = item.get("type", "")
            
            if item_type == "dir":
                lines.append(f"{indent}📁 {name}/")
                # サブディレクトリを再帰取得
                sub_path = f"{path}/{name}" if path else name
                sub_structure = await self._get_structure(client, owner, repo, sub_path, depth + 1)
                if sub_structure:
                    lines.append(sub_structure)
            else:
                lines.append(f"{indent}📄 {name}")
        
        return "\n".join(lines)
