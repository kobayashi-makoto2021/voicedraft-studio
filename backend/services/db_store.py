"""SQLite-backed persistence (local development). 本番はFirestoreに置き換える。"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "voicedraft.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS drafts (
    draft_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    author TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    extracted_points TEXT,
    status TEXT NOT NULL,
    tags TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS generated_texts (
    text_id TEXT PRIMARY KEY,
    draft_id TEXT NOT NULL,
    output_type TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    prompt_used TEXT NOT NULL,
    model TEXT NOT NULL,
    created_at TEXT NOT NULL,
    edited_body TEXT
);
CREATE TABLE IF NOT EXISTS generated_images (
    image_id TEXT PRIMARY KEY,
    draft_id TEXT,
    text_id TEXT,
    image_type TEXT NOT NULL,
    prompt TEXT NOT NULL,
    image_url TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SQLiteStore:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _draft_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        draft = dict(row)
        draft["tags"] = json.loads(draft["tags"])
        return draft

    def create_draft(self, raw_text: str, author: str, tenant_id: str, tags: Optional[List[str]]) -> Dict[str, Any]:
        draft = {
            "draft_id": str(uuid4()),
            "tenant_id": tenant_id,
            "author": author,
            "raw_text": raw_text,
            "extracted_points": None,
            "status": "draft",
            "tags": tags or [],
            "created_at": _now(),
            "updated_at": _now(),
        }
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO drafts VALUES (:draft_id, :tenant_id, :author, :raw_text, :extracted_points, :status, :tags_json, :created_at, :updated_at)",
                {**draft, "tags_json": json.dumps(draft["tags"], ensure_ascii=False)},
            )
        return draft

    def list_drafts(self, tenant_id: str) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM drafts WHERE tenant_id = ? ORDER BY updated_at DESC", (tenant_id,)
            ).fetchall()
        return [self._draft_to_dict(row) for row in rows]

    def get_draft(self, draft_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)).fetchone()
        return self._draft_to_dict(row) if row else None

    def update_draft(self, draft_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        allowed = {"raw_text", "extracted_points", "status", "tags"}
        fields = {k: v for k, v in updates.items() if k in allowed}
        if "tags" in fields:
            fields["tags"] = json.dumps(fields["tags"], ensure_ascii=False)
        if not fields:
            return self.get_draft(draft_id)
        fields["updated_at"] = _now()
        set_clause = ", ".join(f"{k} = :{k}" for k in fields)
        with self._connect() as conn:
            conn.execute(f"UPDATE drafts SET {set_clause} WHERE draft_id = :draft_id", {**fields, "draft_id": draft_id})
        return self.get_draft(draft_id)

    def create_generated_text(self, draft_id: str, output_type: str, title: str, body: str,
                              prompt_used: str, model: str) -> Dict[str, Any]:
        generated = {
            "text_id": str(uuid4()),
            "draft_id": draft_id,
            "output_type": output_type,
            "title": title,
            "body": body,
            "prompt_used": prompt_used,
            "model": model,
            "created_at": _now(),
            "edited_body": None,
        }
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO generated_texts VALUES (:text_id, :draft_id, :output_type, :title, :body, :prompt_used, :model, :created_at, :edited_body)",
                generated,
            )
        return generated

    def list_generated_texts(self, draft_id: str) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM generated_texts WHERE draft_id = ? ORDER BY created_at DESC", (draft_id,)
            ).fetchall()
        return [dict(row) for row in rows]

    def create_generated_image(self, draft_id: Optional[str], text_id: Optional[str], image_type: str,
                               prompt: str, image_url: str) -> Dict[str, Any]:
        generated = {
            "image_id": str(uuid4()),
            "draft_id": draft_id,
            "text_id": text_id,
            "image_type": image_type,
            "prompt": prompt,
            "image_url": image_url,
            "created_at": _now(),
        }
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO generated_images VALUES (:image_id, :draft_id, :text_id, :image_type, :prompt, :image_url, :created_at)",
                generated,
            )
        return generated

    def list_generated_images(self, draft_id: str) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM generated_images WHERE draft_id = ? ORDER BY created_at DESC", (draft_id,)
            ).fetchall()
        return [dict(row) for row in rows]


store = SQLiteStore()
