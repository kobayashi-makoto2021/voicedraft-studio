"""Firestore client wrapper."""

import firebase_admin
from firebase_admin import credentials, firestore
import os
from typing import Optional, Dict, Any, List


class FirestoreClient:
    """Firestore操作のラッパー"""

    def __init__(self):
        """初期化"""
        if not firebase_admin._apps:
            creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if creds_path:
                cred = credentials.Certificate(creds_path)
                firebase_admin.initialize_app(cred)
            else:
                firebase_admin.initialize_app()
        
        self.db = firestore.client()

    def get_tenant_settings(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """テナント設定を取得"""
        doc = self.db.collection("tenant_settings").document(tenant_id).get()
        return doc.to_dict() if doc.exists else None

    def create_draft(self, draft_id: str, data: Dict[str, Any]) -> None:
        """下書きを作成"""
        self.db.collection("drafts").document(draft_id).set(data)

    def get_draft(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """下書きを取得"""
        doc = self.db.collection("drafts").document(draft_id).get()
        return doc.to_dict() if doc.exists else None

    def list_drafts(self, tenant_id: str) -> List[Dict[str, Any]]:
        """下書き一覧を取得"""
        docs = self.db.collection("drafts").where("tenant_id", "==", tenant_id).stream()
        return [doc.to_dict() for doc in docs]

    def update_draft(self, draft_id: str, data: Dict[str, Any]) -> None:
        """下書きを更新"""
        self.db.collection("drafts").document(draft_id).update(data)

    def create_generated_text(self, text_id: str, data: Dict[str, Any]) -> None:
        """生成テキストを作成"""
        self.db.collection("generated_texts").document(text_id).set(data)

    def create_generated_image(self, image_id: str, data: Dict[str, Any]) -> None:
        """生成画像を作成"""
        self.db.collection("generated_images").document(image_id).set(data)
