"""Image generation API routes."""

from fastapi import APIRouter

try:
    from ..models import GenerateImageRequest, GeneratedImageResponse, ImagePromptDraftRequest, ImagePromptDraftResponse
    from ..services.in_memory_store import store
except ImportError:  # pragma: no cover - local dev fallback
    from models import GenerateImageRequest, GeneratedImageResponse, ImagePromptDraftRequest, ImagePromptDraftResponse
    from services.in_memory_store import store

router = APIRouter()


@router.post("/image/prompt-draft", response_model=ImagePromptDraftResponse)
async def generate_image_prompt_draft(request: ImagePromptDraftRequest):
    """画像生成プロンプトのたたき台を生成"""
    prompt = f"A polished {request.image_type} illustration inspired by: {request.extracted_points[:200]}"
    return ImagePromptDraftResponse(prompt=prompt)


@router.post("/image", response_model=GeneratedImageResponse)
async def generate_image(request: GenerateImageRequest):
    """画像を生成"""
    generated = store.create_generated_image(
        draft_id=request.draft_id,
        text_id=request.text_id,
        image_type=request.image_type,
        prompt=request.prompt,
        image_url="https://placehold.co/1024x1024/png?text=VoiceDraft+Studio",
    )
    return GeneratedImageResponse(**generated)
