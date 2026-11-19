#!/usr/bin/env python3
"""Check local relative links and UTF-8 validity across all Markdown files."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

# Directories to skip when scanning Markdown files
SKIP_DIRS = {
    ".git",
    "Binaries",
    "DerivedDataCache",
    "Intermediate",
    "Saved",
    "node_modules",
    ".vs",
    ".idea",
}

EXTERNAL_SCHEMES = ("http://", "https://", "mailto:", "tel:", "data:", "javascript:", "ftp://")

# Match inline links/images: [label](target) or ![alt](target)
INLINE_LINK_RE = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
# Match reference link definitions: [ref]: target
REF_DEF_RE = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*(\S+)")
# Match inline code spans (`...`)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def iter_markdown_files(root: Path) -> list[Path]:
    md_files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if name.lower().endswith(".md"):
                md_files.append(Path(dirpath) / name)
    return md_files


def clean_target(raw_target: str) -> str:
    """Extract clean path from a markdown link destination."""
    target = raw_target.strip()
    if target.startswith("<"):
        end = target.find(">")
        if end != -1:
            target = target[1:end].strip()
    else:
        # Strip optional title: path/to/file.md "title" or 'title'
        parts = target.split(None, 1)
        if parts:
            target = parts[0].strip()
    return target


def strip_fenced_code_and_extract_links(text: str) -> list[tuple[int, str]]:
    """Return list of (1-based line_number, raw_target) outside code fences & inline code."""
    results: list[tuple[int, str]] = []
    in_fence = False
    fence_char = ""
    fence_len = 0

    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        fence_match = re.match(r"^(`{3,}|~{3,})", stripped)
        if fence_match:
            marker = fence_match.group(1)
            if not in_fence:
                in_fence = True
                fence_char = marker[0]
                fence_len = len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_len:
                in_fence = False
            continue

        if in_fence:
            continue

        # Remove inline code spans so examples like `[doc](foo.md)` are ignored
        scrubbed = INLINE_CODE_RE.sub("", line)

        for match in INLINE_LINK_RE.finditer(scrubbed):
            results.append((lineno, match.group(1)))

        ref_match = REF_DEF_RE.match(scrubbed)
        if ref_match:
            results.append((lineno, ref_match.group(1)))

    return results


def path_exists_exact_case(target: Path, repo_root: Path) -> bool:
    """Check existence and verify exact case even on case-insensitive OS (Windows)."""
    # Use os.path.normpath instead of Path.resolve() so Windows doesn't silently
    # rewrite the link's letter case to match the on-disk filename.
    norm_target = Path(os.path.normpath(str(target)))
    if not norm_target.exists():
        return False
    try:
        rel = norm_target.relative_to(repo_root)
    except ValueError:
        # Target points outside repository root
        return False

    cur = repo_root
    for part in rel.parts:
        try:
            entries = os.listdir(cur)
        except OSError:
            return False
        if part not in entries:
            return False
        cur = cur / part
    return True


def main() -> int:
    repo_root = Path.cwd().resolve()
    md_files = iter_markdown_files(repo_root)

    if not md_files:
        print("未找到任何 Markdown 文件。")
        return 0

    errors: list[str] = []
    checked_links = 0

    for md_path in md_files:
        rel_md = md_path.relative_to(repo_root).as_posix()
        try:
            content = md_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"{rel_md}: 不是合法的 UTF-8 编码 ({exc})")
            continue

        for lineno, raw_target in strip_fenced_code_and_extract_links(content):
            target = clean_target(raw_target)
            if not target or target.startswith("#"):
                continue
            lower_target = target.lower()
            if lower_target.startswith(EXTERNAL_SCHEMES):
                continue

            # Strip #anchor and ?query
            path_part = target.split("#", 1)[0].split("?", 1)[0]
            if not path_part:
                continue

            decoded_path = unquote(path_part)
            if decoded_path.startswith("/"):
                candidate = Path(os.path.normpath(str(repo_root / decoded_path.lstrip("/"))))
            else:
                candidate = Path(os.path.normpath(str(md_path.parent / decoded_path)))

            checked_links += 1

            # Ensure resolved target stays inside repo and exists with exact case
            try:
                candidate.relative_to(repo_root)
            except ValueError:
                errors.append(
                    f"{rel_md}:{lineno} -> 链接超出了仓库根目录范围：`{target}`"
                )
                continue

            if not path_exists_exact_case(candidate, repo_root):
                errors.append(
                    f"{rel_md}:{lineno} -> 找不到目标文件（或大小写不一致）：`{target}`"
                )

    if errors:
        print(f"[FAIL] 共扫描 {len(md_files)} 个 Markdown 文件，发现 {len(errors)} 处问题：\n")
        for err in errors:
            print(f"  - {err}")
        print("\n排查建议：")
        print("  1. 检查目标文件是否改名、移动，或路径层级（../）写错。")
        print("  2. GitHub Actions 运行在 Linux 上，文件名严格区分大小写（例如 README.md != readme.md）。")
        print("  3. 本地可直接运行 `python .github/scripts/check_md_links.py` 快速复查。")
        return 1

    print(
        f"[OK] 共扫描 {len(md_files)} 个 Markdown 文件，校验了 {checked_links} 个本地相对链接，全部有效。"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
