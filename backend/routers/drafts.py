"""Drafts API routes."""

from fastapi import APIRouter, HTTPException
from typing import List
from models import DraftCreate, DraftResponse, ExtractPointsRequest

router = APIRouter()


@router.post("", response_model=DraftResponse)
async def create_draft(request: DraftCreate):
    """下書きを新規作成"""
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.get("", response_model=List[DraftResponse])
async def list_drafts(tenant_id: str = "aiaruku"):
    """下書き一覧取得"""
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.get("/{draft_id}", response_model=DraftResponse)
async def get_draft(draft_id: str, tenant_id: str = "aiaruku"):
    """下書き詳細取得"""
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.post("/{draft_id}/extract")
async def extract_points(draft_id: str, request: ExtractPointsRequest):
    """要点抽出を実行"""
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not Implemented")
