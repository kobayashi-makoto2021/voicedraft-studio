"""Drafts API routes."""

import os
import sys

import anthropic
from fastapi import APIRouter, HTTPException
from typing import List

try:
    from ..models import DraftCreate, DraftResponse, ExtractPointsRequest, GeneratedTextResponse
    from ..services.db_store import store
    from ..services.claude_client import ClaudeClient
except ImportError:  # pragma: no cover - local dev fallback
    from models import DraftCreate, DraftResponse, ExtractPointsRequest, GeneratedTextResponse
    from services.db_store import store
    from services.claude_client import ClaudeClient

router = APIRouter()


@router.post("", response_model=DraftResponse)
async def create_draft(request: DraftCreate):
    """下書きを新規作成"""
    draft = store.create_draft(
        raw_text=request.raw_text,
        author=request.author,
        tenant_id=request.tenant_id,
        tags=request.tags,
    )
    return DraftResponse(**draft)


@router.get("", response_model=List[DraftResponse])
def list_drafts(tenant_id: str = "aiaruku"):
    """下書き一覧取得"""
    drafts = store.list_drafts(tenant_id)
    return [DraftResponse(**draft) for draft in drafts]


@router.get("/{draft_id}", response_model=DraftResponse)
def get_draft(draft_id: str, tenant_id: str = "aiaruku"):
    """下書き詳細取得"""
    draft = store.get_draft(draft_id)
    if not draft or draft["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="draft not found")
    return DraftResponse(**draft)


@router.get("/{draft_id}/texts", response_model=List[GeneratedTextResponse])
def list_generated_texts(draft_id: str, tenant_id: str = "aiaruku"):
    """下書きに紐づく生成テキスト一覧（新しい順）。書庫からの再開用"""
    draft = store.get_draft(draft_id)
    if not draft or draft["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="draft not found")
    return [GeneratedTextResponse(**t) for t in store.list_generated_texts(draft_id)]


@router.post("/{draft_id}/extract")
async def extract_points(draft_id: str, request: ExtractPointsRequest):
    """要点抽出を実行 - Claude APIを使用"""
    draft = store.get_draft(draft_id)
    if not draft or draft["tenant_id"] != request.tenant_id:
        raise HTTPException(status_code=404, detail="draft not found")

    raw_text = draft["raw_text"]
    claude_client = ClaudeClient()
    try:
        points = claude_client.extract_points(
            raw_text=raw_text,
            org_name=os.getenv("ORG_NAME", "教育機関"),
            org_description=os.getenv("ORG_DESCRIPTION", "プログラミング教室"),
        )
    except anthropic.APIStatusError as e:
        print(f"[claude extract] Claude API error status={e.status_code} body={e.message}", file=sys.stderr)
        raise HTTPException(status_code=502, detail=f"Claude API error: {e.message}")

    store.update_draft(
        draft_id,
        {
            "extracted_points": points,
            "status": "extracted",
        },
    )
    return {"draft_id": draft_id, "extracted_points": points}
