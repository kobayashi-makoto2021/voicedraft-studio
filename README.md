# VoiceDraft Studio

アイアルク用の口述筆記からブログ・クラウドファンディング本文を自動生成するアプリケーション。

## 仕様書

[口述筆記アプリ_実装仕様書.md](./口述筆記アプリ_実装仕様書.md)

## プロジェクト構成

```
/
├── frontend/          # HTML + TypeScript
├── backend/           # FastAPI
├── .github/workflows/ # GitHub Actions
└── .env.example       # 環境変数テンプレート
```

## セットアップ

### バックエンド

```bash
# Python仮想環境の作成
python3 -m venv venv
source venv/bin/activate

# 依存パッケージのインストール
pip install -r backend/requirements.txt
```

### フロントエンド

```bash
# Node依存パッケージのインストール
cd frontend
npm install
```

## 開発サーバー起動

### バックエンド

```bash
source venv/bin/activate
cd backend
uvicorn main:app --reload --port 8000
```

### フロントエンド

```bash
cd frontend
npm run dev
```

## 環境変数

`.env.example` を参考に `.env` ファイルを作成してください。

- `ANTHROPIC_API_KEY`: Claude API キー
- `OPENAI_API_KEY`: OpenAI API キー（DALL-E用）
- `GCP_PROJECT_ID`: Google Cloud プロジェクト ID
- `GOOGLE_APPLICATION_CREDENTIALS`: Firestore認証ファイルのパス
