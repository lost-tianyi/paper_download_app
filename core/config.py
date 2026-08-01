"""Installer configuration: skill sources and download URLs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


APP_NAME = "Literature Review Installer"
APP_VERSION = "1.2.1"


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
    exe = Path(sys.executable).resolve()
    candidates = [
        root / "bundled",
        root / "Resources" / "bundled",
        # macOS .app: MacOS/../Resources/bundled
        exe.parent.parent / "Resources" / "bundled",
        # PyInstaller onedir next to executable
        exe.parent / "_internal" / "bundled",
        exe.parent / "bundled",
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
        description="文献检索",
    ),
    SkillSpec(
        name="sciencedirect-live-session-fetcher",
        url="https://github.com/Given-Dream/sciencedirect-live-session-fetcher.git",
        description="全文下载",
    ),
    SkillSpec(
        name="literature-review-workflow",
        url="",
        description="工作流程指南",
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

# Legacy default; runtime UI uses core.i18n.wizard_steps().
WIZARD_STEPS = (
    "语言",
    "欢迎",
    "环境检测",
    "安装选项",
    "安装进度",
    "标准化测试",
    "完成",
)
