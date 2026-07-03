"""Pydantic models for API requests/responses."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class DraftCreate(BaseModel):
    """リクエスト: 下書き作成"""
    raw_text: str
    author: str = "unknown"
    tenant_id: str = "aiaruku"
    tags: Optional[List[str]] = None


class DraftResponse(BaseModel):
    """レスポンス: 下書き詳細"""
    draft_id: str
    tenant_id: str
    author: str
    raw_text: str
    extracted_points: Optional[str] = None
    status: str
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime


class ExtractPointsRequest(BaseModel):
    """リクエスト: 要点抽出実行"""
    draft_id: str
    tenant_id: str = "aiaruku"


class GenerateTextRequest(BaseModel):
    """リクエスト: テキスト生成"""
    draft_id: str
    output_type: str  # "blog" or "crowdfunding"
    tenant_id: str = "aiaruku"


class GeneratedTextResponse(BaseModel):
    """レスポンス: 生成テキスト"""
    text_id: str
    draft_id: str
    output_type: str
    title: str
    body: str
    prompt_used: str
    model: str
    created_at: datetime
    edited_body: Optional[str] = None


class ImagePromptDraftRequest(BaseModel):
    """リクエスト: 画像生成プロンプトのたたき台"""
    extracted_points: str
    image_type: str  # "slide" or "illustration"
    tenant_id: str = "aiaruku"
    body_text: Optional[str] = None  # 生成済み本文（スライド生成時に文字を取り込むため）


class ImagePromptDraftResponse(BaseModel):
    """レスポンス: 画像生成プロンプトのたたき台"""
    prompt: str


class GenerateImageRequest(BaseModel):
    """リクエスト: 画像生成"""
    prompt: str
    image_type: str  # "slide" or "illustration"
    draft_id: Optional[str] = None
    text_id: Optional[str] = None
    tenant_id: str = "aiaruku"
    n: int = Field(default=3, ge=1, le=4)  # 生成枚数（グリッド表示して選択）


class GeneratedImageResponse(BaseModel):
    """レスポンス: 生成画像"""
    image_id: str
    draft_id: Optional[str] = None
    text_id: Optional[str] = None
    image_type: str
    prompt: str
    image_url: str
    created_at: datetime


class ImageCandidatesResponse(BaseModel):
    """レスポンス: 生成画像の候補一覧（グリッド表示用）"""
    images: List[GeneratedImageResponse]
