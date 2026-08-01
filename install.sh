#!/usr/bin/env bash
# One-click installer for the AI-based literature review workflow.
#
# Flow:
#   1) Detect Codex / Claude Code / Cursor (at least one) and Zotero
#   2) Install academic-search + sciencedirect-live-session-fetcher into skill dirs
#   3) Run standardized CLI / script smoke tests
#   4) Exit 0 only when tests pass

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/lib/test.sh"

usage() {
  cat <<'EOF'
用法:
  bash install.sh [选项]

选项:
  --detect-only          仅检测环境，不安装
  --skip-test            安装后跳过标准化测试
  --force                强制重新克隆技能缓存并覆盖安装
  --dry-run              只打印将要执行的操作
  --full-agent-test      额外用 codex exec / claude -p 探测技能（需已登录）
  --skip-network-test    跳过 Crossref 网络探测
  -h, --help             显示帮助

环境变量:
  FORCE_REINSTALL=1
  DRY_RUN=1
  FULL_AGENT_TEST=1
  SKIP_NETWORK_TEST=1

示例:
  bash install.sh
  bash install.sh --detect-only
  bash install.sh --full-agent-test
EOF
}

DETECT_ONLY=0
SKIP_TEST=0
FORCE_REINSTALL="${FORCE_REINSTALL:-0}"
DRY_RUN="${DRY_RUN:-0}"
FULL_AGENT_TEST="${FULL_AGENT_TEST:-0}"
SKIP_NETWORK_TEST="${SKIP_NETWORK_TEST:-0}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --detect-only) DETECT_ONLY=1 ;;
    --skip-test) SKIP_TEST=1 ;;
    --force) FORCE_REINSTALL=1 ;;
    --dry-run) DRY_RUN=1 ;;
    --full-agent-test) FULL_AGENT_TEST=1 ;;
    --skip-network-test) SKIP_NETWORK_TEST=1 ;;
    -h|--help) usage; exit 0 ;;
    *) die "未知参数: $1（使用 --help 查看用法）" ;;
  esac
  shift
done

export FORCE_REINSTALL DRY_RUN FULL_AGENT_TEST SKIP_NETWORK_TEST

print_banner() {
  section "AI Literature Review Workflow Installer"
  log "基于工作流文档安装并验证两个核心 Skills："
  log "  1) academic-search"
  log "     ${URL_ACADEMIC_SEARCH}"
  log "  2) sciencedirect-live-session-fetcher"
  log "     ${URL_DOWNLOAD_SKILL}"
  log ""
  log "目标技能目录："
  log "  Codex : ~/.codex/skills/"
  log "  Claude: ~/.claude/skills/"
  log "  Cursor: ~/.cursor/skills/"
}

print_next_steps() {
  section "安装完成 · 下一步"
  cat <<'EOF'
1. 打开已检测到的编码助手（Codex / Claude Code / Cursor）。
2. 在项目目录中发起文献检索，例如：

   使用 academic-search，检索 2020-2026 年关于 <你的主题> 的期刊论文，
   核验 DOI，输出 Core / Background / Pending Verification，并导出 Excel。

3. 人工审阅 Excel，增加 Approved = Yes/No 列。
4. 机构权限场景下，先在浏览器登录出版社站点，再调用
   sciencedirect-live-session-fetcher 仅处理 Approved = Yes 的记录。
5. 将下载结果整理进 Zotero，并做最终对账。

注意：不要向助手提供账号密码；仅使用你已授权的合法访问。
EOF
}

main() {
  print_banner

  if ! assert_prerequisites; then
    exit 1
  fi

  if (( DETECT_ONLY )); then
    ok "仅检测模式结束"
    exit 0
  fi

  install_all_skills

  if (( SKIP_TEST )); then
    verify_skill_layout
    warn "已按 --skip-test 跳过标准化测试"
    print_next_steps
    exit 0
  fi

  if run_standardized_tests; then
    print_next_steps
    section "结果"
    ok "安装完成：环境检测通过 · Skills 已就位 · 标准化测试通过"
    exit 0
  fi

  section "结果"
  die "安装未完成：标准化测试失败。请根据上方日志修复后重试。"
}

main "$@"
