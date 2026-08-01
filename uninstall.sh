#!/usr/bin/env bash
# Remove literature-review skills installed by install.sh.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/lib/detect.sh"

detect_all

section "卸载 Literature Review Skills"

removed=0
while IFS= read -r target; do
  [[ -z "${target}" ]] && continue
  while IFS= read -r spec; do
    name="$(parse_skill_field "${spec}" name)"
    path="${target}/${name}"
    if [[ -d "${path}" ]]; then
      rm -rf "${path}"
      ok "已删除 ${path}"
      removed=$((removed + 1))
    fi
  done < <(skill_specs)
done < <(target_skill_dirs)

if [[ -d "${INSTALLER_ROOT}/.cache" ]]; then
  rm -rf "${INSTALLER_ROOT}/.cache"
  ok "已清理本地缓存 ${INSTALLER_ROOT}/.cache"
fi

if (( removed == 0 )); then
  warn "未找到可卸载的技能目录"
else
  ok "卸载完成（共删除 ${removed} 个技能目录）"
fi
