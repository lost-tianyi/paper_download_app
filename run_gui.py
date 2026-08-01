#!/usr/bin/env python3
"""Launch the literature-review installer wizard (development entrypoint)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gui.app import run_wizard


def main() -> None:
    run_wizard()


if __name__ == "__main__":
    main()
