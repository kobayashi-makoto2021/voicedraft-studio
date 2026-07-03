"""FastAPI main application."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import routers
try:
    from .routers import drafts, generate_text, generate_image
except ImportError:  # pragma: no cover - local dev fallback
    from routers import drafts, generate_text, generate_image

app = FastAPI(
    title="VoiceDraft Studio API",
    description="口述筆記からブログ・クラファン本文を自動生成するAPI",
    version="0.1.0"
)

# CORS設定（本番では ALLOWED_ORIGINS にフロントのURLをカンマ区切りで設定）
allowed_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 生成画像などの静的ファイル配信
static_dir = Path(__file__).resolve().parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ルーター登録
app.include_router(drafts.router, prefix="/drafts", tags=["drafts"])
app.include_router(generate_text.router, prefix="/generate", tags=["generate"])
app.include_router(generate_image.router, prefix="/generate", tags=["generate"])


@app.get("/")
async def root():
    """ヘルスチェック"""
    return {
        "message": "VoiceDraft Studio API",
        "status": "ok"
    }


@app.get("/health")
async def health():
    """ヘルスチェック（詳細）"""
    return {
        "status": "healthy",
        "anthropic_key": "✓" if os.getenv("ANTHROPIC_API_KEY") else "✗",
        "openai_key": "✓" if os.getenv("OPENAI_API_KEY") else "✗",
        "gcp_project_id": "✓" if os.getenv("GCP_PROJECT_ID") else "✗",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
