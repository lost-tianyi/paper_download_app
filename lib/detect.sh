#!/usr/bin/env bash
# Detect Codex / Claude Code / Cursor and Zotero.

set -euo pipefail

# shellcheck disable=SC1091
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

# Exported detection results
DETECTED_CODEX=0
DETECTED_CLAUDE=0
DETECTED_CURSOR=0
DETECTED_ZOTERO=0
DETECTED_ASSISTANT_COUNT=0

CODEX_CLI=""
CLAUDE_CLI=""
CURSOR_CLI=""
ZOTERO_APP=""
CODEX_APP=""
CLAUDE_APP=""
CURSOR_APP=""

CODEX_SKILLS_DIR="${HOME}/.codex/skills"
CLAUDE_SKILLS_DIR="${HOME}/.claude/skills"
CURSOR_SKILLS_DIR="${HOME}/.cursor/skills"

find_first_executable() {
  local candidate
  for candidate in "$@"; do
    if [[ -n "${candidate}" && -x "${candidate}" ]]; then
      printf '%s\n' "${candidate}"
      return 0
    fi
  done
  return 1
}

resolve_cli_from_whence() {
  local name="$1"
  if command -v "${name}" >/dev/null 2>&1; then
    command -v "${name}"
    return 0
  fi
  return 1
}

detect_codex() {
  DETECTED_CODEX=0
  CODEX_CLI=""
  CODEX_APP=""

  local found_cli found_app
  found_cli="$(find_first_executable \
    "$(resolve_cli_from_whence codex 2>/dev/null || true)" \
    "/Applications/ChatGPT.app/Contents/Resources/codex" \
    "${HOME}/.local/bin/codex" \
    "/opt/homebrew/bin/codex" \
    "/usr/local/bin/codex" \
    || true)"

  if [[ -n "${found_cli}" ]]; then
    CODEX_CLI="${found_cli}"
    DETECTED_CODEX=1
  fi

  if [[ "$(os_name)" == "macos" ]]; then
    found_app="$(bundle_id_path_macos 'com.openai.codex' || true)"
    if [[ -z "${found_app}" ]]; then
      found_app="$(app_exists_macos 'ChatGPT' || true)"
    fi
    if [[ -n "${found_app}" ]]; then
      CODEX_APP="${found_app}"
      DETECTED_CODEX=1
      if [[ -z "${CODEX_CLI}" && -x "${found_app}/Contents/Resources/codex" ]]; then
        CODEX_CLI="${found_app}/Contents/Resources/codex"
      fi
    fi
  fi

  # Config/skills presence alone is not enough to claim Codex is "available".
  return 0
}

detect_claude() {
  DETECTED_CLAUDE=0
  CLAUDE_CLI=""
  CLAUDE_APP=""

  local found_cli found_app
  found_cli="$(find_first_executable \
    "$(resolve_cli_from_whence claude 2>/dev/null || true)" \
    "${HOME}/.local/bin/claude" \
    "/opt/homebrew/bin/claude" \
    "/usr/local/bin/claude" \
    || true)"

  if [[ -n "${found_cli}" ]]; then
    CLAUDE_CLI="${found_cli}"
    DETECTED_CLAUDE=1
  fi

  if [[ "$(os_name)" == "macos" ]]; then
    found_app="$(app_exists_macos 'Claude' || true)"
    if [[ -z "${found_app}" ]]; then
      found_app="$(bundle_id_path_macos 'com.anthropic.claudefordesktop' || true)"
    fi
    if [[ -n "${found_app}" ]]; then
      CLAUDE_APP="${found_app}"
      DETECTED_CLAUDE=1
    fi
  fi

  # Claude Code is primarily a CLI; also accept a usable ~/.claude install
  # only when the `claude` binary itself is present.
  return 0
}

detect_cursor() {
  DETECTED_CURSOR=0
  CURSOR_CLI=""
  CURSOR_APP=""

  local found_cli found_app
  found_cli="$(find_first_executable \
    "$(resolve_cli_from_whence cursor 2>/dev/null || true)" \
    "/Applications/Cursor.app/Contents/Resources/app/bin/cursor" \
    "${HOME}/.local/bin/cursor" \
    "/opt/homebrew/bin/cursor" \
    "/usr/local/bin/cursor" \
    || true)"

  if [[ -n "${found_cli}" ]]; then
    CURSOR_CLI="${found_cli}"
    DETECTED_CURSOR=1
  fi

  if [[ "$(os_name)" == "macos" ]]; then
    found_app="$(app_exists_macos 'Cursor' || true)"
    if [[ -z "${found_app}" ]]; then
      found_app="$(bundle_id_path_macos 'com.todesktop.230313mzl4w4u92' || true)"
    fi
    if [[ -n "${found_app}" ]]; then
      CURSOR_APP="${found_app}"
      DETECTED_CURSOR=1
      if [[ -z "${CURSOR_CLI}" && -x "${found_app}/Contents/Resources/app/bin/cursor" ]]; then
        CURSOR_CLI="${found_app}/Contents/Resources/app/bin/cursor"
      fi
    fi
  fi

  return 0
}

