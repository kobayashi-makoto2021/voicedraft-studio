"""Simple in-memory persistence for local development."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


class InMemoryStore:
    def __init__(self) -> None:
        self._drafts: Dict[str, Dict[str, Any]] = {}
        self._generated_texts: Dict[str, Dict[str, Any]] = {}
        self._generated_images: Dict[str, Dict[str, Any]] = {}

    def create_draft(self, raw_text: str, author: str, tenant_id: str, tags: Optional[List[str]]) -> Dict[str, Any]:
        draft_id = str(uuid4())
        now = datetime.now(timezone.utc)
        draft = {
            "draft_id": draft_id,
            "tenant_id": tenant_id,
            "author": author,
            "raw_text": raw_text,
            "extracted_points": None,
            "created_at": now,
            "updated_at": now,
            "status": "draft",
            "tags": tags or [],
        }
        self._drafts[draft_id] = draft
        return draft

    def list_drafts(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [draft for draft in self._drafts.values() if draft["tenant_id"] == tenant_id]

    def get_draft(self, draft_id: str) -> Optional[Dict[str, Any]]:
        return self._drafts.get(draft_id)

    def update_draft(self, draft_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        draft = self._drafts.get(draft_id)
        if not draft:
            return None
        draft.update(updates)
        draft["updated_at"] = datetime.now(timezone.utc)
        return draft

    def create_generated_text(self, draft_id: str, output_type: str, title: str, body: str, prompt_used: str, model: str) -> Dict[str, Any]:
        text_id = str(uuid4())
        now = datetime.now(timezone.utc)
        generated = {
            "text_id": text_id,
            "draft_id": draft_id,
            "output_type": output_type,
            "title": title,
            "body": body,
            "prompt_used": prompt_used,
            "model": model,
            "created_at": now,
            "edited_body": None,
        }
        self._generated_texts[text_id] = generated
        return generated

    def create_generated_image(self, draft_id: Optional[str], text_id: Optional[str], image_type: str, prompt: str, image_url: str) -> Dict[str, Any]:
        image_id = str(uuid4())
        now = datetime.now(timezone.utc)
        generated = {
            "image_id": image_id,
            "draft_id": draft_id,
            "text_id": text_id,
            "image_type": image_type,
            "prompt": prompt,
            "image_url": image_url,
            "created_at": now,
        }
        self._generated_images[image_id] = generated
        return generated


store = InMemoryStore()
