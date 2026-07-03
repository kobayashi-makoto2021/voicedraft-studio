"""Claude API client wrapper."""

import os
from anthropic import Anthropic

MODEL = "claude-sonnet-5"


def _first_text(message) -> str:
    for block in message.content:
        if block.type == "text":
            return block.text
    return ""


class ClaudeClient:
    """Claude APIの操作ラッパー"""

    MODEL = MODEL

    def __init__(self):
        """初期化"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = Anthropic(api_key=api_key)

    def _create(self, tag: str, prompt: str, max_tokens: int) -> str:
        print(f"[{tag}] Claude API request start model={MODEL} prompt_len={len(prompt)}")
        message = self.client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        print(f"[{tag}] Claude API response ok input_tokens={message.usage.input_tokens} output_tokens={message.usage.output_tokens}")
        return _first_text(message)

    def extract_points(self, raw_text: str, org_name: str, org_description: str) -> str:
        """要点を抽出"""
        prompt = f"""あなたは{org_name}のブログ・広報担当のアシスタントです。
以下は口述筆記された原文です。話し言葉特有の言い淀みや脱線を整理し、
箇条書きで要点を抽出してください。

# 出力形式
- 主題（1行）
- 要点（箇条書き、5〜8個）
- 印象的なエピソードや具体的な発言があれば、そのまま引用候補としてリストアップ

# 制約
- 原文にない内容を推測・補完で追加しない。整理はするが創作はしない

# 原文
{raw_text}"""

        return self._create("claude extract", prompt, max_tokens=1024)

    def generate_blog(self, extracted_points: str, org_name: str, org_description: str,
                     blog_tone: str, blog_cta: str) -> tuple[str, str]:
        """ブログ本文を生成。返り値: (title, body)"""
        prompt = f"""あなたはブログ記事を書くライターです。以下の要点をもとに、読みやすい
ブログ記事を作成してください。

# トーン
- {blog_tone}

# 構成
- タイトル
- 導入（1〜2段落）
- 本文（小見出しを使って読みやすく）
- まとめ（{blog_cta}）

# 制約（重要）
- **要点に含まれる内容だけで記事を構成する。** 原文にない出来事・エピソード・実績・数値・固有名詞を創作・追加しない
- 組織名・教室の種類・事業内容など、要点に書かれていない背景情報を勝手に書かない（例: 要点に「プログラミング教室」とないなら書かない）
- 話されていないことを推測で補完しない。膨らませるのは表現のみで、事実は足さない
- Markdownの表（テーブル記法）は使わない（ブログ側エディタが非対応のため。比較は箇条書きで表現する）

# 要点
{extracted_points}"""

        body = self._create("claude blog", prompt, max_tokens=2048)
        title = next(
            (line.lstrip("#").strip() for line in body.split("\n") if line.strip()),
            "Untitled",
        )
        return title, body

    def generate_crowdfunding(self, extracted_points: str, org_name: str,
                             crowdfunding_project_name: str, crowdfunding_background: str,
                             crowdfunding_notes: str) -> str:
        """クラファン本文を生成"""
        prompt = f"""あなたは{crowdfunding_project_name}のクラウドファンディング
担当です。
以下の要点をもとに、プロジェクトページに掲載する文章を作成してください。

# 注意事項
- {crowdfunding_background}
- {crowdfunding_notes}
- 支援者の共感を呼ぶストーリー性を重視

# 要点
{extracted_points}"""

        return self._create("claude crowdfunding", prompt, max_tokens=2048)

    def generate_image_prompt_draft(self, extracted_points: str, image_type: str,
                                    body_text: str | None = None) -> str:
        """画像生成用プロンプトのたたき台を生成"""
        if image_type == "slide":
            source = body_text or extracted_points
            prompt = f"""以下のブログ/クラファン本文をもとに、プレゼン資料の1枚（スライド）として使える画像を生成するためのプロンプトを日本語で1つ作ってください。

# スライドの構成
- 本文から、スライドに載せるタイトル（15文字以内）とキーフレーズ（各12文字以内、2〜3個）を選ぶ
- プロンプト内で「画像内テキスト:」として、入れる文字を一字一句そのまま指定する（画像生成AIは長い文字が崩れるため、必ず短く）
- 文字を主役に、内容を象徴するシンプルなモチーフ・図解を添える横長のレイアウトを記述する

# 制約
- スライドに載せる文字とモチーフは本文の内容から選ぶ。本文にない内容を創作しない
- 組織名・教室名・ブランド名・ロゴは入れない
- 特定の実在人物と分かる描写はしない
- 配色・画風の指定は書かない（複数枚をスタイル違いで生成するため、システム側で別途付与する）
- 出力はプロンプト本文のみ。前置き・説明・Markdown囲みは一切不要

# 本文
{source}"""
        else:
            prompt = f"""以下のブログ/クラファン本文の要点から、画像生成AIに渡すプロンプトを日本語で1つ作ってください。

# 画像タイプ
記事の情景を表現する挿絵。読者が場面を思い浮かべられる具体的なシーンを描く。

# 制約
- 記事の内容の情景・モチーフだけを描写する。本文にない内容を創作しない。組織名・教室名・ブランド名・ロゴは入れない
- 画像内に文字・テキスト・看板の文字は入れない（画像生成AIでは文字が崩れるため）
- 特定の実在人物と分かる描写はしない
- 配色・画風・スタイルの指定は書かない（複数枚をスタイル違いで生成するため、システム側で別途付与する）。情景・構図・モチーフのみ記述する
- 出力はプロンプト本文のみ。前置き・説明・Markdown囲みは一切不要

# 要点
{extracted_points}"""

        text = self._create("claude image-prompt", prompt, max_tokens=512).strip()
        # コードブロック囲みが付いてきた場合は除去する
        if text.startswith("```"):
            lines = [line for line in text.split("\n") if not line.strip().startswith("```")]
            text = "\n".join(lines).strip()
        return text
