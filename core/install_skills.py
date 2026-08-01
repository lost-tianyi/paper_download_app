"""Install literature-review skills from the offline bundled package."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Callable, Optional

from .config import SKILLS, SkillSpec, bundled_dir, project_root
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


def bundled_skill_source(spec: SkillSpec) -> Path:
    """Return the offline skill package directory (already install-ready)."""
    path = bundled_dir() / "skills" / spec.name
    if not (path / "SKILL.md").is_file():
        raise RuntimeError(
            f"安装包缺少离线技能素材: {path}\n"
            "请使用完整打包的安装程序，或运行 build/vendor_skills.sh 后重新构建。"
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

    target = target_root / spec.name
    if (target / "SKILL.md").is_file():
        _log(log, f"==> 覆盖已有技能: {target}")
    target_root.mkdir(parents=True, exist_ok=True)
    _copy_skill_tree(source_dir, target)

    if not (target / "SKILL.md").is_file():
        raise RuntimeError(f"安装失败，未找到 {target / 'SKILL.md'}")
    _log(log, f"[OK] 已安装 {spec.name} -> {target}")
    return target


def install_python_deps(skill_dir: Path, log: Optional[LogFn] = None) -> None:
    """Install download-skill deps from offline wheels bundled in the installer."""
    req = skill_dir / "scripts" / "requirements.txt"
    if not req.is_file():
        return

    wheels = bundled_dir() / "wheels"
    py = sys.executable
    _log(log, "==> 安装下载技能 Python 依赖（离线 wheels）")

    if not wheels.is_dir() or not any(wheels.glob("*.whl")):
        _log(log, "[WARN] 安装包未包含 wheels，跳过 pip（不影响 Skills 本体安装）")
        return

    try:
        result = _run(
            [
                py,
                "-m",
                "pip",
                "install",
                "--user",
                "--no-index",
                f"--find-links={wheels}",
                "-r",
                str(req),
            ],
            check=False,
        )
        if result.returncode != 0:
            _log(log, "[WARN] 离线 pip 未完全成功，后续测试会继续检查脚本语法")
            detail = (result.stderr or result.stdout or "").strip()
            if detail:
                _log(log, detail[:500])
        else:
            _log(log, "[OK] Python 依赖已从离线包安装")
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
        targets = detection.target_skill_dirs()
        if not targets:
            raise RuntimeError("未找到可用的技能安装目录")

        bundle = bundled_dir()
        _log(log, "------------------------------------------------------------")
        _log(log, "开始安装 Skills（离线本地复制，无需联网）")
        _log(log, f"素材目录: {bundle}")
        if not (bundle / "skills").is_dir():
            raise RuntimeError(f"安装包缺少 bundled/skills: {bundle}")

        first_download: Optional[Path] = None
        for spec in SKILLS:
            _log(log, f"==> {spec.name}: {spec.description}")
            source = bundled_skill_source(spec)
            _log(log, f"==> 使用离线素材: {source}")
            for target_root in targets:
                installed = install_one_skill(spec, source, target_root, log=log)
                result.installed_paths.append(str(installed))
                if spec.name == "sciencedirect-live-session-fetcher" and first_download is None:
                    first_download = installed

        if first_download is not None:
            install_python_deps(first_download, log=log)

        if not verify_skill_layout(detection, log=log):
            raise RuntimeError("Skills 布局校验失败")

        result.ok = True
        result.messages.append("Skills 安装完成")
        _log(log, "[OK] Skills 安装完成（全部来自安装包内置素材）")
        return result
    except Exception as exc:  # noqa: BLE001 - surface to GUI
        result.ok = False
        result.messages.append(str(exc))
        _log(log, f"[FAIL] {exc}")
        return result
