"""Image generation API routes."""

from fastapi import APIRouter, HTTPException
from models import GenerateImageRequest, GeneratedImageResponse, ImagePromptDraftRequest, ImagePromptDraftResponse

router = APIRouter()


@router.post("/image/prompt-draft", response_model=ImagePromptDraftResponse)
async def generate_image_prompt_draft(request: ImagePromptDraftRequest):
    """画像生成プロンプトのたたき台を生成"""
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.post("/image", response_model=GeneratedImageResponse)
async def generate_image(request: GenerateImageRequest):
    """画像を生成"""
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not Implemented")
