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
ASSET_NAME = "template.zip"


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
    zip_url = source.get("asset_url")
    source_type = source.get("source_type", "unknown")
    if not zip_url:
        print(f"[init] 下载源缺少 {ASSET_NAME} 附件，无法下载。")
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
            return _release_template_asset(release, "latest release")
        except RuntimeError as exc:
            if "HTTP 404" not in str(exc):
                raise
            releases = _api_get(f"{API_BASE}/releases?per_page=1")
            if isinstance(releases, list) and releases:
                return _release_template_asset(releases[0], "latest listed release")
            raise RuntimeError("仓库没有可用 release。")

    release = _api_get(f"{API_BASE}/releases/tags/{version}")
    return _release_template_asset(release, "release tag")


def _release_template_asset(release: dict | list, source_type: str) -> dict:
    if not isinstance(release, dict):
        raise RuntimeError("Release 信息格式异常。")

    assets = release.get("assets")
    if not isinstance(assets, list):
        raise RuntimeError("Release 资产信息格式异常。")

    asset_url = None
    for asset in assets:
        if isinstance(asset, dict) and asset.get("name") == ASSET_NAME:
            asset_url = asset.get("browser_download_url")
            break

    if not asset_url:
        raise RuntimeError(
            f"Release `{release.get('tag_name') or 'unknown'}` 未找到附件 `{ASSET_NAME}`。"
        )

    return {
        "source_type": source_type,
        "tag_name": release.get("tag_name") or "unknown",
        "asset_url": asset_url,
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
        zip_path = Path(tmp_dir) / ASSET_NAME
        extract_dir = Path(tmp_dir) / "extract"
        _download_file(zip_url, zip_path)
        extract_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(extract_dir)

        source_root = _detect_source_root(extract_dir)
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


def _detect_source_root(extract_dir: Path) -> Path:
    children = [path for path in extract_dir.iterdir() if path.name != "__MACOSX"]
    if not children:
        raise RuntimeError("压缩包为空。")

    dirs = [path for path in children if path.is_dir()]
    files = [path for path in children if path.is_file()]
    if len(dirs) == 1 and not files:
        return dirs[0]
    return extract_dir


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
