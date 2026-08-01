from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.config import APP_VERSION
from core.i18n import t
from gui.pages.base import BasePage
from gui.widgets import COLORS, ui_font


class WelcomePage(BasePage):
    title_key = "welcome_title"
    subtitle_key = "welcome_subtitle"

    def _resolve_texts(self) -> None:
        self.title = t("welcome_title")
        self.subtitle = t("welcome_subtitle", version=APP_VERSION)

    def build(self) -> None:
        self.hero = tk.Frame(
            self.body,
            bg=COLORS["accent_soft"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        self.hero.pack(fill="x", pady=(0, 16))
        self.hero_title = tk.Label(
            self.hero,
            text=t("welcome_hero"),
            bg=COLORS["accent_soft"],
            fg=COLORS["text"],
            font=ui_font(14, "bold"),
            anchor="w",
        )
        self.hero_title.pack(fill="x", padx=16, pady=(14, 4))
        self.hero_body = tk.Label(
            self.hero,
            text=t("welcome_hero_body"),
            bg=COLORS["accent_soft"],
            fg=COLORS["muted"],
            font=ui_font(11),
            anchor="w",
            justify="left",
            wraplength=620,
        )
        self.hero_body.pack(fill="x", padx=16, pady=(0, 14))

        self.body_host = ttk.Frame(self.body, style="Panel.TFrame")
        self.body_host.pack(fill="both", expand=True)
        self.footer = ttk.Label(self.body, text=t("welcome_footer"), style="Muted.TLabel")
        self.footer.pack(anchor="w", pady=(18, 0))
        self._fill_body()

    def _fill_body(self) -> None:
        for child in self.body_host.winfo_children():
            child.destroy()
        for line in t("welcome_body").split("\n"):
            ttk.Label(self.body_host, text=line, style="Body.TLabel").pack(anchor="w", pady=1)

    def on_show(self) -> None:
        self._resolve_texts()
        self.refresh_header()
        self.hero_title.configure(text=t("welcome_hero"))
        self.hero_body.configure(text=t("welcome_hero_body"))
        self.footer.configure(text=t("welcome_footer"))
        self._fill_body()

    def back_enabled(self) -> bool:
        return True
