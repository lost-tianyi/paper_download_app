"""Install literature-review skills from the offline bundled package."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Callable, Optional

from .config import SKILLS, SkillSpec, bundled_dir
from .detect import DetectionResult, detect_environment

LogFn = Callable[[str], None]


@dataclass
class InstallOptions:
    force: bool = False
    skip_network_test: bool = False
    skip_test: bool = False
    skip_python_deps: bool = False
    # Which assistants to install/test for: "codex" | "claude" | "cursor"
    assistants: tuple[str, ...] = ()


@dataclass
class InstallResult:
    ok: bool
    messages: list[str] = field(default_factory=list)
    installed_paths: list[str] = field(default_factory=list)


def _log(log: Optional[LogFn], message: str) -> None:
    if log:
        log(message)


def _step(log: Optional[LogFn], current: int, total: int, message: str) -> None:
    _log(log, f"[{current}/{total}] {message}")


def bundled_skill_source(spec: SkillSpec) -> Path:
    """Return the offline skill package directory (already install-ready)."""
    from .i18n import feature_label

    path = bundled_dir() / "skills" / spec.name
    if not (path / "SKILL.md").is_file():
        raise RuntimeError(
            f"缺少安装内容：{feature_label(spec.name, spec.name)}。请使用完整安装程序。"
        )
    return path


def _copy_skill_tree(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    ignore = shutil.ignore_patterns(".git", ".github", "__pycache__", ".DS_Store")
    shutil.copytree(source, target, ignore=ignore)


def install_one_skill(
    spec: SkillSpec,
    source_dir: Path,
    target_root: Path,
    log: Optional[LogFn] = None,
) -> Path:
    skill_md = source_dir / "SKILL.md"
    if not skill_md.is_file():
        raise RuntimeError(f"技能包缺少 SKILL.md: {source_dir}")

    from .i18n import feature_label, t

    target = target_root / spec.name
    label = feature_label(spec.name, spec.description or spec.name)
    target_root.mkdir(parents=True, exist_ok=True)
    started = time.time()
    _copy_skill_tree(source_dir, target)
    elapsed = time.time() - started

    if not (target / "SKILL.md").is_file():
        raise RuntimeError(t("install_fail", error=label))
    _log(log, f"[OK] {t('install_feature_ok', name=label)}（{elapsed:.1f}s）")
    return target


def _resolve_pip_python(log: Optional[LogFn] = None) -> Optional[str]:
    """Prefer a real Python for pip; frozen GUI exe is a poor pip host."""
    if not getattr(sys, "frozen", False):
        return sys.executable

    for name in ("python3", "python"):
        path = shutil.which(name)
        if path:
            _log(log, f"  · 将使用系统 Python 执行离线 pip：{path}")
            return path

    _log(log, "[WARN] 未检测到系统 Python，跳过依赖安装（Skills 本体已安装完成）")
    _log(log, "  说明：仅在使用「浏览器抓 PDF」脚本时才需要这些依赖")
    return None


def install_python_deps(skill_dir: Path, log: Optional[LogFn] = None) -> None:
    """Install download-skill deps from offline wheels bundled in the installer."""
    req = skill_dir / "scripts" / "requirements.txt"
    if not req.is_file():
        _log(log, "  · 未找到 requirements.txt，跳过 Python 依赖")
        return

    wheels = bundled_dir() / "wheels"
    _log(log, "  · 此步骤使用安装包内置 wheels，不会访问 PyPI / 不会联网下载")
    _log(log, "  · 仅服务于下载技能脚本；不影响 academic-search 使用")

    if not wheels.is_dir() or not any(wheels.glob("*.whl")):
        _log(log, "[WARN] 安装包未包含 wheels，跳过 pip（不影响 Skills 本体安装）")
        return

    wheel_count = len(list(wheels.glob("*.whl")))
    _log(log, f"  · 离线包数量：{wheel_count} 个 wheel")
    _log(log, f"  · 依赖清单：{req.name}")

    py = _resolve_pip_python(log)
    if not py:
        return

    cmd = [
        py,
        "-m",
        "pip",
        "install",
        "--user",
        "--no-index",
        f"--find-links={wheels}",
        "-r",
        str(req),
        "--disable-pip-version-check",
        "--no-warn-script-location",
        "-v",
    ]
    _log(log, "  · 开始本地安装（解压 wheel，通常需要几十秒，请稍候…）")
    started = time.time()

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert proc.stdout is not None
        interesting_prefixes = (
            "Processing ",
            "Collecting ",
            "Installing ",
            "Requirement already",
            "Successfully installed",
            "Using cached",
            "Looking in links",
            "ERROR",
            "error:",
            "WARNING",
        )
        for line in proc.stdout:
            text = line.rstrip()
            if not text:
                continue
            if text.startswith(interesting_prefixes) or "Installing collected" in text:
                _log(log, f"  · {text}")
        code = proc.wait()
        elapsed = time.time() - started
        if code != 0:
            _log(log, f"[WARN] 离线 pip 未完全成功（耗时 {elapsed:.1f}s）")
            _log(log, "  Skills 本体已安装；下载脚本依赖可稍后手动处理")
        else:
            _log(log, f"[OK] Python 依赖已从离线包安装（耗时 {elapsed:.1f}s）")
    except OSError as exc:
        _log(log, f"[WARN] pip 调用失败: {exc}")
        _log(log, "  Skills 本体不受影响，可继续下一步测试")


def verify_skill_layout(
    detection: DetectionResult,
    log: Optional[LogFn] = None,
    selected: Optional[tuple[str, ...]] = None,
) -> bool:
    from .i18n import feature_label

    ok = True
    targets = detection.target_skill_dirs(selected)
    if not targets:
        return False
    for target in targets:
        for spec in SKILLS:
            path = target / spec.name / "SKILL.md"
            label = feature_label(spec.name, spec.description or spec.name)
            if path.is_file():
                _log(log, f"[OK] {label}")
            else:
                _log(log, f"[FAIL] {label}")
                ok = False
    return ok


def install_all_skills(
    detection: Optional[DetectionResult] = None,
    options: Optional[InstallOptions] = None,
    log: Optional[LogFn] = None,
) -> InstallResult:
    options = options or InstallOptions()
    detection = detection or detect_environment()
    result = InstallResult(ok=False)

    selected = tuple(options.assistants) if options.assistants else tuple(
        detection.found_assistant_keys()
    )
    if not detection.ok_for_selection(selected):
        for msg in detection.missing_messages(selected):
            result.messages.append(msg)
            _log(log, f"[FAIL] {msg}")
        return result

    skill_count = len(SKILLS)
    total = 2 + skill_count + (0 if options.skip_python_deps else 1)

    try:
        from .detect import ASSISTANT_LABELS
        from .i18n import feature_label, get_language, t

        targets = detection.target_skill_dirs(selected)
        if not targets:
            raise RuntimeError(t("options_no_target"))

        bundle = bundled_dir()
        sep = ", " if get_language() == "en" else "、"
        labels = sep.join(
            ASSISTANT_LABELS.get(k, k)
            for k in detection.selected_found_keys(selected)
        )
        _log(log, t("install_banner"))
        _log(log, t("install_mode"))
        _log(log, t("install_selected", labels=labels))

        if not (bundle / "skills").is_dir():
            raise RuntimeError(t("install_fail", error="bundle"))

        step = 1
        _step(log, step, total, t("install_prepare"))
        for spec in SKILLS:
            bundled_skill_source(spec)
            _log(log, f"[OK] {feature_label(spec.name, spec.description)}")
        step += 1

        first_download: Optional[Path] = None
        for index, spec in enumerate(SKILLS, start=1):
            label = feature_label(spec.name, spec.description or spec.name)
            _step(log, step, total, t("install_feature", name=label))
            source = bundled_skill_source(spec)
            for target_root in targets:
                installed = install_one_skill(spec, source, target_root, log=log)
                result.installed_paths.append(str(installed))
                if spec.name == "sciencedirect-live-session-fetcher" and first_download is None:
                    first_download = installed
            step += 1

        if not options.skip_python_deps and first_download is not None:
            _step(log, step, total, t("install_deps"))
            install_python_deps(first_download, log=log)
            step += 1

        _step(log, step, total, t("install_verify"))
        if not verify_skill_layout(detection, log=log, selected=selected):
            raise RuntimeError(t("install_fail", error="verify"))

        result.ok = True
        result.messages.append(t("install_done"))
        _log(log, "[OK] " + t("install_done"))
        return result
    except Exception as exc:  # noqa: BLE001 - surface to GUI
        from .i18n import t

        result.ok = False
        result.messages.append(str(exc))
        _log(log, f"[FAIL] {t('install_fail', error=str(exc))}")
        _log(log, t("install_retry"))
        return result
