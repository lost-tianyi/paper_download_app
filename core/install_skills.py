"""Clone and install literature-review skills into assistant skill directories."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Callable, Optional

from .config import SKILLS, SkillSpec, user_cache_dir
from .detect import DetectionResult, detect_environment

LogFn = Callable[[str], None]


@dataclass
class InstallOptions:
    force: bool = False
    skip_network_test: bool = False
    skip_test: bool = False


@dataclass
class InstallResult:
    ok: bool
    messages: list[str] = field(default_factory=list)
    installed_paths: list[str] = field(default_factory=list)


def _log(log: Optional[LogFn], message: str) -> None:
    if log:
        log(message)


def _run(
    cmd: list[str],
    *,
    cwd: Optional[Path] = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=check,
        text=True,
        capture_output=True,
    )


def ensure_git(log: Optional[LogFn] = None) -> None:
    if not shutil.which("git"):
        raise RuntimeError("未找到 git，请先安装 Git 后再试")
    _log(log, "[OK] 已找到 git")


def refresh_skill_cache(spec: SkillSpec, log: Optional[LogFn] = None) -> Path:
    cache_root = user_cache_dir() / "skills"
    cache_root.mkdir(parents=True, exist_ok=True)
    dest = cache_root / spec.name

    if (dest / ".git").is_dir():
        _log(log, f"==> 更新缓存: {spec.name}")
        try:
            _run(["git", "-C", str(dest), "fetch", "--depth", "1", "origin", "HEAD"], check=False)
            result = _run(
                ["git", "-C", str(dest), "reset", "--hard", "FETCH_HEAD"],
                check=False,
            )
            if result.returncode != 0:
                _run(["git", "-C", str(dest), "pull", "--ff-only"], check=False)
        except OSError as exc:
            raise RuntimeError(f"更新技能缓存失败: {spec.name}: {exc}") from exc
    else:
        _log(log, f"==> 克隆技能仓库: {spec.name}")
        if dest.exists():
            shutil.rmtree(dest)
        try:
            _run(["git", "clone", "--depth", "1", spec.url, str(dest)])
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or exc.stdout or "").strip()
            raise RuntimeError(f"克隆失败: {spec.name}\n{detail}") from exc
    return dest


def _copy_skill_tree(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    ignore = shutil.ignore_patterns(".git", ".github", "__pycache__", ".DS_Store")
    # copytree needs dest not to exist when using dirs_exist_ok=False on older Python;
    # remove then copy into parent.
    shutil.rmtree(target)
    shutil.copytree(source, target, ignore=ignore)


def install_one_skill(
    spec: SkillSpec,
    cache_root: Path,
    target_root: Path,
    log: Optional[LogFn] = None,
) -> Path:
    source = cache_root if spec.subdir in (".", "") else cache_root / spec.subdir
    skill_md = source / "SKILL.md"
    if not skill_md.is_file():
        raise RuntimeError(f"技能包缺少 SKILL.md: {source}")

    target = target_root / spec.name
    if (target / "SKILL.md").is_file():
        _log(log, f"==> 覆盖已有技能: {target}")
    target_root.mkdir(parents=True, exist_ok=True)
    _copy_skill_tree(source, target)

    if not (target / "SKILL.md").is_file():
        raise RuntimeError(f"安装失败，未找到 {target / 'SKILL.md'}")
    _log(log, f"[OK] 已安装 {spec.name} -> {target}")
    return target


def install_python_deps(skill_dir: Path, log: Optional[LogFn] = None) -> None:
    req = skill_dir / "scripts" / "requirements.txt"
    if not req.is_file():
        return
    _log(log, f"==> 安装下载技能 Python 依赖: {req}")
    py = sys.executable
    try:
        result = _run(
            [py, "-m", "pip", "install", "--user", "-r", str(req)],
            check=False,
        )
        if result.returncode != 0:
            _log(
                log,
                "[WARN] Python 依赖安装未完全成功，后续测试会继续检查",
            )
            if result.stderr:
                _log(log, result.stderr.strip()[:500])
        else:
            _log(log, "[OK] Python 依赖已安装")
    except OSError as exc:
        _log(log, f"[WARN] pip 调用失败: {exc}")


def verify_skill_layout(
    detection: DetectionResult,
    log: Optional[LogFn] = None,
) -> bool:
    _log(log, "==> 校验 Skills 布局")
    ok = True
    for target in detection.target_skill_dirs():
        for spec in SKILLS:
            path = target / spec.name / "SKILL.md"
            if path.is_file():
                _log(log, f"[OK] {path}")
            else:
                _log(log, f"[FAIL] 缺失: {path}")
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

    if not detection.ok:
        for msg in detection.missing_messages():
            result.messages.append(msg)
            _log(log, f"[FAIL] {msg}")
        return result

    try:
        ensure_git(log)
        targets = detection.target_skill_dirs()
        if not targets:
            raise RuntimeError("未找到可用的技能安装目录")

        _log(log, "------------------------------------------------------------")
        _log(log, "开始安装 Skills")
        first_download: Optional[Path] = None

        for spec in SKILLS:
            _log(log, f"==> {spec.name}: {spec.description}")
            cache_root = refresh_skill_cache(spec, log=log)
            for target_root in targets:
                installed = install_one_skill(spec, cache_root, target_root, log=log)
                result.installed_paths.append(str(installed))
                if spec.name == "sciencedirect-live-session-fetcher" and first_download is None:
                    first_download = installed

        if first_download is not None:
            install_python_deps(first_download, log=log)

        if not verify_skill_layout(detection, log=log):
            raise RuntimeError("Skills 布局校验失败")

        result.ok = True
        result.messages.append("Skills 安装完成")
        _log(log, "[OK] Skills 安装完成")
        return result
    except Exception as exc:  # noqa: BLE001 - surface to GUI
        result.ok = False
        result.messages.append(str(exc))
        _log(log, f"[FAIL] {exc}")
        return result
