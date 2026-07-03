"""Text generation API routes."""

import os
import sys

import anthropic
from fastapi import APIRouter, HTTPException

try:
    from ..models import GenerateTextRequest, GeneratedTextResponse
    from ..services.db_store import store
    from ..services.claude_client import ClaudeClient, MODEL
except ImportError:  # pragma: no cover - local dev fallback
    from models import GenerateTextRequest, GeneratedTextResponse
    from services.db_store import store
    from services.claude_client import ClaudeClient, MODEL

router = APIRouter()


@router.post("/blog", response_model=GeneratedTextResponse)
async def generate_blog(request: GenerateTextRequest):
    """ブログ本文を生成 - Claude APIを使用"""
    draft = store.get_draft(request.draft_id)
    if not draft or draft["tenant_id"] != request.tenant_id:
        raise HTTPException(status_code=404, detail="draft not found")

    extracted_points = draft.get("extracted_points", draft["raw_text"])
    claude_client = ClaudeClient()
    try:
        title, body = claude_client.generate_blog(
            extracted_points=extracted_points,
            org_name=os.getenv("ORG_NAME", "教育機関"),
            org_description=os.getenv("ORG_DESCRIPTION", "プログラミング教室"),
            blog_tone=os.getenv("BLOG_TONE", "フレンドリーで親しみやすい"),
            blog_cta=os.getenv("BLOG_CTA", "ぜひお気軽にお問い合わせください"),
        )
    except anthropic.APIStatusError as e:
        print(f"[claude blog] Claude API error status={e.status_code} body={e.message}", file=sys.stderr)
        raise HTTPException(status_code=502, detail=f"Claude API error: {e.message}")

    generated = store.create_generated_text(
        draft_id=request.draft_id,
        output_type=request.output_type,
        title=title,
        body=body,
        prompt_used=MODEL,
        model=MODEL,
    )
    store.update_draft(request.draft_id, {"status": "generated"})
    return GeneratedTextResponse(**generated)


@router.post("/crowdfunding", response_model=GeneratedTextResponse)
async def generate_crowdfunding(request: GenerateTextRequest):
    """クラファン本文を生成 - Claude APIを使用"""
    draft = store.get_draft(request.draft_id)
    if not draft or draft["tenant_id"] != request.tenant_id:
        raise HTTPException(status_code=404, detail="draft not found")

    extracted_points = draft.get("extracted_points", draft["raw_text"])
    claude_client = ClaudeClient()
    try:
        body = claude_client.generate_crowdfunding(
            extracted_points=extracted_points,
            org_name=os.getenv("ORG_NAME", "教育機関"),
            crowdfunding_project_name=os.getenv("CF_PROJECT_NAME", "プログラミング教室プロジェクト"),
            crowdfunding_background=os.getenv("CF_BACKGROUND", "子どもたちの学習支援"),
            crowdfunding_notes=os.getenv("CF_NOTES", "クラウドファンディングで支援してください"),
        )
    except anthropic.APIStatusError as e:
        print(f"[claude crowdfunding] Claude API error status={e.status_code} body={e.message}", file=sys.stderr)
        raise HTTPException(status_code=502, detail=f"Claude API error: {e.message}")

    generated = store.create_generated_text(
        draft_id=request.draft_id,
        output_type=request.output_type,
        title=os.getenv("CF_PROJECT_NAME", "プログラミング教室プロジェクト"),
        body=body,
        prompt_used=MODEL,
        model=MODEL,
    )
    store.update_draft(request.draft_id, {"status": "generated"})
    return GeneratedTextResponse(**generated)
