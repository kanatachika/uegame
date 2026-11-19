#!/usr/bin/env python3
"""Check for UE5 binary assets or large files committed without Git LFS."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# Threshold for any non-LFS tracked file (10 MB)
MAX_NON_LFS_BYTES = 10 * 1024 * 1024

# Binary asset extensions commonly used in UE5 projects that must be stored via Git LFS
LFS_REQUIRED_EXTENSIONS = {
    ".uasset",
    ".umap",
    ".fbx",
    ".obj",
    ".psd",
    ".wav",
    ".png",
    ".tga",
    ".exr",
    ".hdr",
    ".mp4",
    ".mov",
    ".blend",
    ".ogg",
    ".flac",
    ".mp3",
}

LFS_POINTER_PREFIX = b"version https://git-lfs.github.com/spec/v1"
LFS_POINTER_MAX_BYTES = 1024


def run_git(args: list[str], input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return result.stdout


def list_tracked_files() -> list[tuple[str, str]]:
    """Return list of (blob_oid, repo_relative_path) for tracked files in index."""
    raw = run_git(["ls-files", "-s", "-z"])
    entries: list[tuple[str, str]] = []
    for record in raw.split(b"\x00"):
        if not record:
            continue
        meta, _, path_bytes = record.partition(b"\t")
        if not path_bytes:
            continue
        parts = meta.decode("ascii").split()
        if len(parts) < 3:
            continue
        mode, oid = parts[0], parts[1]
        # Skip gitlinks / submodules (160000) and symlinks (120000)
        if mode in ("160000", "120000"):
            continue
        path = path_bytes.decode("utf-8", errors="surrogateescape")
        entries.append((oid, path))
    return entries


def get_blob_sizes(oids: list[str]) -> dict[str, int]:
    """Query Git object sizes in a single batch-check call."""
    if not oids:
        return {}
    unique_oids = list(dict.fromkeys(oids))
    stdin_data = ("\n".join(unique_oids) + "\n").encode("ascii")
    output = run_git(["cat-file", "--batch-check=%(objectname) %(objectsize)"], input_bytes=stdin_data)
    sizes: dict[str, int] = {}
    for line in output.decode("ascii").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].isdigit():
            sizes[parts[0]] = int(parts[1])
    return sizes


def is_lfs_pointer(oid: str, size: int) -> bool:
    """Return True if the Git blob is a valid Git LFS pointer."""
    if size == 0 or size > LFS_POINTER_MAX_BYTES:
        return False
    blob = run_git(["cat-file", "blob", oid])
    return blob.startswith(LFS_POINTER_PREFIX) and b"oid sha256:" in blob


def get_lfs_attr_map(paths: list[str]) -> dict[str, bool]:
    """Batch-query .gitattributes `filter` attribute for all paths."""
    if not paths:
        return {}
    stdin_data = b"\x00".join(p.encode("utf-8", errors="surrogateescape") for p in paths) + b"\x00"
    output = run_git(["check-attr", "--stdin", "-z", "filter"], input_bytes=stdin_data)
    fields = output.split(b"\x00")
    result: dict[str, bool] = {}
    # Each entry is 3 NUL-separated fields: <path>, "filter", <value>
    for i in range(0, len(fields) - 2, 3):
        p = fields[i].decode("utf-8", errors="surrogateescape")
        val = fields[i + 2].decode("utf-8", errors="replace")
        result[p] = val == "lfs"
    return result


def format_size(num_bytes: int) -> str:
    mb = num_bytes / (1024 * 1024)
    if mb >= 1:
        return f"{mb:.2f} MB"
    kb = num_bytes / 1024
    if kb >= 1:
        return f"{kb:.1f} KB"
    return f"{num_bytes} B"


def main() -> int:
    # Ensure we run from repo root
    repo_root = run_git(["rev-parse", "--show-toplevel"]).decode("utf-8").strip()
    os.chdir(repo_root)

    entries = list_tracked_files()
    if not entries:
        print("仓库当前没有已跟踪文件，跳过 LFS 与大文件检查。")
        return 0

    sizes = get_blob_sizes([oid for oid, _ in entries])
    lfs_attrs = get_lfs_attr_map([path for _, path in entries])

    missing_lfs_assets: list[tuple[str, int, bool]] = []
    oversized_files: list[tuple[str, int, bool]] = []

    for oid, path in entries:
        size = sizes.get(oid, 0)
        ext = Path(path).suffix.lower()
        configured = lfs_attrs.get(path, False)
        needs_lfs = configured or (ext in LFS_REQUIRED_EXTENSIONS)
        too_large = size > MAX_NON_LFS_BYTES

        if not needs_lfs and not too_large:
            continue

        if is_lfs_pointer(oid, size):
            continue

        if needs_lfs:
            missing_lfs_assets.append((path, size, configured))
        elif too_large:
            oversized_files.append((path, size, configured))

    if not missing_lfs_assets and not oversized_files:
        print(f"[OK] 已检查 {len(entries)} 个已跟踪文件，未发现漏配 LFS 的二进制资产或超限大文件。")
        return 0

    print("[FAIL] 检测到未走 Git LFS 的资产或超大文件：\n")

    if missing_lfs_assets:
        print("1) 以下 UE5 常见二进制资产没有通过 Git LFS 存储：")
        for path, size, configured in missing_lfs_assets:
            ext = Path(path).suffix.lower()
            reason = (
                ".gitattributes 已配置 LFS，但本地可能未执行 `git lfs install`"
                if configured
                else f".gitattributes 未配置 `{ext}` 的 LFS 规则"
            )
            print(f"   - {path} ({format_size(size)}) -> {reason}")
        print()

    if oversized_files:
        limit_str = format_size(MAX_NON_LFS_BYTES)
        print(f"2) 以下非 LFS 文件超过单个文件上限（{limit_str}）：")
        for path, size, configured in oversized_files:
            ext = Path(path).suffix.lower() or "(无后缀)"
            hint = (
                "已配置 LFS 但疑似漏跑 `git lfs install`"
                if configured
                else f"如需纳入版本管理，请为 `*{ext}` 启用 LFS，否则请移除或加入 .gitignore"
            )
            print(f"   - {path} ({format_size(size)}) -> {hint}")
        print()

    print("如何修复：")
    print("  1. 先在本机确认已安装并启用 Git LFS：")
    print("       git lfs install")
    print("  2. 如果该后缀尚未写入 .gitattributes，执行（以 .uasset 为例）：")
    print('       git lfs track "*.uasset"')
    print("       git add .gitattributes")
    print("  3. 把文件转为 LFS 存储：")
    print("     - 若尚未 push（推荐，连同本地提交一起清干净）：")
    print('       git lfs migrate import --include="*.uasset"')
    print("     - 若只想追加一次新提交转换当前文件（不改写历史）：")
    print("       git lfs migrate import --no-rewrite <文件路径>")
    print("  详细操作请看：docs/devops/git-lfs-guide.md")
    return 1


if __name__ == "__main__":
    sys.exit(main())
