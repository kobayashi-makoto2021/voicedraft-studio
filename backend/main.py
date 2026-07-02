"""FastAPI main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では制限すること
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
