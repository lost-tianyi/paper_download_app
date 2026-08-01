#!/usr/bin/env bash
# Build LiteratureReviewInstaller.app and package it into a branded .dmg
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="${ROOT}/dist"
BUILD="${ROOT}/build/pyi-build"
APP_NAME="LiteratureReviewInstaller"
DMG_NAME="${APP_NAME}-macOS.dmg"
ICON_ICNS="${ROOT}/assets/app-icon.icns"
ICON_PNG="${ROOT}/assets/app-icon-256.png"
SET_ICON="${ROOT}/build/set_file_icon.py"

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
RW_DMG="${BUILD}/${APP_NAME}-rw.dmg"
rm -rf "${STAGE}"
mkdir -p "${STAGE}"
cp -R "${APP_PATH}" "${STAGE}/"
xattr -cr "${STAGE}/${APP_NAME}.app" 2>/dev/null || true
ln -s /Applications "${STAGE}/Applications"

# Volume icon shown when the DMG is opened
if [[ -f "${ICON_ICNS}" ]]; then
  cp "${ICON_ICNS}" "${STAGE}/.VolumeIcon.icns"
fi

echo "==> Creating read-write DMG (for volume icon)"
rm -f "${RW_DMG}"
hdiutil create \
  -volname "Literature Review Installer" \
  -srcfolder "${STAGE}" \
  -ov \
  -format UDRW \
  "${RW_DMG}"

echo "==> Mounting DMG to enable custom volume icon"
MOUNT_POINT="$(mktemp -d "${BUILD}/dmg-mount.XXXXXX")"
# detach any previous volume with same name
hdiutil detach "/Volumes/Literature Review Installer" -force 2>/dev/null || true
ATTACH_OUT="$(hdiutil attach -readwrite -noverify -noautoopen -mountpoint "${MOUNT_POINT}" "${RW_DMG}")"
DEVICE="$(echo "${ATTACH_OUT}" | awk 'NR==1 {print $1}')"

if [[ -f "${MOUNT_POINT}/.VolumeIcon.icns" ]]; then
  # Mark volume as having a custom icon
  if command -v SetFile >/dev/null 2>&1; then
    SetFile -a C "${MOUNT_POINT}" || true
  else
    # Fallback: Finder custom-icon flag via Python/osascript on the mount root
    python3 "${SET_ICON}" "${ICON_PNG:-${ICON_ICNS}}" "${MOUNT_POINT}" || true
  fi
fi

sync
hdiutil detach "${DEVICE}" -force
rmdir "${MOUNT_POINT}" 2>/dev/null || true

echo "==> Compressing DMG"
rm -f "${DIST}/${DMG_NAME}"
hdiutil convert "${RW_DMG}" -format UDZO -imagekey zlib-level=9 -o "${DIST}/${DMG_NAME}"
rm -f "${RW_DMG}"

echo "==> Applying Finder icon to the .dmg file itself"
ICON_FOR_FILE="${ICON_PNG}"
if [[ ! -f "${ICON_FOR_FILE}" ]]; then
  ICON_FOR_FILE="${ICON_ICNS}"
fi
if [[ -f "${ICON_FOR_FILE}" ]]; then
  python3 "${SET_ICON}" "${ICON_FOR_FILE}" "${DIST}/${DMG_NAME}" || \
    echo "[WARN] Could not set Finder icon on DMG (app icon inside DMG is still branded)"
fi

# Touch so Finder refreshes icon cache
touch "${DIST}/${DMG_NAME}" || true

echo "[OK] macOS installer ready:"
echo "  ${DIST}/${DMG_NAME}"
echo "  ${APP_PATH}"
echo "说明：.dmg 与打开后的卷标应显示自定义图标；.app 本身也已带图标。"
echo "     Windows 的 .exe 图标只在 Windows 资源管理器中显示，macOS Finder 会显示通用文档图标。"
