#!/usr/bin/env bash
# Build LiteratureReviewInstaller.app and package it into a .dmg
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="${ROOT}/dist"
BUILD="${ROOT}/build/pyi-build"
APP_NAME="LiteratureReviewInstaller"
DMG_NAME="${APP_NAME}-macOS.dmg"

cd "${ROOT}"

echo "==> Vendoring offline skills into bundled/"
bash "${ROOT}/build/vendor_skills.sh"

echo "==> Installing build dependency (pyinstaller)"
python3 -m pip install --user -q -r requirements-gui.txt

echo "==> Cleaning previous build outputs"
rm -rf "${DIST}/${APP_NAME}.app" "${DIST}/${APP_NAME}" "${DIST}/${DMG_NAME}" "${BUILD}"
mkdir -p "${DIST}" "${BUILD}"

echo "==> Running PyInstaller"
python3 -m PyInstaller \
  --noconfirm \
  --clean \
  --distpath "${DIST}" \
  --workpath "${BUILD}" \
  "${ROOT}/build/installer.spec"

APP_PATH="${DIST}/${APP_NAME}.app"
if [[ ! -d "${APP_PATH}" ]]; then
  echo "ERROR: expected app bundle at ${APP_PATH}" >&2
  exit 1
fi

# Clear Finder/resource-fork xattrs that break ad-hoc codesign on some volumes.
find "${APP_PATH}" -name '._*' -delete 2>/dev/null || true
xattr -cr "${APP_PATH}" 2>/dev/null || true
if command -v dot_clean >/dev/null 2>&1; then
  dot_clean -m "${APP_PATH}" 2>/dev/null || true
fi
codesign --force --deep -s - "${APP_PATH}" 2>/dev/null || true

STAGE="${BUILD}/dmg-stage"
rm -rf "${STAGE}"
mkdir -p "${STAGE}"
cp -R "${APP_PATH}" "${STAGE}/"
xattr -cr "${STAGE}/${APP_NAME}.app" 2>/dev/null || true
ln -s /Applications "${STAGE}/Applications"

echo "==> Creating DMG"
hdiutil create \
  -volname "Literature Review Installer" \
  -srcfolder "${STAGE}" \
  -ov \
  -format UDZO \
  "${DIST}/${DMG_NAME}"

echo "[OK] macOS installer ready:"
echo "  ${DIST}/${DMG_NAME}"
echo "  ${APP_PATH}"
