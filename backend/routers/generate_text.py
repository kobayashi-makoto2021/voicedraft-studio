"""Text generation API routes."""

from fastapi import APIRouter, HTTPException

try:
    from ..models import GenerateTextRequest, GeneratedTextResponse
    from ..services.in_memory_store import store
except ImportError:  # pragma: no cover - local dev fallback
    from models import GenerateTextRequest, GeneratedTextResponse
    from services.in_memory_store import store

router = APIRouter()


@router.post("/blog", response_model=GeneratedTextResponse)
async def generate_blog(request: GenerateTextRequest):
    """ブログ本文を生成"""
    draft = store.get_draft(request.draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="draft not found")

    title = "ブログ本文のひな形"
    body = f"# {title}\n\n{draft['raw_text']}"
    generated = store.create_generated_text(
        draft_id=request.draft_id,
        output_type=request.output_type,
        title=title,
        body=body,
        prompt_used="local-demo-prompt",
        model="local-demo",
    )
    store.update_draft(request.draft_id, {"status": "generated"})
    return GeneratedTextResponse(**generated)


@router.post("/crowdfunding", response_model=GeneratedTextResponse)
async def generate_crowdfunding(request: GenerateTextRequest):
    """クラファン本文を生成"""
    draft = store.get_draft(request.draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="draft not found")

    title = "クラファン本文のひな形"
    body = f"## {title}\n\n{draft['raw_text']}"
    generated = store.create_generated_text(
        draft_id=request.draft_id,
        output_type=request.output_type,
        title=title,
        body=body,
        prompt_used="local-demo-prompt",
        model="local-demo",
    )
    store.update_draft(request.draft_id, {"status": "generated"})
    return GeneratedTextResponse(**generated)
