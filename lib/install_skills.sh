#!/usr/bin/env bash
# Clone/copy literature-review skills into assistant skill directories.

set -euo pipefail

# shellcheck disable=SC1091
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/detect.sh"

INSTALL_CACHE_DIR="${INSTALLER_ROOT}/.cache/skills"
FORCE_REINSTALL="${FORCE_REINSTALL:-0}"
DRY_RUN="${DRY_RUN:-0}"

ensure_git() {
  require_cmd git
}

refresh_skill_cache() {
  local name="$1"
  local url="$2"
  local dest="${INSTALL_CACHE_DIR}/${name}"

  mkdir -p "${INSTALL_CACHE_DIR}"

  if [[ -d "${dest}/.git" ]]; then
    info "更新缓存: ${name}"
    if is_truthy "${DRY_RUN}"; then
      log "  [dry-run] git -C ${dest} pull --ff-only"
    else
      git -C "${dest}" fetch --depth 1 origin HEAD >/dev/null 2>&1 || true
      git -C "${dest}" reset --hard FETCH_HEAD >/dev/null 2>&1 \
        || git -C "${dest}" pull --ff-only >/dev/null
    fi
  else
    info "克隆技能仓库: ${name}"
    if is_truthy "${DRY_RUN}"; then
      log "  [dry-run] git clone --depth 1 ${url} ${dest}"
    else
      rm -rf "${dest}"
      git clone --depth 1 "${url}" "${dest}" >/dev/null
    fi
  fi

  printf '%s\n' "${dest}"
}

install_one_skill_to_dir() {
  local name="$1"
  local cache_root="$2"
  local subdir="$3"
  local target_root="$4"
  local source_dir target_dir

  if [[ "${subdir}" == "." || -z "${subdir}" ]]; then
    source_dir="${cache_root}"
  else
    source_dir="${cache_root}/${subdir}"
  fi

  [[ -f "${source_dir}/SKILL.md" ]] || die "技能包缺少 SKILL.md: ${source_dir}"

  target_dir="${target_root}/${name}"

  if [[ -f "${target_dir}/SKILL.md" ]]; then
    info "覆盖已有技能: ${target_dir}"
  fi

  if is_truthy "${DRY_RUN}"; then
    log "  [dry-run] rsync ${source_dir}/ -> ${target_dir}/"
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
    # Portable fallback
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
  require_cmd python3

  info "安装下载技能 Python 依赖: ${req}"
  if is_truthy "${DRY_RUN}"; then
    log "  [dry-run] python3 -m pip install -r ${req}"
    return 0
  fi

  python3 -m pip install --user -r "${req}" >/tmp/literature-workflow-pip.log 2>&1 \
    || warn "Python 依赖安装未完全成功，详见 /tmp/literature-workflow-pip.log（后续测试会继续检查）"
}

install_all_skills() {
  ensure_git
  section "安装 Skills"

  local targets=()
  local dir
  while IFS= read -r dir; do
    [[ -n "${dir}" ]] && targets+=("${dir}")
  done < <(target_skill_dirs)

  (( ${#targets[@]} > 0 )) || die "未找到可用的技能安装目录"

  local spec name url subdir desc cache_root target first_download_skill=""
  while IFS= read -r spec; do
    [[ -z "${spec}" ]] && continue
    name="$(parse_skill_field "${spec}" name)"
    url="$(parse_skill_field "${spec}" url)"
    subdir="$(parse_skill_field "${spec}" subdir)"
    desc="$(parse_skill_field "${spec}" desc)"

    info "${name}: ${desc}"
    cache_root="$(refresh_skill_cache "${name}" "${url}")"

    for target in "${targets[@]}"; do
      install_one_skill_to_dir "${name}" "${cache_root}" "${subdir}" "${target}"
    done

    if [[ "${name}" == "sciencedirect-live-session-fetcher" ]]; then
      first_download_skill="${targets[0]}/${name}"
    fi
  done < <(skill_specs)

  if [[ -n "${first_download_skill}" ]]; then
    install_python_deps_for_download_skill "${first_download_skill}"
  fi

  ok "Skills 安装完成"
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
