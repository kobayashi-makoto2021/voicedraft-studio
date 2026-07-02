"""Drafts API routes."""

from fastapi import APIRouter, HTTPException
from typing import List

try:
    from ..models import DraftCreate, DraftResponse, ExtractPointsRequest
    from ..services.in_memory_store import store
except ImportError:  # pragma: no cover - local dev fallback
    from models import DraftCreate, DraftResponse, ExtractPointsRequest
    from services.in_memory_store import store

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
async def list_drafts(tenant_id: str = "aiaruku"):
    """下書き一覧取得"""
    drafts = store.list_drafts(tenant_id)
    return [DraftResponse(**draft) for draft in drafts]


@router.get("/{draft_id}", response_model=DraftResponse)
async def get_draft(draft_id: str, tenant_id: str = "aiaruku"):
    """下書き詳細取得"""
    draft = store.get_draft(draft_id)
    if not draft or draft["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="draft not found")
    return DraftResponse(**draft)


@router.post("/{draft_id}/extract")
async def extract_points(draft_id: str, request: ExtractPointsRequest):
    """要点抽出を実行"""
    draft = store.get_draft(draft_id)
    if not draft or draft["tenant_id"] != request.tenant_id:
        raise HTTPException(status_code=404, detail="draft not found")

    raw_text = draft["raw_text"]
    points = [
        "- 主題: " + (raw_text.splitlines()[0] if raw_text.splitlines() else "口述内容"),
        "- 要点: 1. 伝えたい内容を整理する",
        "- 要点: 2. 具体例を添えて説明する",
        "- 要点: 3. まとめを明確に伝える",
    ]
    store.update_draft(
        draft_id,
        {
            "extracted_points": "\n".join(points),
            "status": "extracted",
        },
    )
    return {"draft_id": draft_id, "extracted_points": "\n".join(points)}
