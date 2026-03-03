
# tokkyon データベース設計仕様書 v2

**作成日:** 2026年3月3日
**作成者:** Manus AI

## 1. 概要

本ドキュメントは、特許管理システム「tokkyon」のデータベース設計を定義するものです。
今までのやり取りを踏まえ、フィールドの整理と具体値の定義を行いました。

## 2. ER図

![ER図 v2](/home/ubuntu/tokkyon_er_v2.png)

## 3. テーブル定義

### 3.1. users （ユーザー）

ユーザー情報を管理します。

| 論理名 | 物理名 | データ型 | NOT NULL | 主キー | 外部キー | 説明 |
|---|---|---|---|---|---|---|
| ID | `id` | UUID | ✔ | ✔ | | ユーザーの一意なID |
| メールアドレス | `email` | VARCHAR | ✔ | | | ログインに使用 |
| パスワード（ハッシュ） | `password` | VARCHAR | ✔ | | | ハッシュ化して保存 |
| 氏名 | `full_name` | VARCHAR | ✔ | | | ユーザーの氏名 |
| ロール | `role` | ENUM | ✔ | | | `admin` / `attorney` / `client` のいずれか |
| 作成日時 | `created_at` | DATETIME | ✔ | | | ユーザーの作成日時 |
| 最終ログイン日時 | `last_login_at` | DATETIME | | | | 最終ログイン日時 |

### 3.2. projects （案件）

特許案件の情報を管理します。全ての情報のハブとなります。

| 論理名 | 物理名 | データ型 | NOT NULL | 主キー | 外部キー | 説明 |
|---|---|---|---|---|---|---|
| ID | `id` | UUID | ✔ | ✔ | | 案件の一意なID |
| 担当者ID | `user_id` | UUID | ✔ | | `users(id)` | この案件の担当者 |
| GitHubリポジトリURL | `github_repo_url` | VARCHAR | ✔ | | | 案件の中心となるリポジトリ |
| 顧客社名 | `client_name` | VARCHAR | ✔ | | | 依頼者の会社名（当面はとろたく） |
| ステータス | `status` | ENUM | ✔ | | | `draft` / `in_review` / `submitted` / `completed` |
| 作成日時 | `created_at` | DATETIME | ✔ | | | 案件の作成日時 |
| 最終更新日時 | `updated_at` | DATETIME | ✔ | | | 案件の最終更新日時 |

### 3.3. patent_drafts （明細書）

明細書のバージョンと内容を管理します。

| 論理名 | 物理名 | データ型 | NOT NULL | 主キー | 外部キー | 説明 |
|---|---|---|---|---|---|---|
| ID | `id` | UUID | ✔ | ✔ | | 明細書の一意なID |
| 案件ID | `project_id` | UUID | ✔ | | `projects(id)` | 紐づく案件 |
| バージョン番号 | `version` | INTEGER | ✔ | | | v1, v2, v3... |
| 生成方法 | `generated_by` | ENUM | ✔ | | | `ai` / `manual` |
| 明細書本文 | `content` | TEXT | ✔ | | | HTML形式で保存 |
| 作成日時 | `created_at` | DATETIME | ✔ | | | このバージョンの作成日時 |

### 3.4. comments （コメント）

明細書へのコメントと返信を管理します。

| 論理名 | 物理名 | データ型 | NOT NULL | 主キー | 外部キー | 説明 |
|---|---|---|---|---|---|---|
| ID | `id` | UUID | ✔ | ✔ | | コメントの一意なID |
| 明細書ID | `patent_draft_id` | UUID | ✔ | | `patent_drafts(id)` | 紐づく明細書 |
| 投稿者ユーザーID | `user_id` | UUID | ✔ | | `users(id)` | コメントした人 |
| 親コメントID | `parent_comment_id` | UUID | | | `comments(id)` | 返信の場合、親コメントのID |
| コメント本文 | `text` | TEXT | ✔ | | | コメント内容 |
| 選択テキスト | `selected_text` | TEXT | | | | コメント対象の文章 |
| 選択開始位置 | `selection_start` | INTEGER | | | | コメント対象の開始位置 |
| 選択終了位置 | `selection_end` | INTEGER | | | | コメント対象の終了位置 |
| 解決済みフラグ | `resolved` | BOOLEAN | ✔ | | | このコメントが解決済みか |
| 作成日時 | `created_at` | DATETIME | ✔ | | | コメントの作成日時 |

### 3.5. hearing_sheets （ヒアリングシート）

ヒアリング内容を管理します。

| 論理名 | 物理名 | データ型 | NOT NULL | 主キー | 外部キー | 説明 |
|---|---|---|---|---|---|---|
| ID | `id` | UUID | ✔ | ✔ | | ヒアリングシートの一意なID |
| 案件ID | `project_id` | UUID | ✔ | | `projects(id)` | 紐づく案件 |
| 特許登名 | `patent_name` | VARCHAR | | | | 発明の名称 |
| 解決したい課題 | `problem_to_solve` | TEXT | | | | |
| 従来技術の問題点 | `problem_of_prior_art` | TEXT | | | | |
| 特許的組成（手順） | `composition` | TEXT | | | | |
| 特許的特質 | `features` | TEXT | | | | |
| 特定行時 | `timing` | DATETIME | | | | |
| 最終更新日時 | `updated_at` | DATETIME | ✔ | | | |

### 3.6. files （添付ファイル）

案件に紐づくファイルを管理します。

| 論理名 | 物理名 | データ型 | NOT NULL | 主キー | 外部キー | 説明 |
|---|---|---|---|---|---|---|
| ID | `id` | UUID | ✔ | ✔ | | ファイルの一意なID |
| 案件ID | `project_id` | UUID | ✔ | | `projects(id)` | 紐づく案件 |
| ファイル名 | `file_name` | VARCHAR | ✔ | | | |
| ファイルURL | `file_url` | VARCHAR | ✔ | | | S3などのURL |
| 種別 | `type` | ENUM | ✔ | | | `reference` / `drawing` など |
| 作成日時 | `created_at` | DATETIME | ✔ | | | |

