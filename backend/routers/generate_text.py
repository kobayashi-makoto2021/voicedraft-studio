"""Text generation API routes."""

from fastapi import APIRouter, HTTPException
from models import GenerateTextRequest, GeneratedTextResponse

router = APIRouter()


@router.post("/blog", response_model=GeneratedTextResponse)
async def generate_blog(request: GenerateTextRequest):
    """ブログ本文を生成"""
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.post("/crowdfunding", response_model=GeneratedTextResponse)
async def generate_crowdfunding(request: GenerateTextRequest):
    """クラファン本文を生成"""
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not Implemented")
