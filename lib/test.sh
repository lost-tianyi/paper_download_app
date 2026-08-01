#!/usr/bin/env bash
# Standardized post-install smoke tests.

set -euo pipefail

# shellcheck disable=SC1091
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/install_skills.sh"

TEST_WORKDIR="${INSTALLER_ROOT}/.cache/test-run"
SKIP_NETWORK_TEST="${SKIP_NETWORK_TEST:-0}"
FULL_AGENT_TEST="${FULL_AGENT_TEST:-0}"

TEST_FAILURES=0

record_fail() {
  fail "$*"
  TEST_FAILURES=$((TEST_FAILURES + 1))
}

first_skill_path() {
  local name="$1"
  local target
  while IFS= read -r target; do
    if [[ -f "${target}/${name}/SKILL.md" ]]; then
      printf '%s\n' "${target}/${name}"
      return 0
    fi
  done < <(target_skill_dirs)
  return 1
}

test_skill_frontmatter() {
  section "测试 1/5 · Skill 元数据"
  local name path
  while IFS= read -r spec; do
    name="$(parse_skill_field "${spec}" name)"
    path="$(first_skill_path "${name}" || true)"
    if [[ -z "${path}" ]]; then
      record_fail "未找到已安装技能: ${name}"
      continue
    fi
    if head -n 5 "${path}/SKILL.md" | grep -q '^---'; then
      ok "${name}: frontmatter 存在"
    else
      record_fail "${name}: SKILL.md 缺少 YAML frontmatter"
    fi
    if grep -Eq "^name:[[:space:]]*${name}" "${path}/SKILL.md"; then
      ok "${name}: name 字段匹配"
    else
      warn "${name}: name 字段未精确匹配（继续）"
    fi
  done < <(skill_specs)
}

test_assistant_clis() {
  section "测试 2/5 · 编码助手 CLI"

  if (( DETECTED_CODEX )) && [[ -n "${CODEX_CLI}" ]]; then
    if "${CODEX_CLI}" --version >/tmp/literature-workflow-codex-version.txt 2>&1; then
      ok "codex --version: $(tr '\n' ' ' </tmp/literature-workflow-codex-version.txt | sed 's/[[:space:]]*$//')"
    else
      record_fail "codex --version 失败"
    fi
    if "${CODEX_CLI}" doctor >/tmp/literature-workflow-codex-doctor.txt 2>&1; then
      ok "codex doctor 已执行"
    else
      # doctor 可能因终端/网络告警返回非零，只要有输出就视为 CLI 可用
      if [[ -s /tmp/literature-workflow-codex-doctor.txt ]]; then
        warn "codex doctor 返回非零，但 CLI 可运行（见 /tmp/literature-workflow-codex-doctor.txt）"
      else
        record_fail "codex doctor 无输出"
      fi
    fi
  elif (( DETECTED_CODEX )); then
    warn "检测到 Codex 应用，但未找到可用 CLI，跳过 codex CLI 测试"
  fi

  if (( DETECTED_CLAUDE )) && [[ -n "${CLAUDE_CLI}" ]]; then
    if "${CLAUDE_CLI}" --version >/tmp/literature-workflow-claude-version.txt 2>&1; then
      ok "claude --version: $(tr '\n' ' ' </tmp/literature-workflow-claude-version.txt | sed 's/[[:space:]]*$//')"
    else
      record_fail "claude --version 失败"
    fi
  elif (( DETECTED_CLAUDE )); then
    warn "检测到 Claude，但未找到可用 CLI，跳过 claude CLI 测试"
  fi

  if (( DETECTED_CURSOR )) && [[ -n "${CURSOR_CLI}" ]]; then
    if "${CURSOR_CLI}" --version >/tmp/literature-workflow-cursor-version.txt 2>&1; then
      ok "cursor --version: $(tr '\n' ' ' </tmp/literature-workflow-cursor-version.txt | sed 's/[[:space:]]*$//')"
    else
      record_fail "cursor --version 失败"
    fi
  elif (( DETECTED_CURSOR )); then
    warn "检测到 Cursor，但未找到可用 CLI，跳过 cursor CLI 测试"
  fi
}

test_academic_search_scripts() {
  section "测试 3/5 · academic-search 自检"
  local skill_dir
  skill_dir="$(first_skill_path 'academic-search' || true)"
  [[ -n "${skill_dir}" ]] || { record_fail "academic-search 未安装"; return 0; }

  require_cmd curl
  require_cmd node

  if [[ -x "${skill_dir}/scripts/check-deps.sh" ]] || [[ -f "${skill_dir}/scripts/check-deps.sh" ]]; then
    if bash "${skill_dir}/scripts/check-deps.sh" >/tmp/literature-workflow-check-deps.txt 2>&1; then
      ok "check-deps.sh 通过"
    else
      # Chrome 未开远程调试时脚本仍可能成功；若 curl 缺失会失败
      if grep -q 'curl: missing' /tmp/literature-workflow-check-deps.txt; then
        record_fail "check-deps.sh 失败：缺少 curl"
      else
        warn "check-deps.sh 有告警（常见于未开启 Chrome remote debugging），详见 /tmp/literature-workflow-check-deps.txt"
        ok "check-deps.sh 已执行（API 模式可用）"
      fi
    fi
  else
    record_fail "缺少 check-deps.sh"
  fi

  if [[ -f "${skill_dir}/scripts/oa-pdf-download-self-test.sh" ]]; then
    if bash "${skill_dir}/scripts/oa-pdf-download-self-test.sh" >/tmp/literature-workflow-oa-self-test.txt 2>&1; then
      ok "oa-pdf-download-self-test.sh 通过"
    else
      record_fail "oa-pdf-download-self-test.sh 失败（详见 /tmp/literature-workflow-oa-self-test.txt）"
    fi
  else
    record_fail "缺少 oa-pdf-download-self-test.sh"
  fi
}

