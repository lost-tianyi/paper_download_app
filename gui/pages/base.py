"""Base wizard page."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from core.i18n import t
from gui.widgets import COLORS

if TYPE_CHECKING:
    from gui.app import InstallerApp


class BasePage(ttk.Frame):
    title = ""
    subtitle = ""
    title_key = ""
    subtitle_key = ""

    def __init__(self, master: tk.Misc, app: "InstallerApp") -> None:
        super().__init__(master, style="Panel.TFrame")
        self.app = app
        self._title_label: ttk.Label | None = None
        self._subtitle_label: ttk.Label | None = None
        self._resolve_texts()
        self._build_header()
        self.body = ttk.Frame(self, style="Panel.TFrame")
        self.body.pack(fill="both", expand=True, padx=28, pady=(8, 20))
        self.build()

    def _resolve_texts(self) -> None:
        if self.title_key:
            self.title = t(self.title_key)
        if self.subtitle_key:
            self.subtitle = t(self.subtitle_key)

    def _build_header(self) -> None:
        header = ttk.Frame(self, style="Panel.TFrame")
        header.pack(fill="x", padx=28, pady=(24, 0))
        self._title_label = ttk.Label(header, text=self.title, style="Title.TLabel")
        self._title_label.pack(anchor="w")
        self._subtitle_label = ttk.Label(header, text=self.subtitle, style="Muted.TLabel")
        self._subtitle_label.pack(anchor="w", pady=(6, 0))
        sep = tk.Frame(self, bg=COLORS["border"], height=1)
        sep.pack(fill="x", padx=28, pady=(16, 0))

    def refresh_header(self) -> None:
        self._resolve_texts()
        if self._title_label is not None:
            self._title_label.configure(text=self.title)
        if self._subtitle_label is not None:
            self._subtitle_label.configure(text=self.subtitle)

    def build(self) -> None:
        raise NotImplementedError

    def on_show(self) -> None:
        """Called when page becomes visible."""
        self.refresh_header()

    def can_continue(self) -> bool:
        return True

    def on_next(self) -> bool:
        """Return False to block navigation."""
        return True

    def next_label(self) -> str:
        return t("next")

    def back_enabled(self) -> bool:
        return True
