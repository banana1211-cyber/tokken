# 📄 Tokkyon

GitHubリポジトリから日本特許庁(JPO)形式の特許明細書を自動生成するWebアプリケーション。

## 🚀 インストール

### 前提条件
- Python 3.10+
- GitHub Personal Access Token (PAT)
- OpenAI API Key (または LMStudio)

### 1. リポジトリをクローン
```bash
git clone https://github.com/your-username/tokkyon.git
cd tokkyon
```

### 2. 仮想環境を作成・有効化
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. 依存パッケージをインストール
```bash
pip install -r requirements.txt
```

### 3. 環境変数を設定
`.env.example` をコピーして `.env` を作成:
```bash
cp .env.example .env
```

`.env` を編集してAPIキーを設定:
```
GITHUB_PAT=your_github_personal_access_token
OPENAI_API_KEY=your_openai_api_key
```

## ▶️ サーバー起動

```bash
python main.py
```

ブラウザで http://localhost:8000 を開く。

## ⚙️ 設定

ヘッダー右上の「⚙️ 設定」から:
- **LLMプロバイダー**: OpenAI / LMStudio を切り替え
- **接続テスト**: LLMへの疎通確認
- **保存**: 設定を `config.py` に反映

## 📖 使い方

1. トップページでGitHubリポジトリURLを入力
2. 出願人を入力
3. LLMプロバイダーを選択
4. 「🚀 明細書を生成」をクリック
5. 生成完了後、「📝 エディタで開く」でレビュー・コメント追加

---

## 💡 ChatGPT汎用プロンプト雛形：リポジトリ → 特許明細書(DOCX)＋図面(HTML)

```
あなたは弁理士補助エンジニアです。
以下の入力情報を基に、指定リポジトリを解析し、
(1) 日本特許庁(JPO)提出形式の特許明細書(DOCX)、
(2) 図面HTML(図1〜図3) を生成してください。

【入力】
- リポジトリURL: {{REPO_URL}}
- 出願人: {{APPLICANT}}（例: 株式会社〇〇）
- 出願国/庁: JP (JPO)
- クレーム方針: {{CLAIM_SCOPE}}（例: A=汎用システム／B=特定実装）
- 発明名称(任意): {{TITLE}}
- DOCXファイル名: {{DOCX_NAME}}（例: patent_spec_jpo.docx）
- HTMLファイル名: {{HTML_NAME}}（例: patent_figures.html）

【要件】
1. リポジトリを解析し、README・/docs・/src・設定ファイル等から技術要素を抽出する。
2. 機能構成・データフロー・主要モジュール・入出力・処理手順を整理する。
3. 特許明細書を日本特許庁形式で出力する（章立て下記）。
4. 図1〜図3を汎用的に表現したHTML図面を生成する。

【DOCX出力仕様】
- 章構成:
  1)【発明の名称】
  2)【技術分野】
  3)【背景技術】
  4)【発明が解決しようとする課題】
  5)【課題を解決するための手段】
  6)【発明の効果】
  7)【図面の簡単な説明】(図1〜図3)
  8)【発明を実施するための形態】(主要構成、処理手順、動作例など)
  9)【符号の説明】(101,102,103...)
  10)【特許請求の範囲】(請求項1〜N)
  11)【要約書】
  12)【出願人】{{APPLICANT}}
- 表現は日本特許庁の公報調に準じ、「〜を備える」「〜を特徴とする」で統一。
- クレーム方針に応じ、
  - A：汎用的なアルゴリズム・システム請求
  - B：特定の実装(例: モバイル・クラウド・IoT等)

【HTML図面出力仕様】
- 図1：システム構成図（主要モジュール・入出力・データフロー）
- 図2：処理シーケンス（イベント時系列・判断・出力）
- 図3：ユーザインタフェースやルール構成の概念図（設定UIや操作画面の例）
- CSS/スタイル込みの単一HTMLファイルとして出力。
- 凡例(符号リスト)・注記を含める。

【出力形式】
1. DOCXファイル：/mnt/data/{{DOCX_NAME}}
2. HTMLファイル：キャンバス（canmore.create_textdoc）として出力

【手順】
1. 指定リポジトリの主要構成・特徴を解析
2. 抽出情報を整理して特許明細書を生成
3. python_user_visibleでDOCXファイル生成
4. canmore.create_textdocでHTML図面生成
5. ユーザーにDOCXダウンロードリンクとHTML図面を提示

【出力例】
📘 DOCXファイルリンク: sandbox:/mnt/data/{{DOCX_NAME}}
🖼️ HTML図面キャンバス: (図1〜図3を含む)

開始してください。
```

---

このプロンプトをそのまま貼り付け、`{{REPO_URL}}`や`{{APPLICANT}}`などを埋めるだけで、ChatGPTが
リポジトリの解析からWord明細書生成、HTML図面出力まで自動実行できる汎用テンプレートになります。
