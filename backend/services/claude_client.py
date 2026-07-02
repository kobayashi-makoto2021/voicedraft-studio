"""Claude API client wrapper."""

import os
from anthropic import Anthropic


class ClaudeClient:
    """Claude APIの操作ラッパー"""

    def __init__(self):
        """初期化"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = Anthropic(api_key=api_key)

    def extract_points(self, raw_text: str, org_name: str, org_description: str) -> str:
        """要点を抽出"""
        prompt = f"""あなたは{org_name}のブログ・広報担当のアシスタントです。
以下は口述筆記された原文です。話し言葉特有の言い淀みや脱線を整理し、
箇条書きで要点を抽出してください。

# 出力形式
- 主題（1行）
- 要点（箇条書き、5〜8個）
- 印象的なエピソードや具体的な発言があれば、そのまま引用候補としてリストアップ

# 原文
{raw_text}"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text

    def generate_blog(self, extracted_points: str, org_name: str, org_description: str,
                     blog_tone: str, blog_cta: str) -> tuple[str, str]:
        """ブログ本文を生成。返り値: (title, body)"""
        prompt = f"""あなたは{org_name}（{org_description}）の
ブログ記事を書くライターです。以下の要点をもとに、保護者が読みやすい
ブログ記事を作成してください。

# トーン
- {blog_tone}

# 構成
- タイトル
- 導入（1〜2段落）
- 本文（小見出しを使って読みやすく）
- まとめ（{blog_cta}）

# 要点
{extracted_points}"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        body = message.content[0].text
        # TODO: タイトル抽出ロジックを改善
        lines = body.split("\n")
        title = lines[0] if lines else "Untitled"
        
        return title, body

    def generate_crowdfunding(self, extracted_points: str, org_name: str,
                             crowdfunding_project_name: str, crowdfunding_background: str,
                             crowdfunding_notes: str) -> str:
        """クラファン本文を生成"""
        prompt = f"""あなたは{crowdfunding_project_name}のクラウドファンディング担当です。
以下の要点をもとに、プロジェクトページに掲載する文章を作成してください。

# 注意事項
- {crowdfunding_background}
- {crowdfunding_notes}
- 支援者の共感を呼ぶストーリー性を重視

# 要点
{extracted_points}"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text

    def generate_image_prompt_draft(self, extracted_points: str, image_type: str) -> str:
        """DALL-E用プロンプトのたたき台を生成"""
        prompt = f"""以下のブログ/クラファン本文の要点から、DALL-Eに渡す画像生成プロンプトの
たたき台を1つ作ってください。{image_type}（スライド風 or イメージ画像風）
に適した構図・雰囲気を英語で記述してください。

要点: {extracted_points}
画像タイプ: {image_type}"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
