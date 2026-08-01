"""Base wizard page."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Optional

from gui.widgets import COLORS

if TYPE_CHECKING:
    from gui.app import InstallerApp


class BasePage(ttk.Frame):
    title = ""
    subtitle = ""

    def __init__(self, master: tk.Misc, app: "InstallerApp") -> None:
        super().__init__(master, style="Panel.TFrame")
        self.app = app
        self._build_header()
        self.body = ttk.Frame(self, style="Panel.TFrame")
        self.body.pack(fill="both", expand=True, padx=28, pady=(8, 20))
        self.build()

    def _build_header(self) -> None:
        header = ttk.Frame(self, style="Panel.TFrame")
        header.pack(fill="x", padx=28, pady=(24, 0))
        if self.title:
            ttk.Label(header, text=self.title, style="Title.TLabel").pack(anchor="w")
        if self.subtitle:
            ttk.Label(header, text=self.subtitle, style="Muted.TLabel").pack(
                anchor="w", pady=(6, 0)
            )
        sep = tk.Frame(self, bg=COLORS["border"], height=1)
        sep.pack(fill="x", padx=28, pady=(16, 0))

    def build(self) -> None:
        raise NotImplementedError

    def on_show(self) -> None:
        """Called when page becomes visible."""

    def can_continue(self) -> bool:
        return True

    def on_next(self) -> bool:
        """Return False to block navigation."""
        return True

    def next_label(self) -> str:
        return "下一步"

    def back_enabled(self) -> bool:
        return True
