from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.i18n import set_language, t
from gui.pages.base import BasePage
from gui.widgets import COLORS, ui_font


class LanguagePage(BasePage):
    title_key = "lang_title"
    subtitle_key = "lang_subtitle"

    def build(self) -> None:
        self.lang_var = tk.StringVar(value=getattr(self.app, "lang", "zh") or "zh")

        self.box = tk.Frame(
            self.body,
            bg=COLORS["accent_soft"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        self.box.pack(fill="x", pady=(8, 0))

        self.brand = tk.Label(
            self.box,
            text="Literature Review Installer",
            bg=COLORS["accent_soft"],
            fg=COLORS["text"],
            font=ui_font(16, "bold"),
            anchor="w",
        )
        self.brand.pack(fill="x", padx=18, pady=(16, 4))
        self.sub = tk.Label(
            self.box,
            text=t("lang_subtitle"),
            bg=COLORS["accent_soft"],
            fg=COLORS["muted"],
            font=ui_font(11),
            anchor="w",
        )
        self.sub.pack(fill="x", padx=18, pady=(0, 12))

        row = tk.Frame(self.box, bg=COLORS["accent_soft"])
        row.pack(fill="x", padx=18, pady=(0, 16))

        self.rb_zh = ttk.Radiobutton(
            row,
            text=t("lang_zh"),
            value="zh",
            variable=self.lang_var,
            command=self._on_pick,
        )
        self.rb_zh.pack(anchor="w", pady=4)
        self.rb_en = ttk.Radiobutton(
            row,
            text=t("lang_en"),
            value="en",
            variable=self.lang_var,
            command=self._on_pick,
        )
        self.rb_en.pack(anchor="w", pady=4)

        self.hint = ttk.Label(self.body, text=t("lang_hint"), style="Muted.TLabel")
        self.hint.pack(anchor="w", pady=(16, 0))

    def _retranslate(self) -> None:
        self.refresh_header()
        self.sub.configure(text=t("lang_subtitle"))
        self.rb_zh.configure(text=t("lang_zh"))
        self.rb_en.configure(text=t("lang_en"))
        self.hint.configure(text=t("lang_hint"))

    def _on_pick(self) -> None:
        lang = self.lang_var.get()
        self.app.lang = lang
        set_language(lang)
        self.app.apply_language(rebuild_pages=False)
        self._retranslate()

    def on_show(self) -> None:
        self.lang_var.set(getattr(self.app, "lang", "zh") or "zh")
        self._retranslate()

    def on_next(self) -> bool:
        lang = self.lang_var.get() or "zh"
        self.app.lang = lang
        set_language(lang)
        self.app.apply_language(rebuild_pages=True)
        return True

    def next_label(self) -> str:
        return t("next")

    def back_enabled(self) -> bool:
        return False
