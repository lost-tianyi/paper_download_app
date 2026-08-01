"""Installer configuration: skill sources and download URLs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


APP_NAME = "Literature Review Workflow Installer"
APP_VERSION = "1.0.0"


def project_root() -> Path:
    """Return the project / resource root whether running from source or frozen."""
    if getattr(sys, "frozen", False):
        # PyInstaller onefile/onedir extracts datas into sys._MEIPASS
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)
        exe = Path(sys.executable).resolve()
        if sys.platform == "darwin" and ".app/Contents/MacOS" in str(exe):
            return exe.parents[1]  # Contents/
        return exe.parent
    return Path(__file__).resolve().parent.parent


def bundled_dir() -> Path:
    """Offline skills/wheels directory shipped inside the installer."""
    root = project_root()
    candidates = [
        root / "bundled",
        root / "Resources" / "bundled",  # macOS app Contents/Resources via some layouts
    ]
    for path in candidates:
        if (path / "skills").is_dir():
            return path
    return root / "bundled"


def user_cache_dir() -> Path:
    home = Path.home()
    if sys.platform == "darwin":
        base = home / "Library" / "Caches" / "LiteratureReviewInstaller"
    elif sys.platform == "win32":
        base = Path(
            __import__("os").environ.get("LOCALAPPDATA", home / "AppData" / "Local")
        ) / "LiteratureReviewInstaller"
    else:
        base = home / ".cache" / "LiteratureReviewInstaller"
    base.mkdir(parents=True, exist_ok=True)
    return base


@dataclass(frozen=True)
class SkillSpec:
    name: str
    url: str
    description: str
    # Offline package lives at bundled/skills/<name>/ (already install-ready).


SKILLS: tuple[SkillSpec, ...] = (
    SkillSpec(
        name="academic-search",
        url="https://github.com/ustc-ai4science/academic-search.git",
        description="学术文献检索、核验与结构化导出",
    ),
    SkillSpec(
        name="sciencedirect-live-session-fetcher",
        url="https://github.com/Given-Dream/sciencedirect-live-session-fetcher.git",
        description="通过已授权浏览器会话合法串行下载 PDF",
    ),
)

DOWNLOAD_URLS = {
    "codex": "https://chatgpt.com/codex",
    "claude": "https://docs.anthropic.com/en/docs/claude-code/overview",
    "cursor": "https://cursor.com/download",
    "zotero": "https://www.zotero.org/download/",
    "academic_search": "https://github.com/ustc-ai4science/academic-search",
    "download_skill": "https://github.com/Given-Dream/sciencedirect-live-session-fetcher",
}

WIZARD_STEPS = (
    "欢迎",
    "环境检测",
    "安装选项",
    "安装进度",
    "标准化测试",
    "完成",
)
