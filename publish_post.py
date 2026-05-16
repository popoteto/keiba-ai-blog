"""
競馬AI ブログ自動投稿スクリプト
使い方: python publish_post.py <draft_md_path>
例:    python publish_post.py ../競馬AI/keibaAI-v2/keibaAI-v2-main/data/logs/20260516_blog_draft.md
"""
import sys
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

BLOG_DIR = Path(__file__).parent
POSTS_DIR = BLOG_DIR / "content" / "posts"


def convert_draft_to_post(draft_path: Path) -> Path:
    text = draft_path.read_text(encoding="utf-8")

    # ファイル名から日付を取得 (例: 20260516_blog_draft.md)
    date_match = re.search(r'(\d{8})', draft_path.name)
    if date_match:
        d = date_match.group(1)
        date_str = f"{d[:4]}-{d[4:6]}-{d[6:8]}"
    else:
        date_str = datetime.today().strftime('%Y-%m-%d')

    # タイトル抽出（最初の # 行）
    title_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "競馬AI予想結果"

    # 最初の # 見出しを削除（フロントマターにtitleとして入れるため）
    body = re.sub(r'^#\s+.+\n', '', text, count=1).strip()

    # フロントマター生成
    slug = draft_path.stem.replace('_blog_draft', '').replace('_', '-')
    frontmatter = f"""---
title: "{title}"
date: {date_str}
draft: false
tags: ["予想結果", "収支記録", "LightGBM"]
categories: ["週次レポート"]
description: "{title[:80]}"
---

"""

    out_path = POSTS_DIR / f"{slug}.md"
    out_path.write_text(frontmatter + body, encoding="utf-8")
    print(f"投稿ファイル作成: {out_path}")
    return out_path


def git_push(message: str):
    os.chdir(BLOG_DIR)
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("GitHubへpush完了。Cloudflare Pagesが自動デプロイします。")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python publish_post.py <draft_md_path>")
        sys.exit(1)

    draft = Path(sys.argv[1])
    if not draft.exists():
        print(f"ファイルが見つかりません: {draft}")
        sys.exit(1)

    post = convert_draft_to_post(draft)
    today = datetime.today().strftime('%Y/%m/%d')
    git_push(f"記事追加: {today} 競馬AI予想結果")
