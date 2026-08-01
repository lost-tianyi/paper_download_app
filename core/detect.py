"""Detect Codex / Claude Code / Cursor and Zotero across platforms."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os
import shutil
import subprocess
import sys
from typing import Iterable, Optional, Sequence


# Stable keys used by installer selection / install / tests.
ASSISTANT_KEYS: tuple[str, ...] = ("codex", "claude", "cursor")
ASSISTANT_LABELS = {
    "codex": "Codex",
    "claude": "Claude Code",
    "cursor": "Cursor",
}


@dataclass
class AppHit:
    name: str
    found: bool
    app_path: str = ""
    cli_path: str = ""
    skills_dir: str = ""


@dataclass
class DetectionResult:
    codex: AppHit
    claude: AppHit
    cursor: AppHit
    zotero: AppHit
    platform: str = field(default_factory=lambda: sys.platform)

    def hit(self, key: str) -> AppHit:
        if key == "codex":
            return self.codex
        if key == "claude":
            return self.claude
        if key == "cursor":
            return self.cursor
        raise KeyError(f"unknown assistant key: {key}")

    def found_assistant_keys(self) -> list[str]:
        return [key for key in ASSISTANT_KEYS if self.hit(key).found]

    @property
    def assistant_count(self) -> int:
        return len(self.found_assistant_keys())

    @property
    def ok(self) -> bool:
        return self.assistant_count > 0 and self.zotero.found

    def selected_found_keys(self, selected: Sequence[str] | None = None) -> list[str]:
        if selected is None:
            return self.found_assistant_keys()
        wanted = {k for k in selected if k in ASSISTANT_KEYS}
        return [key for key in ASSISTANT_KEYS if key in wanted and self.hit(key).found]

    def ok_for_selection(self, selected: Sequence[str]) -> bool:
        return bool(self.selected_found_keys(selected)) and self.zotero.found

    def target_skill_dirs(self, selected: Sequence[str] | None = None) -> list[Path]:
        dirs: list[Path] = []
        for key in self.selected_found_keys(selected):
            hit = self.hit(key)
            if hit.skills_dir:
                dirs.append(Path(hit.skills_dir))
        return dirs

    def missing_messages(self, selected: Sequence[str] | None = None) -> list[str]:
        msgs: list[str] = []
        if selected is None:
            if self.assistant_count == 0:
                msgs.append("需要至少安装 Codex / Claude Code / Cursor 其中之一")
        else:
            if not selected:
                msgs.append("请至少勾选一个 AI 编程助手")
            elif not self.selected_found_keys(selected):
                labels = "、".join(ASSISTANT_LABELS[k] for k in selected if k in ASSISTANT_LABELS)
                msgs.append(f"勾选的助手尚未安装或未检测到：{labels or '（无）'}")
        if not self.zotero.found:
            msgs.append("未检测到 Zotero，请安装或手动指定路径")
        return msgs


def _which(name: str) -> str:
    path = shutil.which(name)
    return path or ""


def _first_existing(candidates: Iterable[Path]) -> Optional[Path]:
    for path in candidates:
        if path and path.exists():
            return path
    return None


def _first_executable(candidates: Iterable[str]) -> str:
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
        # Windows .exe may not report X_OK the same way
        if sys.platform == "win32" and path.is_file():
            return str(path)
    return ""


def _macos_app(name: str) -> Optional[Path]:
    return _first_existing(
        [
            Path("/Applications") / f"{name}.app",
            Path.home() / "Applications" / f"{name}.app",
        ]
    )


def _mdfind_bundle(bundle_id: str) -> Optional[Path]:
    if sys.platform != "darwin" or not shutil.which("mdfind"):
        return None
    try:
        out = subprocess.check_output(
            ["mdfind", f"kMDItemCFBundleIdentifier == '{bundle_id}'"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=5,
        ).strip()
    except (subprocess.SubprocessError, OSError):
        return None
    if not out:
        return None
    path = Path(out.splitlines()[0].strip())
    return path if path.exists() else None


def _skills_dir(product: str) -> Path:
    return Path.home() / f".{product}" / "skills"


def detect_codex() -> AppHit:
    hit = AppHit(name="Codex", found=False, skills_dir=str(_skills_dir("codex")))
    cli_candidates = [
        _which("codex"),
        str(Path.home() / ".local" / "bin" / "codex"),
        "/opt/homebrew/bin/codex",
        "/usr/local/bin/codex",
    ]
    if sys.platform == "darwin":
        cli_candidates.insert(
            1, "/Applications/ChatGPT.app/Contents/Resources/codex"
        )
    if sys.platform == "win32":
        local = Path(os.environ.get("LOCALAPPDATA", ""))
        cli_candidates.extend(
            [
                str(local / "Programs" / "ChatGPT" / "resources" / "codex.exe"),
                str(local / "Programs" / "codex" / "codex.exe"),
            ]
        )
    hit.cli_path = _first_executable(cli_candidates)

    app: Optional[Path] = None
    if sys.platform == "darwin":
        app = _mdfind_bundle("com.openai.codex") or _macos_app("ChatGPT")
        if app and not hit.cli_path:
            embedded = app / "Contents" / "Resources" / "codex"
            if embedded.exists():
                hit.cli_path = str(embedded)
    elif sys.platform == "win32":
        local = Path(os.environ.get("LOCALAPPDATA", ""))
        app = _first_existing(
            [
                local / "Programs" / "ChatGPT" / "ChatGPT.exe",
                local / "Programs" / "codex" / "Codex.exe",
            ]
        )

    if app:
        hit.app_path = str(app)
    hit.found = bool(hit.cli_path or hit.app_path)
    return hit


def detect_claude() -> AppHit:
    hit = AppHit(name="Claude Code", found=False, skills_dir=str(_skills_dir("claude")))
    cli_candidates = [
        _which("claude"),
        str(Path.home() / ".local" / "bin" / "claude"),
        "/opt/homebrew/bin/claude",
        "/usr/local/bin/claude",
    ]
    if sys.platform == "win32":
        appdata = Path(os.environ.get("APPDATA", ""))
        npm = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "nodejs"
        cli_candidates.extend(
            [
                str(appdata / "npm" / "claude.cmd"),
                str(appdata / "npm" / "claude.exe"),
                str(npm / "claude.cmd"),
            ]
        )
    hit.cli_path = _first_executable(cli_candidates)

    app: Optional[Path] = None
    if sys.platform == "darwin":
        app = _macos_app("Claude") or _mdfind_bundle("com.anthropic.claudefordesktop")
    elif sys.platform == "win32":
        local = Path(os.environ.get("LOCALAPPDATA", ""))
        app = _first_existing(
            [
                local / "AnthropicClaude" / "claude.exe",
                local / "Programs" / "Claude" / "Claude.exe",
            ]
        )

    if app:
        hit.app_path = str(app)
    # Claude Code is primarily a CLI; require CLI for "found" when no desktop app
    hit.found = bool(hit.cli_path or hit.app_path)
    return hit


def detect_cursor() -> AppHit:
    hit = AppHit(name="Cursor", found=False, skills_dir=str(_skills_dir("cursor")))
    cli_candidates = [
        _which("cursor"),
        str(Path.home() / ".local" / "bin" / "cursor"),
        "/opt/homebrew/bin/cursor",
        "/usr/local/bin/cursor",
        "/Applications/Cursor.app/Contents/Resources/app/bin/cursor",
    ]
    if sys.platform == "win32":
        local = Path(os.environ.get("LOCALAPPDATA", ""))
        cli_candidates.extend(
            [
                str(local / "Programs" / "cursor" / "Cursor.exe"),
                str(local / "Programs" / "cursor" / "resources" / "app" / "bin" / "cursor.cmd"),
            ]
        )
    hit.cli_path = _first_executable(cli_candidates)

    app: Optional[Path] = None
    if sys.platform == "darwin":
        app = _macos_app("Cursor") or _mdfind_bundle("com.todesktop.230313mzl4w4u92")
        if app and not hit.cli_path:
            embedded = app / "Contents" / "Resources" / "app" / "bin" / "cursor"
            if embedded.exists():
                hit.cli_path = str(embedded)
    elif sys.platform == "win32":
        local = Path(os.environ.get("LOCALAPPDATA", ""))
        app = _first_existing(
            [
                local / "Programs" / "cursor" / "Cursor.exe",
                Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
                / "Cursor"
                / "Cursor.exe",
            ]
        )
        if app and not hit.cli_path:
            hit.cli_path = str(app)

    if app:
        hit.app_path = str(app)
    hit.found = bool(hit.cli_path or hit.app_path)
    return hit


def _looks_like_zotero_app(path: Path) -> bool:
    """Return True if path appears to be a Zotero install (cross-platform)."""
    try:
        path = path.expanduser()
        if not path.exists():
            return False
    except OSError:
        return False

    name = path.name.lower()

    if sys.platform == "darwin":
        # Prefer *.app bundles named Zotero*.app
        app = path
        if path.is_file():
            # Binary selected inside the bundle
            for parent in path.parents:
                if parent.suffix == ".app":
                    app = parent
                    break
        if app.suffix == ".app" and app.is_dir():
            if "zotero" not in app.stem.lower():
                return False
            macos_bin = app / "Contents" / "MacOS"
            if not macos_bin.is_dir():
                return False
            # Official builds ship Contents/MacOS/zotero
            for candidate in macos_bin.iterdir():
                if candidate.is_file() and "zotero" in candidate.name.lower():
                    return True
            plist = app / "Contents" / "Info.plist"
            return plist.is_file()
        # Allow selecting the executable itself
        return path.is_file() and "zotero" in name

    if sys.platform == "win32":
        if path.is_file():
            return path.suffix.lower() == ".exe" and "zotero" in name
        if path.is_dir():
            return (path / "zotero.exe").is_file()
        return False

    # Linux: binary or known flatpak marker
    if path.is_file() and os.access(path, os.X_OK) and "zotero" in name:
        return True
    return False


def resolve_zotero_path(path: str | Path) -> AppHit:
    """Validate a user-picked Zotero path and return an AppHit."""
    hit = AppHit(name="Zotero", found=False)
    raw = str(path or "").strip()
    if not raw:
        return hit

    p = Path(raw).expanduser()
    try:
        p = p.resolve()
    except OSError:
        pass

    if not p.exists():
        return hit

    if sys.platform == "darwin":
        app = p
        if p.is_file():
            for parent in p.parents:
                if parent.suffix == ".app":
                    app = parent
                    break
        if app.suffix != ".app" and p.is_dir() and (p / "Contents" / "MacOS").is_dir():
            app = p
        if not _looks_like_zotero_app(app if app.suffix == ".app" else p):
            return hit
        target = app if app.suffix == ".app" else p
        hit.app_path = str(target)
        hit.cli_path = str(target)
        hit.found = True
        return hit

    if sys.platform == "win32":
        exe = p
        if p.is_dir():
            exe = p / "zotero.exe"
        if not _looks_like_zotero_app(exe):
            return hit
        hit.app_path = str(exe)
        hit.cli_path = str(exe)
        hit.found = True
        return hit

    if _looks_like_zotero_app(p):
        hit.app_path = str(p)
        hit.cli_path = str(p)
        hit.found = True
    return hit


def detect_zotero(manual_path: str = "") -> AppHit:
    # Manual override first (user browsed a custom install location).
    if manual_path:
        manual = resolve_zotero_path(manual_path)
        if manual.found:
            return manual

    hit = AppHit(name="Zotero", found=False)
    cli = _which("zotero")
    if cli:
        hit.cli_path = cli
        hit.app_path = cli
        hit.found = True
        return hit

    if sys.platform == "darwin":
        candidates: list[Path] = []
        for base in (Path("/Applications"), Path.home() / "Applications"):
            candidates.append(base / "Zotero.app")
            if base.is_dir():
                try:
                    for child in base.iterdir():
                        if child.suffix == ".app" and "zotero" in child.stem.lower():
                            candidates.append(child)
                except OSError:
                    pass
        app = _first_existing(candidates) or _mdfind_bundle("org.zotero.zotero")
        if app and _looks_like_zotero_app(app):
            hit.app_path = str(app)
            hit.found = True
            return hit
    elif sys.platform == "win32":
        pf = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
        pf86 = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
        local = Path(os.environ.get("LOCALAPPDATA", ""))
        home = Path.home()
        app = _first_existing(
            [
                pf / "Zotero" / "zotero.exe",
                pf86 / "Zotero" / "zotero.exe",
                local / "Programs" / "Zotero" / "zotero.exe",
                home / "AppData" / "Local" / "Programs" / "Zotero" / "zotero.exe",
                home / "Zotero" / "zotero.exe",
                Path(r"D:\Program Files\Zotero\zotero.exe"),
                Path(r"D:\Zotero\zotero.exe"),
            ]
        )
        if app:
            hit.app_path = str(app)
            hit.cli_path = str(app)
            hit.found = True
            return hit
    else:
        # Linux flatpak
        if shutil.which("flatpak"):
            try:
                subprocess.check_call(
                    ["flatpak", "info", "org.zotero.Zotero"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5,
                )
                hit.app_path = "flatpak:org.zotero.Zotero"
                hit.found = True
            except (subprocess.SubprocessError, OSError):
                pass
    return hit


def detect_environment(manual_zotero_path: str = "") -> DetectionResult:
    return DetectionResult(
        codex=detect_codex(),
        claude=detect_claude(),
        cursor=detect_cursor(),
        zotero=detect_zotero(manual_path=manual_zotero_path),
    )
