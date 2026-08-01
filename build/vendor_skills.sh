#!/usr/bin/env bash
# Populate bundled/skills and bundled/wheels for offline installer packaging.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUNDLE="${ROOT}/bundled"
CACHE="${ROOT}/.cache/skills"
TMP="${ROOT}/.cache/vendor-tmp"

mkdir -p "${BUNDLE}/skills" "${BUNDLE}/wheels" "${CACHE}" "${TMP}"

clone_or_update() {
  local name="$1"
  local url="$2"
  local dest="${CACHE}/${name}"
  if [[ -d "${dest}/.git" ]]; then
    echo "==> Refresh cache: ${name}"
    git -C "${dest}" fetch --depth 1 origin HEAD >/dev/null 2>&1 || true
    git -C "${dest}" reset --hard FETCH_HEAD >/dev/null 2>&1 \
      || git -C "${dest}" pull --ff-only >/dev/null 2>&1 || true
  elif [[ ! -d "${dest}" ]]; then
    echo "==> Clone for vendoring: ${name}"
    git clone --depth 1 "${url}" "${dest}"
  fi
}

copy_tree() {
  local src="$1"
  local dst="$2"
  rm -rf "${dst}"
  mkdir -p "${dst}"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a \
      --exclude '.git' \
      --exclude '.github' \
      --exclude '__pycache__' \
      --exclude '.DS_Store' \
      "${src}/" "${dst}/"
  else
    tar -C "${src}" \
      --exclude '.git' \
      --exclude '.github' \
      --exclude '__pycache__' \
      --exclude '.DS_Store' \
      -cf - . | tar -C "${dst}" -xf -
  fi
}

# Prefer existing cache; only network if missing.
if [[ ! -f "${CACHE}/academic-search/SKILL.md" ]]; then
  clone_or_update "academic-search" "https://github.com/ustc-ai4science/academic-search.git"
fi
if [[ ! -f "${CACHE}/sciencedirect-live-session-fetcher/codex-skill/SKILL.md" ]]; then
  clone_or_update "sciencedirect-live-session-fetcher" "https://github.com/Given-Dream/sciencedirect-live-session-fetcher.git"
fi

echo "==> Vendoring installable skill packages into bundled/skills"
copy_tree "${CACHE}/academic-search" "${BUNDLE}/skills/academic-search"
copy_tree "${CACHE}/sciencedirect-live-session-fetcher/codex-skill" \
  "${BUNDLE}/skills/sciencedirect-live-session-fetcher"

REQ="${BUNDLE}/skills/sciencedirect-live-session-fetcher/scripts/requirements.txt"
if [[ -f "${REQ}" ]]; then
  echo "==> Downloading offline Python wheels"
  python3 -m pip download -q -r "${REQ}" -d "${BUNDLE}/wheels" || \
    echo "[WARN] wheel download incomplete; installer will skip offline pip if missing"
fi

cat > "${BUNDLE}/MANIFEST.txt" <<EOF
Offline skill bundle for Literature Review Installer
- academic-search
- sciencedirect-live-session-fetcher (codex-skill package)
Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
EOF

test -f "${BUNDLE}/skills/academic-search/SKILL.md"
test -f "${BUNDLE}/skills/sciencedirect-live-session-fetcher/SKILL.md"
echo "[OK] Bundled skills ready at ${BUNDLE}"
du -sh "${BUNDLE}" "${BUNDLE}/skills"/* "${BUNDLE}/wheels" 2>/dev/null || true
