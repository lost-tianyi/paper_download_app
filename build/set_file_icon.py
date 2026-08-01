#!/usr/bin/env python3
"""Set a custom Finder icon on a file/folder using AppKit (macOS only)."""

from __future__ import annotations

import sys


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: set_file_icon.py <icon.png|icns> <target>", file=sys.stderr)
        return 2
    icon_path, target_path = sys.argv[1], sys.argv[2]
    try:
        from AppKit import NSImage, NSWorkspace  # type: ignore
    except ImportError:
        # Fallback via AppleScript/ObjC bridge (no pyobjc required)
        import subprocess

        script = f'''
        use framework "AppKit"
        set img to current application's NSImage's alloc()'s initWithContentsOfFile:"{icon_path}"
        if img is missing value then error "failed to load icon"
        set ws to current application's NSWorkspace's sharedWorkspace()
        set ok to ws's setIcon:img forFile:"{target_path}" options:0
        if (ok as integer) is 0 then error "setIcon failed"
        '''
        r = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            print(r.stderr or r.stdout, file=sys.stderr)
            return 1
        return 0

    image = NSImage.alloc().initWithContentsOfFile_(icon_path)
    if image is None:
        print(f"failed to load icon: {icon_path}", file=sys.stderr)
        return 1
    ok = NSWorkspace.sharedWorkspace().setIcon_forFile_options_(image, target_path, 0)
    if not ok:
        print(f"setIcon failed for: {target_path}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
