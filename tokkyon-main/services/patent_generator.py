"""
Patent Generator - 明細書HTML生成とコメント管理
"""
import os
import json
import uuid
from datetime import datetime
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


class PatentGenerator:
    """明細書生成とコメント管理"""
    
    def __init__(self):
        self.data_dir = DATA_DIR
    
    def save_patent(self, patent_id: str, content: str, repo_url: str) -> dict:
        """生成した明細書を保存"""
        
        patent_data = {
            "id": patent_id,
            "repo_url": repo_url,
            "content": content,
            "comments": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        file_path = self.data_dir / f"{patent_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(patent_data, f, ensure_ascii=False, indent=2)
        
        return patent_data
    
    def get_patent(self, patent_id: str) -> dict | None:
        """明細書を取得"""
        
        file_path = self.data_dir / f"{patent_id}.json"
        if not file_path.exists():
            return None
        
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def add_comment(self, patent_id: str, comment_data: dict) -> dict | None:
        """コメントを追加"""
        
        patent = self.get_patent(patent_id)
        if not patent:
            return None
        
        comment = {
            "id": str(uuid.uuid4()),
            "author": comment_data.get("author", "匿名"),
            "text": comment_data.get("text", ""),
            "selection_start": comment_data.get("selection_start", 0),
            "selection_end": comment_data.get("selection_end", 0),
            "selected_text": comment_data.get("selected_text", ""),
            "replies": [],
            "resolved": False,
            "created_at": datetime.now().isoformat()
        }
        
        patent["comments"].append(comment)
        patent["updated_at"] = datetime.now().isoformat()
        
        self._save(patent)
        return comment
    
    def add_reply(self, patent_id: str, comment_id: str, reply_data: dict) -> dict | None:
        """コメントに返信を追加"""
        
        patent = self.get_patent(patent_id)
        if not patent:
            return None
        
        for comment in patent["comments"]:
            if comment["id"] == comment_id:
                reply = {
                    "id": str(uuid.uuid4()),
                    "author": reply_data.get("author", "匿名"),
                    "text": reply_data.get("text", ""),
                    "created_at": datetime.now().isoformat()
                }
                comment["replies"].append(reply)
                patent["updated_at"] = datetime.now().isoformat()
                self._save(patent)
                return reply
        
        return None
    
    def resolve_comment(self, patent_id: str, comment_id: str, resolved: bool = True) -> bool:
        """コメントを解決済み/未解決に変更"""
        
        patent = self.get_patent(patent_id)
        if not patent:
            return False
        
        for comment in patent["comments"]:
            if comment["id"] == comment_id:
                comment["resolved"] = resolved
                patent["updated_at"] = datetime.now().isoformat()
                self._save(patent)
                return True
        
        return False
    
    def _save(self, patent: dict):
        """明細書データを保存"""
        file_path = self.data_dir / f"{patent['id']}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(patent, f, ensure_ascii=False, indent=2)
    
    def generate_figures_html(self, repo_info: dict) -> str:
        """図面HTML（図1〜3）を生成"""
        
        return f"""
<div class="patent-figures">
    <div class="figure" id="figure-1">
        <h4>【図1】システム構成図</h4>
        <div class="figure-content">
            <svg viewBox="0 0 400 300" class="figure-svg">
                <rect x="50" y="20" width="120" height="60" fill="#e3f2fd" stroke="#1976d2" stroke-width="2" rx="8"/>
                <text x="110" y="55" text-anchor="middle" font-size="14">ユーザー端末</text>
                
                <rect x="230" y="20" width="120" height="60" fill="#e8f5e9" stroke="#388e3c" stroke-width="2" rx="8"/>
                <text x="290" y="55" text-anchor="middle" font-size="14">サーバー</text>
                
                <rect x="140" y="140" width="120" height="60" fill="#fff3e0" stroke="#f57c00" stroke-width="2" rx="8"/>
                <text x="200" y="175" text-anchor="middle" font-size="14">処理エンジン</text>
                
                <rect x="140" y="230" width="120" height="60" fill="#fce4ec" stroke="#c2185b" stroke-width="2" rx="8"/>
                <text x="200" y="265" text-anchor="middle" font-size="14">データベース</text>
                
                <line x1="170" y1="80" x2="170" y2="140" stroke="#666" stroke-width="2" marker-end="url(#arrow)"/>
                <line x1="230" y1="80" x2="230" y2="140" stroke="#666" stroke-width="2" marker-end="url(#arrow)"/>
                <line x1="200" y1="200" x2="200" y2="230" stroke="#666" stroke-width="2" marker-end="url(#arrow)"/>
                
                <defs>
                    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                        <path d="M0,0 L0,6 L9,3 z" fill="#666"/>
                    </marker>
                </defs>
            </svg>
        </div>
        <p class="figure-caption">図1は、本発明のシステム構成を示す概念図である。</p>
    </div>
    
    <div class="figure" id="figure-2">
        <h4>【図2】処理シーケンス図</h4>
        <div class="figure-content">
            <svg viewBox="0 0 400 250" class="figure-svg">
                <line x1="80" y1="30" x2="80" y2="230" stroke="#1976d2" stroke-width="2"/>
                <line x1="200" y1="30" x2="200" y2="230" stroke="#388e3c" stroke-width="2"/>
                <line x1="320" y1="30" x2="320" y2="230" stroke="#f57c00" stroke-width="2"/>
                
                <rect x="50" y="10" width="60" height="25" fill="#e3f2fd" stroke="#1976d2" rx="4"/>
                <text x="80" y="27" text-anchor="middle" font-size="11">クライアント</text>
                
                <rect x="170" y="10" width="60" height="25" fill="#e8f5e9" stroke="#388e3c" rx="4"/>
                <text x="200" y="27" text-anchor="middle" font-size="11">サーバー</text>
                
                <rect x="290" y="10" width="60" height="25" fill="#fff3e0" stroke="#f57c00" rx="4"/>
                <text x="320" y="27" text-anchor="middle" font-size="11">DB</text>
                
                <line x1="80" y1="60" x2="200" y2="60" stroke="#333" stroke-width="1" marker-end="url(#arrow2)"/>
                <text x="140" y="55" text-anchor="middle" font-size="10">1. リクエスト</text>
                
                <line x1="200" y1="100" x2="320" y2="100" stroke="#333" stroke-width="1" marker-end="url(#arrow2)"/>
                <text x="260" y="95" text-anchor="middle" font-size="10">2. クエリ</text>
                
                <line x1="320" y1="140" x2="200" y2="140" stroke="#333" stroke-width="1" stroke-dasharray="5,3" marker-end="url(#arrow2)"/>
                <text x="260" y="135" text-anchor="middle" font-size="10">3. 結果</text>
                
                <line x1="200" y1="180" x2="80" y2="180" stroke="#333" stroke-width="1" stroke-dasharray="5,3" marker-end="url(#arrow2)"/>
                <text x="140" y="175" text-anchor="middle" font-size="10">4. レスポンス</text>
                
                <defs>
                    <marker id="arrow2" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
                        <path d="M0,0 L0,6 L7,3 z" fill="#333"/>
                    </marker>
                </defs>
            </svg>
        </div>
        <p class="figure-caption">図2は、本発明の処理シーケンスを示す図である。</p>
    </div>
    
    <div class="figure" id="figure-3">
        <h4>【図3】ユーザインタフェース概念図</h4>
        <div class="figure-content">
            <svg viewBox="0 0 400 280" class="figure-svg">
                <rect x="20" y="10" width="360" height="260" fill="#f5f5f5" stroke="#333" stroke-width="2" rx="8"/>
                
                <rect x="20" y="10" width="360" height="40" fill="#1976d2" rx="8"/>
                <rect x="20" y="30" width="360" height="20" fill="#1976d2"/>
                <text x="40" y="35" fill="white" font-size="14" font-weight="bold">{repo_info.get('name', 'アプリケーション')}</text>
                
                <rect x="35" y="65" width="250" height="25" fill="white" stroke="#ccc" rx="4"/>
                <text x="45" y="82" fill="#999" font-size="12">検索...</text>
                
                <rect x="295" y="65" width="70" height="25" fill="#4caf50" rx="4"/>
                <text x="330" y="82" fill="white" text-anchor="middle" font-size="12">実行</text>
                
                <rect x="35" y="105" width="330" height="150" fill="white" stroke="#e0e0e0" rx="4"/>
                <text x="50" y="130" font-size="12" fill="#333">結果表示エリア</text>
                <line x1="50" y1="145" x2="350" y2="145" stroke="#eee"/>
                <text x="50" y="165" font-size="11" fill="#666">項目1: データ内容</text>
                <text x="50" y="185" font-size="11" fill="#666">項目2: データ内容</text>
                <text x="50" y="205" font-size="11" fill="#666">項目3: データ内容</text>
            </svg>
        </div>
        <p class="figure-caption">図3は、本発明のユーザインタフェースを示す概念図である。</p>
    </div>
</div>
"""
