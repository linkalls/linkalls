#!/usr/bin/env python3
"""
GitHubプロフィールREADMEのSVG画像URLに内容ハッシュを付ける。

同じパスのSVGを書き換えても、GitHubやブラウザの画像キャッシュによって
「Preparing...」の古い画像が表示され続けることがある。
生成したSVGのSHA-256先頭12桁をURLのクエリに付与し、
実際に画像の中身が変わった場合だけREADMEのURLを変更する。
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"

# この3つはGitHub Actionsが毎日生成するローカルSVG。
CARDS = {
    "profile/stats.svg",
    "profile/top-langs.svg",
    "profile/trophy.svg",
}

# URLはHTML imgのsrcやMarkdownの画像指定に含まれている。
# 既存の?v=ハッシュも一緒に置換して、更新のたびに連結しない。
IMAGE_URL = re.compile(
    r"(?P<prefix>\./)?"
    r"(?P<path>profile/(?:stats|top-langs|trophy)\.svg)"
    r"(?:\?v=[0-9a-f]{12})?"
)


def main() -> None:
    original = README.read_text(encoding="utf-8")
    seen: set[str] = set()

    def replace(match: re.Match[str]) -> str:
        relative_path = match.group("path")
        asset = ROOT / relative_path

        if not asset.is_file():
            raise FileNotFoundError(f"SVG not found: {relative_path}")

        seen.add(relative_path)
        digest = hashlib.sha256(asset.read_bytes()).hexdigest()[:12]
        prefix = match.group("prefix") or ""

        print(f"{relative_path}: cache version {digest}")
        return f"{prefix}{relative_path}?v={digest}"

    updated = IMAGE_URL.sub(replace, original)

    missing = CARDS - seen
    if missing:
        raise RuntimeError(f"Missing image references in README.md: {sorted(missing)}")

    if updated != original:
        README.write_text(updated, encoding="utf-8")
        print("README.md image URLs updated.")
    else:
        print("README.md already points to the latest image versions.")


if __name__ == "__main__":
    main()
