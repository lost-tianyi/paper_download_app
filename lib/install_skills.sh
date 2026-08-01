#!/usr/bin/env bash
# Install literature-review skills from offline bundled/ packages.

set -euo pipefail

# shellcheck disable=SC1091
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/detect.sh"

BUNDLED_SKILLS_DIR="${INSTALLER_ROOT}/bundled/skills"
BUNDLED_WHEELS_DIR="${INSTALLER_ROOT}/bundled/wheels"

install_one_skill_from_bundle() {
  local name="$1"
  local target_root="$2"
  local source_dir="${BUNDLED_SKILLS_DIR}/${name}"
  local target_dir="${target_root}/${name}"

  [[ -f "${source_dir}/SKILL.md" ]] || die "安装包缺少离线技能: ${source_dir}"

  if [[ -f "${target_dir}/SKILL.md" ]]; then
    info "覆盖已有技能: ${target_dir}"
  fi

  if is_truthy "${DRY_RUN:-0}"; then
    log "  [dry-run] copy ${source_dir}/ -> ${target_dir}/"
    return 0
  fi

  mkdir -p "${target_root}"
  rm -rf "${target_dir}"
  mkdir -p "${target_dir}"

  if command -v rsync >/dev/null 2>&1; then
    rsync -a \
      --exclude '.git' \
      --exclude '.github' \
      --exclude '__pycache__' \
      --exclude '.DS_Store' \
      "${source_dir}/" "${target_dir}/"
  else
    tar -C "${source_dir}" \
      --exclude '.git' \
      --exclude '.github' \
      --exclude '__pycache__' \
      --exclude '.DS_Store' \
      -cf - . | tar -C "${target_dir}" -xf -
  fi

  [[ -f "${target_dir}/SKILL.md" ]] || die "安装失败，未找到 ${target_dir}/SKILL.md"
  ok "已安装 ${name} -> ${target_dir}"
}

install_python_deps_for_download_skill() {
  local skill_dir="$1"
  local req="${skill_dir}/scripts/requirements.txt"

  [[ -f "${req}" ]] || return 0
  if [[ ! -d "${BUNDLED_WHEELS_DIR}" ]] || ! ls "${BUNDLED_WHEELS_DIR}"/*.whl >/dev/null 2>&1; then
    warn "未找到离线 wheels，跳过 pip"
    return 0
  fi

  require_cmd python3
  info "离线安装下载技能 Python 依赖"
  if is_truthy "${DRY_RUN:-0}"; then
    log "  [dry-run] pip install --no-index --find-links=${BUNDLED_WHEELS_DIR} -r ${req}"
    return 0
  fi

  python3 -m pip install --user --no-index --find-links="${BUNDLED_WHEELS_DIR}" -r "${req}" \
    >/tmp/literature-workflow-pip.log 2>&1 \
    || warn "离线 pip 未完全成功，详见 /tmp/literature-workflow-pip.log"
}

install_all_skills() {
  section "安装 Skills（离线）"
  [[ -d "${BUNDLED_SKILLS_DIR}" ]] || die "缺少 ${BUNDLED_SKILLS_DIR}，请先运行 bash build/vendor_skills.sh"

  local targets=()
  local dir
  while IFS= read -r dir; do
    [[ -n "${dir}" ]] && targets+=("${dir}")
  done < <(target_skill_dirs)

  (( ${#targets[@]} > 0 )) || die "未找到可用的技能安装目录"

  local spec name target first_download_skill=""
  while IFS= read -r spec; do
    [[ -z "${spec}" ]] && continue
    name="$(parse_skill_field "${spec}" name)"
    info "${name}: $(parse_skill_field "${spec}" desc)"
    for target in "${targets[@]}"; do
      install_one_skill_from_bundle "${name}" "${target}"
    done
    if [[ "${name}" == "sciencedirect-live-session-fetcher" ]]; then
      first_download_skill="${targets[0]}/${name}"
    fi
  done < <(skill_specs)

  if [[ -n "${first_download_skill}" ]]; then
    install_python_deps_for_download_skill "${first_download_skill}"
  fi

  ok "Skills 安装完成（全部来自安装包内置素材）"
}

verify_skill_layout() {
  local target name path missing=0
  section "校验 Skills 布局"

  while IFS= read -r target; do
    [[ -z "${target}" ]] && continue
    while IFS= read -r spec; do
      name="$(parse_skill_field "${spec}" name)"
      path="${target}/${name}/SKILL.md"
      if [[ -f "${path}" ]]; then
        ok "${path}"
      else
        fail "缺失: ${path}"
        missing=1
      fi
    done < <(skill_specs)
  done < <(target_skill_dirs)

  (( missing == 0 )) || die "Skills 布局校验失败"
}
