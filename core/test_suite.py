"""Standardized post-install smoke tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import py_compile
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from typing import Callable, Optional

from .config import SKILLS, user_cache_dir
from .detect import ASSISTANT_LABELS, DetectionResult, detect_environment
from .install_skills import verify_skill_layout

LogFn = Callable[[str], None]
SelectedAssistants = Optional[tuple[str, ...]]


@dataclass
class TestResult:
    ok: bool
    failures: int = 0
    messages: list[str] = field(default_factory=list)


def _log(log: Optional[LogFn], message: str) -> None:
    if log:
        log(message)


def _find_bash() -> str:
    bash = shutil.which("bash")
    if bash:
        return bash
    if sys.platform == "win32":
        for candidate in (
            r"C:\Program Files\Git\bin\bash.exe",
            r"C:\Program Files (x86)\Git\bin\bash.exe",
        ):
            if Path(candidate).is_file():
                return candidate
    return ""


def first_skill_path(
    detection: DetectionResult,
    name: str,
    selected: SelectedAssistants = None,
) -> Optional[Path]:
    for target in detection.target_skill_dirs(selected):
        path = target / name
        if (path / "SKILL.md").is_file():
            return path
    return None


def test_skill_frontmatter(
    detection: DetectionResult,
    result: TestResult,
    log: Optional[LogFn] = None,
    selected: SelectedAssistants = None,
) -> None:
    _log(log, "测试 1/5 · Skill 元数据")
    for spec in SKILLS:
        path = first_skill_path(detection, spec.name, selected)
        if path is None:
            result.failures += 1
            _log(log, f"[FAIL] 未找到已安装技能: {spec.name}")
            continue
        text = (path / "SKILL.md").read_text(encoding="utf-8", errors="replace")
        head = "\n".join(text.splitlines()[:5])
        if head.lstrip().startswith("---"):
            _log(log, f"[OK] {spec.name}: frontmatter 存在")
        else:
            result.failures += 1
            _log(log, f"[FAIL] {spec.name}: SKILL.md 缺少 YAML frontmatter")
        if f"name: {spec.name}" in text or f"name: '{spec.name}'" in text:
            _log(log, f"[OK] {spec.name}: name 字段匹配")
        else:
            _log(log, f"[WARN] {spec.name}: name 字段未精确匹配（继续）")


def _run_cli_version(cli: str, label: str, result: TestResult, log: Optional[LogFn]) -> None:
    try:
        proc = subprocess.run(
            [cli, "--version"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        out = (proc.stdout or proc.stderr or "").strip().replace("\n", " ")
        if proc.returncode == 0 or out:
            _log(log, f"[OK] {label} --version: {out[:120]}")
        else:
            result.failures += 1
            _log(log, f"[FAIL] {label} --version 失败")
    except (OSError, subprocess.SubprocessError) as exc:
        result.failures += 1
        _log(log, f"[FAIL] {label} --version 异常: {exc}")


def test_assistant_clis(
    detection: DetectionResult,
    result: TestResult,
    log: Optional[LogFn] = None,
    selected: SelectedAssistants = None,
) -> None:
    keys = detection.selected_found_keys(selected)
    labels = "、".join(ASSISTANT_LABELS.get(k, k) for k in keys) or "（无）"
    _log(log, f"测试 2/5 · 编码助手 CLI（仅测试勾选：{labels}）")

    if "codex" in keys:
        if detection.codex.cli_path:
            _run_cli_version(detection.codex.cli_path, "codex", result, log)
            try:
                proc = subprocess.run(
                    [detection.codex.cli_path, "doctor"],
                    capture_output=True,
                    text=True,
                    timeout=90,
                    check=False,
                )
                out = (proc.stdout or "") + (proc.stderr or "")
                if out.strip():
                    if proc.returncode == 0:
                        _log(log, "[OK] codex doctor 已执行")
                    else:
                        _log(log, "[WARN] codex doctor 返回非零，但 CLI 可运行")
                else:
                    result.failures += 1
                    _log(log, "[FAIL] codex doctor 无输出")
            except (OSError, subprocess.SubprocessError) as exc:
                _log(log, f"[WARN] codex doctor 跳过: {exc}")
        else:
            _log(log, "[WARN] 勾选了 Codex，但未找到 CLI，跳过 CLI 测试")
    else:
        _log(log, "  · 跳过 Codex（未勾选）")

    if "claude" in keys:
        if detection.claude.cli_path:
            _run_cli_version(detection.claude.cli_path, "claude", result, log)
        else:
            _log(log, "[WARN] 勾选了 Claude Code，但未找到 CLI，跳过 CLI 测试")
    else:
        _log(log, "  · 跳过 Claude Code（未勾选）")

    if "cursor" in keys:
        if detection.cursor.cli_path:
            _run_cli_version(detection.cursor.cli_path, "cursor", result, log)
        else:
            _log(log, "[WARN] 勾选了 Cursor，但未找到 CLI，跳过 CLI 测试")
    else:
        _log(log, "  · 跳过 Cursor（未勾选）")


def test_academic_search_scripts(
    detection: DetectionResult,
    result: TestResult,
    log: Optional[LogFn] = None,
    selected: SelectedAssistants = None,
) -> None:
    _log(log, "测试 3/5 · academic-search 自检")
    skill_dir = first_skill_path(detection, "academic-search", selected)
    if skill_dir is None:
        result.failures += 1
        _log(log, "[FAIL] academic-search 未安装")
        return

    check_deps = skill_dir / "scripts" / "check-deps.sh"
    oa_test = skill_dir / "scripts" / "oa-pdf-download-self-test.sh"
    oa_mjs = skill_dir / "scripts" / "oa-pdf-download.mjs"
    required_files = (
        skill_dir / "SKILL.md",
        check_deps,
        oa_test,
        oa_mjs,
        skill_dir / "scripts" / "cdp-proxy.mjs",
    )
    for path in required_files:
        if path.is_file():
            _log(log, f"[OK] 技能文件存在：{path.name}")
        else:
            result.failures += 1
            _log(log, f"[FAIL] 缺少技能文件：{path}")

    node = shutil.which("node")
    if not node:
        # Node is only for CDP browser automation / script self-tests.
        # arXiv / Semantic Scholar / PubMed API search works without Node.
        _log(log, "[WARN] 未检测到 Node.js —— 这不是安装失败")
        _log(log, "  · Node 仅用于 Google Scholar 等浏览器自动化（CDP）及脚本自检")
        _log(log, "  · 常规 API 检索（arXiv / Semantic Scholar / PubMed 等）不需要 Node")
        _log(log, "  · 安装包未内置 Node（体积约 50MB+，且多数用户用不到）")
        _log(log, "  · 如需 CDP 模式，可另行安装：https://nodejs.org/")
        _log(log, "[OK] academic-search 本体校验通过（已跳过需要 Node 的自检）")
        return

    _log(log, f"[OK] node: {node}")

    bash = _find_bash()
    if not bash:
        _log(log, "[WARN] 未找到 bash，跳过 shell 自检（Windows 可安装 Git for Windows）")
        _log(log, "[OK] academic-search 文件校验通过")
        return

    if check_deps.is_file():
        proc = subprocess.run(
            [bash, str(check_deps)],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode == 0:
            _log(log, "[OK] check-deps.sh 通过")
        elif "curl: missing" in out:
            result.failures += 1
            _log(log, "[FAIL] check-deps.sh 失败：缺少 curl")
        else:
            _log(log, "[WARN] check-deps.sh 有告警（常见于未开启 Chrome remote debugging）")
            _log(log, "[OK] check-deps.sh 已执行（API 模式可用）")
    else:
        result.failures += 1
        _log(log, "[FAIL] 缺少 check-deps.sh")

    if oa_test.is_file():
        proc = subprocess.run(
            [bash, str(oa_test)],
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        if proc.returncode == 0:
            _log(log, "[OK] oa-pdf-download-self-test.sh 通过")
        else:
            _log(log, "[WARN] oa-pdf-download-self-test.sh 未通过（不影响 Skills 安装）")
            detail = ((proc.stderr or proc.stdout or "")[-300:]).strip()
            if detail:
                _log(log, f"  · 详情：{detail}")
    else:
        result.failures += 1
        _log(log, "[FAIL] 缺少 oa-pdf-download-self-test.sh")

def test_download_skill_scripts(
    detection: DetectionResult,
    result: TestResult,
    log: Optional[LogFn] = None,
    selected: SelectedAssistants = None,
) -> None:
    _log(log, "测试 4/5 · 下载技能脚本")
    skill_dir = first_skill_path(
        detection, "sciencedirect-live-session-fetcher", selected
    )
    if skill_dir is None:
        result.failures += 1
        _log(log, "[FAIL] sciencedirect-live-session-fetcher 未安装")
        return

    scripts = [
        "devtools_sciencedirect_serial_fetch.py",
        "attach_sciencedirect_remote_debug.py",
        "firefox_sciencedirect_serial_fetch.py",
    ]
    for name in scripts:
        path = skill_dir / "scripts" / name
        if not path.is_file():
            result.failures += 1
            _log(log, f"[FAIL] 缺少脚本: {path}")
            continue
        try:
            py_compile.compile(str(path), doraise=True)
            _log(log, f"[OK] py_compile: {name}")
        except py_compile.PyCompileError as exc:
            result.failures += 1
            _log(log, f"[FAIL] py_compile 失败: {name}: {exc}")

    launcher = skill_dir / "scripts" / "launch_chrome_clone_remote_debug_macos.sh"
    edge = skill_dir / "scripts" / "launch_edge_clone_remote_debug.ps1"
    if launcher.is_file():
        _log(log, "[OK] macOS Chrome launcher 存在")
    elif edge.is_file():
        _log(log, "[OK] Windows Edge launcher 存在")
    else:
        _log(log, "[WARN] 未找到浏览器 launcher 脚本")


def test_network_smoke(
    result: TestResult,
    log: Optional[LogFn] = None,
    skip: bool = False,
) -> None:
    _log(log, "测试 5/5 · 标准化网络探测（Crossref）")
    if skip:
        _log(log, "[WARN] 已跳过网络探测")
        return

    work = user_cache_dir() / "test-run"
    work.mkdir(parents=True, exist_ok=True)
    out = work / "crossref-10.1038-nature14539.json"
    doi = "10.1038/nature14539"
    url = f"https://api.crossref.org/works/{doi}"
    try:
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "LiteratureReviewInstaller/1.0 (mailto:demo@example.com)",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read().decode("utf-8", errors="replace")
        out.write_text(data, encoding="utf-8")
        if "Deep Residual Learning" in data or "nature14539" in data:
            _log(log, f"[OK] Crossref DOI 解析成功: {doi}")
        else:
            result.failures += 1
            _log(log, "[FAIL] Crossref 响应缺少预期字段")
    except Exception as exc:  # noqa: BLE001
        result.failures += 1
        _log(log, f"[FAIL] Crossref 请求失败: {exc}")


def run_standardized_tests(
    detection: Optional[DetectionResult] = None,
    *,
    skip_network_test: bool = False,
    assistants: SelectedAssistants = None,
    log: Optional[LogFn] = None,
) -> TestResult:
    detection = detection or detect_environment()
    selected = tuple(assistants) if assistants else tuple(detection.found_assistant_keys())
    result = TestResult(ok=False)

    _log(log, "------------------------------------------------------------")
    _log(log, "开始标准化测试")
    _log(
        log,
        "测试范围："
        + ("、".join(ASSISTANT_LABELS.get(k, k) for k in selected) or "（无）"),
    )

    if not verify_skill_layout(detection, log=log, selected=selected):
        result.failures += 1
        _log(log, "[FAIL] Skills 布局校验失败")

    test_skill_frontmatter(detection, result, log, selected)
    test_assistant_clis(detection, result, log, selected)
    test_academic_search_scripts(detection, result, log, selected)
    test_download_skill_scripts(detection, result, log, selected)
    test_network_smoke(result, log=log, skip=skip_network_test)

    result.ok = result.failures == 0
    if result.ok:
        _log(log, "[OK] 全部标准化测试通过")
        result.messages.append("全部标准化测试通过")
    else:
        msg = f"有 {result.failures} 项测试失败"
        _log(log, f"[FAIL] {msg}")
        result.messages.append(msg)
    return result
