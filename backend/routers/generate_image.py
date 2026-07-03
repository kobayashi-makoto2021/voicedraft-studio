"""Image generation API routes."""

import sys
from pathlib import Path
from uuid import uuid4

import anthropic
import openai
from fastapi import APIRouter, HTTPException

try:
    from ..models import (
        GenerateImageRequest,
        ImageCandidatesResponse,
        GeneratedImageResponse,
        ImagePromptDraftRequest,
        ImagePromptDraftResponse,
    )
    from ..services.in_memory_store import store
    from ..services.claude_client import ClaudeClient
    from ..services.dalle_client import DALLEClient
except ImportError:  # pragma: no cover - local dev fallback
    from models import (
        GenerateImageRequest,
        ImageCandidatesResponse,
        GeneratedImageResponse,
        ImagePromptDraftRequest,
        ImagePromptDraftResponse,
    )
    from services.in_memory_store import store
    from services.claude_client import ClaudeClient
    from services.dalle_client import DALLEClient

router = APIRouter()

# 生成画像の保存先（本番ではFirebase Storageに置き換え予定）
IMAGES_DIR = Path(__file__).resolve().parents[1] / "static" / "images"

# 複数枚生成時にそれぞれ違う雰囲気になるよう、1枚ごとに付与するスタイル指定
STYLE_VARIATIONS = {
    "slide": [
        "配色: 白基調のミニマルなデザイン。アクセントカラーは青系。",
        "配色: 濃紺の背景に明るいアクセントカラー。コントラストの強いデザイン。",
        "配色: 暖色系（オレンジ・クリーム色）の親しみやすいデザイン。",
    ],
    "illustration": [
        "画風: 温かみのあるフラットデザインのイラスト。",
        "画風: 水彩画風の柔らかいタッチのイラスト。",
        "画風: 明るい色彩の絵本風イラスト。",
    ],
}


@router.post("/image/prompt-draft", response_model=ImagePromptDraftResponse)
async def generate_image_prompt_draft(request: ImagePromptDraftRequest):
    """画像生成プロンプトのたたき台を生成 - Claude APIを使用"""
    claude_client = ClaudeClient()
    try:
        prompt = claude_client.generate_image_prompt_draft(
            extracted_points=request.extracted_points,
            image_type=request.image_type,
            body_text=request.body_text,
        )
    except anthropic.APIStatusError as e:
        print(f"[claude image-prompt] Claude API error status={e.status_code} body={e.message}", file=sys.stderr)
        raise HTTPException(status_code=502, detail=f"Claude API error: {e.message}")
    return ImagePromptDraftResponse(prompt=prompt)


@router.post("/image", response_model=ImageCandidatesResponse)
async def generate_image(request: GenerateImageRequest):
    """画像を生成 - OpenAI画像APIを使用し、静的ファイルとして永続化する。

    スライド風は横長サイズ、複数枚生成時は1枚ごとに違うスタイル指定を付与する。
    """
    dalle_client = DALLEClient()
    is_slide = request.image_type == "slide"
    size = "1536x1024" if is_slide else "1024x1024"
    # スライドは画像内に文字を入れるため、文字が崩れないようhigh画質を強制する
    quality = "high" if is_slide else None
    variations = STYLE_VARIATIONS.get(request.image_type, STYLE_VARIATIONS["illustration"])

    image_bytes_list = []
    try:
        for i in range(request.n):
            styled_prompt = f"{request.prompt}\n\n{variations[i % len(variations)]}"
            image_bytes_list.extend(
                dalle_client.generate_image(prompt=styled_prompt, size=size, n=1, quality=quality)
            )
    except openai.APIStatusError as e:
        print(f"[dalle generate] image API error status={e.status_code} body={e.message}", file=sys.stderr)
        raise HTTPException(status_code=502, detail=f"Image API error: {e.message}")

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    images = []
    for image_bytes in image_bytes_list:
        filename = f"{uuid4()}.png"
        (IMAGES_DIR / filename).write_bytes(image_bytes)
        print(f"[dalle save] saved static/images/{filename} ({len(image_bytes)} bytes)")

        generated = store.create_generated_image(
            draft_id=request.draft_id,
            text_id=request.text_id,
            image_type=request.image_type,
            prompt=request.prompt,
            image_url=f"/static/images/{filename}",
        )
        images.append(GeneratedImageResponse(**generated))

    return ImageCandidatesResponse(images=images)
