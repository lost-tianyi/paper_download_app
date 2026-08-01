#!/usr/bin/env bash
# Shared helpers for the literature-review workflow installer.

set -euo pipefail

INSTALLER_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1091
source "${INSTALLER_ROOT}/config/skills.conf"

if [[ -t 1 ]]; then
  C_RESET=$'\033[0m'
  C_BOLD=$'\033[1m'
  C_DIM=$'\033[2m'
  C_GREEN=$'\033[32m'
  C_YELLOW=$'\033[33m'
  C_RED=$'\033[31m'
  C_CYAN=$'\033[36m'
else
  C_RESET="" C_BOLD="" C_DIM="" C_GREEN="" C_YELLOW="" C_RED="" C_CYAN=""
fi

# User-facing messages go to stderr so command substitutions stay clean.
log()  { printf '%s\n' "$*" >&2; }
info() { printf '%s==>%s %s\n' "${C_CYAN}" "${C_RESET}" "$*" >&2; }
ok()   { printf '%s[OK]%s %s\n' "${C_GREEN}" "${C_RESET}" "$*" >&2; }
warn() { printf '%s[WARN]%s %s\n' "${C_YELLOW}" "${C_RESET}" "$*" >&2; }
fail() { printf '%s[FAIL]%s %s\n' "${C_RED}" "${C_RESET}" "$*" >&2; }
die()  { printf '%s[FAIL]%s %s\n' "${C_RED}" "${C_RESET}" "$*" >&2; exit 1; }

section() {
  printf '\n%s%s%s\n' "${C_BOLD}" "$*" "${C_RESET}" >&2
  printf '%s\n' "------------------------------------------------------------" >&2
}

require_cmd() {
  local cmd="$1"
  command -v "${cmd}" >/dev/null 2>&1 || die "缺少依赖命令: ${cmd}"
}

expand_home() {
  local path="$1"
  if [[ "${path}" == ~* ]]; then
    printf '%s\n' "${HOME}${path:1}"
  else
    printf '%s\n' "${path}"
  fi
}

is_truthy() {
  case "${1:-}" in
    1|true|TRUE|yes|YES|y|Y) return 0 ;;
    *) return 1 ;;
  esac
}

parse_skill_field() {
  # usage: parse_skill_field "$SPEC" name|url|subdir|desc
  local spec="$1"
  local field="$2"
  local name url subdir desc
  IFS='|' read -r name url subdir desc <<<"${spec}"
  case "${field}" in
    name) printf '%s\n' "${name}" ;;
    url) printf '%s\n' "${url}" ;;
    subdir) printf '%s\n' "${subdir}" ;;
    desc) printf '%s\n' "${desc}" ;;
    *) die "未知 skill 字段: ${field}" ;;
  esac
}

skill_specs() {
  printf '%s\n' "${ACADEMIC_SEARCH_SKILL}"
  printf '%s\n' "${DOWNLOAD_SKILL}"
}

os_name() {
  case "$(uname -s)" in
    Darwin) printf 'macos\n' ;;
    Linux) printf 'linux\n' ;;
    MINGW*|MSYS*|CYGWIN*) printf 'windows\n' ;;
    *) printf 'unknown\n' ;;
  esac
}

app_exists_macos() {
  local app_name="$1"
  local candidate
  for candidate in \
    "/Applications/${app_name}.app" \
    "${HOME}/Applications/${app_name}.app"; do
    if [[ -d "${candidate}" ]]; then
      printf '%s\n' "${candidate}"
      return 0
    fi
  done
  return 1
}

bundle_id_path_macos() {
  local bundle_id="$1"
  if command -v mdfind >/dev/null 2>&1; then
    mdfind "kMDItemCFBundleIdentifier == '${bundle_id}'" 2>/dev/null | head -n 1
  fi
}