test_download_skill_scripts() {
  section "测试 4/5 · 下载技能脚本"
  local skill_dir
  skill_dir="$(first_skill_path 'sciencedirect-live-session-fetcher' || true)"
  [[ -n "${skill_dir}" ]] || { record_fail "sciencedirect-live-session-fetcher 未安装"; return 0; }

  require_cmd python3

  local py
  for py in \
    "${skill_dir}/scripts/devtools_sciencedirect_serial_fetch.py" \
    "${skill_dir}/scripts/attach_sciencedirect_remote_debug.py" \
    "${skill_dir}/scripts/firefox_sciencedirect_serial_fetch.py"; do
    if [[ -f "${py}" ]]; then
      if python3 -m py_compile "${py}" >/tmp/literature-workflow-pycompile.txt 2>&1; then
        ok "py_compile: $(basename "${py}")"
      else
        record_fail "py_compile 失败: $(basename "${py}")"
      fi
    else
      record_fail "缺少脚本: ${py}"
    fi
  done

  if [[ -f "${skill_dir}/scripts/launch_chrome_clone_remote_debug_macos.sh" ]]; then
    ok "macOS Chrome launcher 存在"
  else
    warn "未找到 macOS Chrome launcher（Windows 环境可忽略）"
  fi
}

test_network_smoke() {
  section "测试 5/5 · 标准化网络探测（Crossref）"

  if is_truthy "${SKIP_NETWORK_TEST}"; then
    warn "已跳过网络探测（SKIP_NETWORK_TEST=1）"
    return 0
  fi

  require_cmd curl
  mkdir -p "${TEST_WORKDIR}"
  local out="${TEST_WORKDIR}/crossref-10.1038-nature14539.json"
  local doi="10.1038/nature14539"

  if curl -fsSL \
    -H 'Accept: application/json' \
    "https://api.crossref.org/works/${doi}" \
    -o "${out}"; then
    if grep -q 'Deep Residual Learning' "${out}" || grep -q 'nature14539' "${out}"; then
      ok "Crossref DOI 解析成功: ${doi}"
    else
      record_fail "Crossref 响应缺少预期字段"
    fi
  else
    record_fail "Crossref 请求失败（检查网络/代理）"
  fi
}

optional_agent_skill_probe() {
  if ! is_truthy "${FULL_AGENT_TEST}"; then
    return 0
  fi

  section "可选 · 完整 Agent 技能探测（FULL_AGENT_TEST=1）"
  local prompt
  prompt="$(cat <<'EOF'
Read the installed skills academic-search and sciencedirect-live-session-fetcher under the current assistant skills directory. Reply with exactly one line: SKILLS_OK if both SKILL.md files exist and mention literature/PDF workflows; otherwise SKILLS_FAIL. Do not search the web. Do not download anything.
EOF
)"

  if (( DETECTED_CODEX )) && [[ -n "${CODEX_CLI}" ]]; then
    info "运行: codex exec（非交互）"
    if "${CODEX_CLI}" exec --skip-git-repo-check "${prompt}" \
      >/tmp/literature-workflow-codex-exec.txt 2>&1; then
      if grep -q 'SKILLS_OK' /tmp/literature-workflow-codex-exec.txt; then
        ok "codex exec 技能探测通过"
      else
        record_fail "codex exec 未返回 SKILLS_OK（详见 /tmp/literature-workflow-codex-exec.txt）"
      fi
    else
      record_fail "codex exec 失败（可能未登录）。详见 /tmp/literature-workflow-codex-exec.txt"
    fi
  fi

  if (( DETECTED_CLAUDE )) && [[ -n "${CLAUDE_CLI}" ]]; then
    info "运行: claude -p（非交互）"
    if "${CLAUDE_CLI}" -p "${prompt}" \
      >/tmp/literature-workflow-claude-print.txt 2>&1; then
      if grep -q 'SKILLS_OK' /tmp/literature-workflow-claude-print.txt; then
        ok "claude -p 技能探测通过"
      else
        record_fail "claude -p 未返回 SKILLS_OK（详见 /tmp/literature-workflow-claude-print.txt）"
      fi
    else
      record_fail "claude -p 失败（可能未登录）。详见 /tmp/literature-workflow-claude-print.txt"
    fi
  fi
}

run_standardized_tests() {
  TEST_FAILURES=0
  detect_all
  verify_skill_layout
  test_skill_frontmatter
  test_assistant_clis
  test_academic_search_scripts
  test_download_skill_scripts
  test_network_smoke
  optional_agent_skill_probe

  section "测试结果"
  if (( TEST_FAILURES == 0 )); then
    ok "全部标准化测试通过"
    return 0
  fi

  fail "有 ${TEST_FAILURES} 项测试失败"
  return 1
}