detect_zotero() {
  DETECTED_ZOTERO=0
  ZOTERO_APP=""

  local found_app found_cli
  found_cli="$(resolve_cli_from_whence zotero 2>/dev/null || true)"
  if [[ -n "${found_cli}" ]]; then
    DETECTED_ZOTERO=1
    ZOTERO_APP="${found_cli}"
  fi

  if [[ "$(os_name)" == "macos" ]]; then
    found_app="$(app_exists_macos 'Zotero' || true)"
    if [[ -z "${found_app}" ]]; then
      found_app="$(bundle_id_path_macos 'org.zotero.zotero' || true)"
    fi
    if [[ -n "${found_app}" ]]; then
      DETECTED_ZOTERO=1
      ZOTERO_APP="${found_app}"
    fi
  elif [[ "$(os_name)" == "linux" ]]; then
    if command -v flatpak >/dev/null 2>&1 && flatpak info org.zotero.Zotero >/dev/null 2>&1; then
      DETECTED_ZOTERO=1
      ZOTERO_APP="flatpak:org.zotero.Zotero"
    fi
  fi

  return 0
}

detect_all() {
  detect_codex
  detect_claude
  detect_cursor
  detect_zotero
  DETECTED_ASSISTANT_COUNT=$((DETECTED_CODEX + DETECTED_CLAUDE + DETECTED_CURSOR))
}

print_detection_report() {
  section "环境检测"

  if (( DETECTED_CODEX )); then
    ok "Codex: 已检测到"
    [[ -n "${CODEX_APP}" ]] && log "  App : ${CODEX_APP}"
    [[ -n "${CODEX_CLI}" ]] && log "  CLI : ${CODEX_CLI}"
    log "  Skills dir: ${CODEX_SKILLS_DIR}"
  else
    fail "Codex: 未检测到"
  fi

  if (( DETECTED_CLAUDE )); then
    ok "Claude Code: 已检测到"
    [[ -n "${CLAUDE_APP}" ]] && log "  App : ${CLAUDE_APP}"
    [[ -n "${CLAUDE_CLI}" ]] && log "  CLI : ${CLAUDE_CLI}"
    log "  Skills dir: ${CLAUDE_SKILLS_DIR}"
  else
    fail "Claude Code: 未检测到"
  fi

  if (( DETECTED_CURSOR )); then
    ok "Cursor: 已检测到"
    [[ -n "${CURSOR_APP}" ]] && log "  App : ${CURSOR_APP}"
    [[ -n "${CURSOR_CLI}" ]] && log "  CLI : ${CURSOR_CLI}"
    log "  Skills dir: ${CURSOR_SKILLS_DIR}"
  else
    fail "Cursor: 未检测到"
  fi

  if (( DETECTED_ZOTERO )); then
    ok "Zotero: 已检测到"
    log "  Path: ${ZOTERO_APP}"
  else
    fail "Zotero: 未检测到"
  fi
}

print_missing_download_hints() {
  section "请先安装缺失应用，然后重新运行安装脚本"

  if (( DETECTED_ASSISTANT_COUNT == 0 )); then
    warn "需要至少安装以下任一编码助手："
    log "  - Codex:       ${URL_CODEX}"
    log "  - Claude Code: ${URL_CLAUDE_CODE}"
    log "  - Cursor:      ${URL_CURSOR}"
  fi

  if (( DETECTED_ZOTERO == 0 )); then
    warn "需要安装 Zotero："
    log "  - Zotero: ${URL_ZOTERO}"
  fi

  log ""
  log "安装完成后，在本目录重新执行："
  log "  bash ./install.sh"
}

assert_prerequisites() {
  detect_all
  print_detection_report

  local missing=0
  if (( DETECTED_ASSISTANT_COUNT == 0 )); then
    missing=1
  fi
  if (( DETECTED_ZOTERO == 0 )); then
    missing=1
  fi

  if (( missing )); then
    print_missing_download_hints
    return 1
  fi

  ok "前置应用检测通过（编码助手 ${DETECTED_ASSISTANT_COUNT} 个 + Zotero）"
  return 0
}

target_skill_dirs() {
  # Print skill directories for every detected assistant.
  if (( DETECTED_CODEX )); then
    printf '%s\n' "${CODEX_SKILLS_DIR}"
  fi
  if (( DETECTED_CLAUDE )); then
    printf '%s\n' "${CLAUDE_SKILLS_DIR}"
  fi
  if (( DETECTED_CURSOR )); then
    printf '%s\n' "${CURSOR_SKILLS_DIR}"
  fi
}
