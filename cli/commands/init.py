import argparse
import json
import shutil
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

REPO = "AmethystDev-Labs/LazyFox"
API_BASE = f"https://api.github.com/repos/{REPO}"
REPO_URL = f"https://github.com/{REPO}"


def run(args: argparse.Namespace) -> int:
    version = args.version or "latest"
    dest = Path(args.dest).resolve()
    dest.mkdir(parents=True, exist_ok=True)

    try:
        source = _resolve_source(version)
    except RuntimeError as exc:
        print(f"[init] 获取下载源失败: {exc}")
        return 1

    tag = source.get("tag_name") or version
    zip_url = source.get("zipball_url")
    source_type = source.get("source_type", "unknown")
    if not zip_url:
        print("[init] 下载源缺少 zipball_url，无法下载源码。")
        return 1

    print(f"[init] 仓库: {REPO_URL}")
    print(f"[init] 来源: {source_type}")
    print(f"[init] 版本: {tag}")
    print(f"[init] 目标目录: {dest}")

    try:
        _download_and_extract(zip_url=zip_url, dest=dest, force=args.force)
    except RuntimeError as exc:
        print(f"[init] 初始化失败: {exc}")
        return 1

    print("[init] 完成。")
    return 0


def _api_get(url: str) -> dict | list:
    request = urllib.request.Request(url, headers=_headers())
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code}: {_read_error(exc)}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(str(exc.reason)) from exc


def _resolve_source(version: str) -> dict:
    if version == "latest":
        try:
            release = _api_get(f"{API_BASE}/releases/latest")
            if isinstance(release, dict) and release.get("zipball_url"):
                return {
                    "source_type": "latest release",
                    "tag_name": release.get("tag_name") or "latest",
                    "zipball_url": release["zipball_url"],
                }
        except RuntimeError as exc:
            if "HTTP 404" not in str(exc):
                raise

        tags = _api_get(f"{API_BASE}/tags?per_page=1")
        if isinstance(tags, list) and tags:
            first = tags[0]
            return {
                "source_type": "latest tag",
                "tag_name": first.get("name") or "latest-tag",
                "zipball_url": first.get("zipball_url"),
            }

        return _default_branch_source()

    try:
        release = _api_get(f"{API_BASE}/releases/tags/{version}")
        if isinstance(release, dict) and release.get("zipball_url"):
            return {
                "source_type": "release tag",
                "tag_name": release.get("tag_name") or version,
                "zipball_url": release["zipball_url"],
            }
    except RuntimeError as exc:
        if "HTTP 404" not in str(exc):
            raise

    tags = _api_get(f"{API_BASE}/tags?per_page=100")
    if isinstance(tags, list):
        for item in tags:
            if item.get("name") == version:
                return {
                    "source_type": "git tag",
                    "tag_name": version,
                    "zipball_url": item.get("zipball_url"),
                }

    raise RuntimeError(f"未找到版本 `{version}` 的 release 或 tag。")


def _default_branch_source() -> dict:
    repo = _api_get(API_BASE)
    if not isinstance(repo, dict):
        raise RuntimeError("仓库信息格式异常。")
    branch = repo.get("default_branch")
    if not branch:
        raise RuntimeError("仓库没有默认分支信息。")
    return {
        "source_type": f"default branch ({branch})",
        "tag_name": branch,
        "zipball_url": f"{REPO_URL}/archive/refs/heads/{branch}.zip",
    }


def _read_error(error: urllib.error.HTTPError) -> str:
    try:
        return error.read().decode("utf-8", errors="ignore")
    except Exception:
        return error.reason if hasattr(error, "reason") else "unknown error"


def _headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "User-Agent": "LazyFox-CLI",
    }


def _download_and_extract(zip_url: str, dest: Path, force: bool) -> None:
    with tempfile.TemporaryDirectory(prefix="lazyfox-init-") as tmp_dir:
        zip_path = Path(tmp_dir) / "source.zip"
        _download_file(zip_url, zip_path)

        with zipfile.ZipFile(zip_path, "r") as archive:
            root_name = _detect_root_folder(archive)
            archive.extractall(tmp_dir)

        source_root = Path(tmp_dir) / root_name
        if not source_root.exists():
            raise RuntimeError("解压后未找到源码目录。")

        _copy_tree(source_root, dest, force=force)


def _download_file(url: str, output_path: Path) -> None:
    request = urllib.request.Request(url, headers=_headers())
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            with output_path.open("wb") as file:
                shutil.copyfileobj(response, file)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"下载失败 HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"下载失败: {exc.reason}") from exc


def _detect_root_folder(archive: zipfile.ZipFile) -> str:
    names = [name for name in archive.namelist() if name and not name.startswith("__MACOSX/")]
    if not names:
        raise RuntimeError("压缩包为空。")
    return names[0].split("/", 1)[0]


def _copy_tree(source_root: Path, dest: Path, force: bool) -> None:
    conflicts: list[Path] = []
    for source in source_root.rglob("*"):
        relative = source.relative_to(source_root)
        target = dest / relative

        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue

        if target.exists() and not force:
            conflicts.append(relative)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    if conflicts:
        preview = "\n".join(f"  - {item}" for item in conflicts[:20])
        more = "" if len(conflicts) <= 20 else f"\n  ... 还有 {len(conflicts) - 20} 个冲突文件"
        raise RuntimeError(
            "目标目录存在同名文件，已停止写入。可使用 --force 覆盖。\n"
            f"冲突文件示例:\n{preview}{more}"
        )
