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
    _log(log, f"[步骤 {current}/{total}] {message}")


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
        _log(log, f"  · 发现已安装版本，准备覆盖：{target}")
    else:
        _log(log, f"  · 写入新目录：{target}")

    target_root.mkdir(parents=True, exist_ok=True)
    started = time.time()
    _copy_skill_tree(source_dir, target)
    elapsed = time.time() - started

    if not (target / "SKILL.md").is_file():
        raise RuntimeError(f"安装失败，未找到 {target / 'SKILL.md'}")
    _log(log, f"[OK] {spec.name} 已复制完成（{elapsed:.1f}s）→ {target}")
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
    _log(log, "  · 正在核对 SKILL.md 是否已就位…")
    ok = True
    targets = detection.target_skill_dirs(selected)
    if not targets:
        _log(log, "[FAIL] 没有可校验的目标 Skills 目录（请检查助手勾选）")
        return False
    for target in targets:
        for spec in SKILLS:
            path = target / spec.name / "SKILL.md"
            if path.is_file():
                _log(log, f"[OK] 校验通过：{path}")
            else:
                _log(log, f"[FAIL] 缺失：{path}")
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

        targets = detection.target_skill_dirs(selected)
        if not targets:
            raise RuntimeError("未找到可用的技能安装目录（请勾选已检测到的助手）")

        bundle = bundled_dir()
        _log(log, "============================================================")
        _log(log, "文献综述 Skills 安装开始")
        _log(log, "模式：离线本地复制（不访问 GitHub，不下载技能仓库）")
        _log(log, f"素材目录：{bundle}")
        _log(log, "用户勾选：" + "、".join(
            ASSISTANT_LABELS.get(k, k) for k in selected
        ))
        _log(log, "实际安装：" + "、".join(
            ASSISTANT_LABELS.get(k, k) for k in detection.selected_found_keys(selected)
        ))
        for t in targets:
            _log(log, f"  · Skills 目录：{t}")
        _log(log, "============================================================")

        if not (bundle / "skills").is_dir():
            raise RuntimeError(f"安装包缺少 bundled/skills: {bundle}")

        step = 1
        _step(log, step, total, "准备离线素材")
        for spec in SKILLS:
            source = bundled_skill_source(spec)
            _log(log, f"[OK] 已找到内置技能包：{spec.name}")
            _log(log, f"  · 路径：{source}")
        step += 1

        first_download: Optional[Path] = None
        for index, spec in enumerate(SKILLS, start=1):
            _step(log, step, total, f"安装技能 {index}/{skill_count}：{spec.name}")
            _log(log, f"  · 说明：{spec.description}")
            source = bundled_skill_source(spec)
            for target_root in targets:
                installed = install_one_skill(spec, source, target_root, log=log)
                result.installed_paths.append(str(installed))
                if spec.name == "sciencedirect-live-session-fetcher" and first_download is None:
                    first_download = installed
            step += 1

        if not options.skip_python_deps and first_download is not None:
            _step(log, step, total, "安装下载技能的可选 Python 依赖（离线）")
            install_python_deps(first_download, log=log)
            step += 1
        else:
            _log(log, "[步骤] 已跳过 Python 依赖安装")

        _step(log, step, total, "校验安装结果")
        if not verify_skill_layout(detection, log=log, selected=selected):
            raise RuntimeError("Skills 布局校验失败")

        result.ok = True
        result.messages.append("Skills 安装完成")
        _log(log, "============================================================")
        _log(log, "[OK] 全部完成：Skills 已从安装包内置素材安装")
        _log(log, "下一步：可进入「标准化测试」")
        _log(log, "============================================================")
        return result
    except Exception as exc:  # noqa: BLE001 - surface to GUI
        result.ok = False
        result.messages.append(str(exc))
        _log(log, f"[FAIL] {exc}")
        _log(log, "可返回上一步后重试；Skills 复制失败时请检查磁盘权限")
        return result
