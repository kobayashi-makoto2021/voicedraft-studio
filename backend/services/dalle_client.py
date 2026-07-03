"""OpenAI image generation API client wrapper (DALL-E後継のgpt-image系)."""

import base64
import os
from openai import OpenAI


class DALLEClient:
    """OpenAI画像生成APIの操作ラッパー"""

    def __init__(self):
        """初期化"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("IMAGE_MODEL", "gpt-image-2")
        self.quality = os.getenv("IMAGE_QUALITY", "medium")  # low / medium / high

    def generate_image(self, prompt: str, size: str = "1024x1024", n: int = 1,
                       quality: str | None = None) -> list[bytes]:
        """画像を生成して、PNGバイト列のリストを返す（base64で受け取るため失効URLの問題なし）"""
        quality = quality or self.quality
        print(f"[dalle generate] request start model={self.model} quality={quality} size={size} n={n} prompt_len={len(prompt)}")
        response = self.client.images.generate(
            model=self.model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=n,
        )
        print(f"[dalle generate] response ok images={len(response.data)}")
        return [base64.b64decode(img.b64_json) for img in response.data]
