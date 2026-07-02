"""DALL-E API client wrapper."""

import os
from openai import OpenAI


class DALLEClient:
    """DALL-E APIの操作ラッパー"""

    def __init__(self):
        """初期化"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=api_key)

    def generate_image(self, prompt: str, size: str = "1024x1024", n: int = 1) -> list[str]:
        """画像を生成して、URLリストを返す"""
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="standard",
            n=n
        )
        return [img.url for img in response.data]
