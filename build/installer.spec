# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Literature Review Workflow Installer.
# Prefer using build_macos.sh / build_windows.ps1 which pass platform flags.

import sys
from pathlib import Path

# SPECPATH is the directory that contains this .spec file (PyInstaller convention).
SPECDIR = Path(SPECPATH).resolve()
ROOT = SPECDIR.parent

bundled = ROOT / "bundled"
if not (bundled / "skills" / "academic-search" / "SKILL.md").is_file():
    raise SystemExit(
        "bundled/skills missing. Run: bash build/vendor_skills.sh"
    )

datas = [
    (str(ROOT / "templates"), "templates"),
    (str(ROOT / "config"), "config"),
    (str(ROOT / "assets"), "assets"),
    (str(ROOT / "README.md"), "."),
    (str(bundled), "bundled"),
]

hiddenimports = [
    "gui",
    "gui.app",
    "gui.widgets",
    "gui.pages",
    "gui.pages.base",
    "gui.pages.language",
    "gui.pages.welcome",
    "gui.pages.detect",
    "gui.pages.options",
    "gui.pages.progress",
    "gui.pages.tests",
    "gui.pages.finish",
    "core",
    "core.config",
    "core.detect",
    "core.install_skills",
    "core.test_suite",
    "core.prompts",
    "core.i18n",
]

ICON_ICNS = ROOT / "assets" / "app-icon.icns"
ICON_ICO = ROOT / "assets" / "app-icon.ico"

block_cipher = None

a = Analysis(
    [str(ROOT / "run_gui.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe_name = "LiteratureReviewInstaller"

if sys.platform == "darwin":
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=exe_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=True,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=str(ICON_ICNS) if ICON_ICNS.is_file() else None,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name=exe_name,
    )
    app = BUNDLE(
        coll,
        name=f"{exe_name}.app",
        icon=str(ICON_ICNS) if ICON_ICNS.is_file() else None,
        bundle_identifier="com.literaturereview.installer",
        info_plist={
            "CFBundleName": "Literature Review Installer",
            "CFBundleDisplayName": "Literature Review Installer",
            "CFBundleShortVersionString": "1.2.1",
            "NSHighResolutionCapable": True,
        },
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name=exe_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=str(ICON_ICO) if ICON_ICO.is_file() else None,
    )
