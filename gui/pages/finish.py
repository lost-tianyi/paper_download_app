from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.i18n import t
from core.prompts import build_workflow_starter_prompt
from gui.pages.base import BasePage
from gui.widgets import COLORS, copy_to_clipboard, status_label, ui_font


class FinishPage(BasePage):
    title_key = "finish_title"
    subtitle_key = "finish_subtitle"

    def build(self) -> None:
        self.status_host = ttk.Frame(self.body, style="Panel.TFrame")
        self.status_host.pack(fill="x")

        self.how_title = ttk.Label(
            self.body, text=t("finish_how_title"), style="Body.TLabel"
        )
        self.how_title.pack(anchor="w", pady=(16, 6))

        self._step_keys = ("finish_step_1", "finish_step_2", "finish_step_3")
        self.step_labels: list[ttk.Label] = []
        for _key in self._step_keys:
            lbl = ttk.Label(self.body, text="", style="Muted.TLabel")
            lbl.pack(anchor="w", pady=2)
            self.step_labels.append(lbl)

        topic_box = tk.Frame(
            self.body,
            bg=COLORS["accent_soft"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        topic_box.pack(fill="both", expand=True, pady=(18, 0))

        self.topic_title = tk.Label(
            topic_box,
            text=t("finish_topic_title"),
            bg=COLORS["accent_soft"],
            fg=COLORS["text"],
            font=ui_font(12, "bold"),
            anchor="w",
        )
        self.topic_title.pack(fill="x", padx=14, pady=(12, 2))
        self.topic_hint = tk.Label(
            topic_box,
            text=t("finish_topic_hint"),
            bg=COLORS["accent_soft"],
            fg=COLORS["muted"],
            font=ui_font(11),
            anchor="w",
            justify="left",
            wraplength=640,
        )
        self.topic_hint.pack(fill="x", padx=14, pady=(0, 8))

        entry_row = tk.Frame(topic_box, bg=COLORS["accent_soft"])
        entry_row.pack(fill="x", padx=14, pady=(0, 8))
        self.topic_label = tk.Label(
            entry_row,
            text=t("finish_topic_label"),
            bg=COLORS["accent_soft"],
            fg=COLORS["text"],
            font=ui_font(11),
        )
        self.topic_label.pack(side="left")
        self.topic_var = tk.StringVar()
        self.topic_entry = ttk.Entry(entry_row, textvariable=self.topic_var, width=48)
        self.topic_entry.pack(side="left", padx=(8, 0), fill="x", expand=True)

        btn_row = tk.Frame(topic_box, bg=COLORS["accent_soft"])
        btn_row.pack(fill="x", padx=14, pady=(0, 8))
        self.generate_btn = ttk.Button(
            btn_row,
            text=t("finish_generate"),
            style="Nav.TButton",
            command=self._generate,
        )
        self.generate_btn.pack(side="left")
        self.copy_btn = ttk.Button(
            btn_row,
            text=t("finish_copy_recommended"),
            style="Accent.TButton",
            command=self._copy_starter,
        )
        self.copy_btn.pack(side="left", padx=(8, 0))

        self.preview_label = tk.Label(
            topic_box,
            text=t("finish_preview"),
            bg=COLORS["accent_soft"],
            fg=COLORS["text"],
            font=ui_font(11, "bold"),
            anchor="w",
        )
        self.preview_label.pack(fill="x", padx=14, pady=(4, 2))

        self.preview = tk.Text(
            topic_box,
            height=7,
            wrap="word",
            font=ui_font(11),
            bg="#F8FAFC",
            fg=COLORS["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        self.preview.pack(fill="both", expand=True, padx=14, pady=(0, 8))

        self.copy_feedback = tk.Label(
            topic_box,
            text="",
            bg=COLORS["accent_soft"],
            fg=COLORS["ok"],
            font=ui_font(11),
            anchor="w",
        )
        self.copy_feedback.pack(fill="x", padx=14, pady=(0, 10))

        self.note_label = ttk.Label(self.body, text=t("finish_note"), style="Muted.TLabel")
        self.note_label.pack(anchor="w", pady=(12, 0))

        self._starter = ""
        self._retranslate_static()

    def _retranslate_static(self) -> None:
        self.how_title.configure(text=t("finish_how_title"))
        for i, (key, lbl) in enumerate(zip(self._step_keys, self.step_labels), 1):
            lbl.configure(text=f"{i}. {t(key)}")
        self.topic_title.configure(text=t("finish_topic_title"))
        self.topic_hint.configure(text=t("finish_topic_hint"))
        self.topic_label.configure(text=t("finish_topic_label"))
        self.generate_btn.configure(text=t("finish_generate"))
        self.copy_btn.configure(text=t("finish_copy_recommended"))
        self.preview_label.configure(text=t("finish_preview"))
        self.note_label.configure(text=t("finish_note"))

    def _flash(self, message: str) -> None:
        self.copy_feedback.configure(text=message, fg=COLORS["ok"])
        self.app.root.after(2500, lambda: self.copy_feedback.configure(text=""))

    def _generate(self) -> None:
        topic = self.topic_var.get().strip()
        if not topic:
            self.copy_feedback.configure(text=t("finish_need_topic"), fg=COLORS["fail"])
            return
        self._starter = build_workflow_starter_prompt(topic, lang=self.app.lang)
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", self._starter)
        self._flash(t("finish_generated"))

    def _copy_starter(self) -> None:
        if not self._starter.strip():
            self._generate()
        if not self._starter.strip():
            return
        copy_to_clipboard(self.app.root, self._starter)
        self._flash(t("finish_copied_recommended"))

    def on_show(self) -> None:
        super().on_show()
        self._retranslate_static()
        for child in self.status_host.winfo_children():
            child.destroy()
        installed = bool(self.app.install_ok)
        tested = bool(self.app.tests_ok)
        if installed and tested:
            status_label(self.status_host, t("finish_ok"), True).pack(anchor="w")
        elif installed:
            status_label(self.status_host, t("finish_partial"), None).pack(anchor="w")
        else:
            status_label(self.status_host, t("finish_fail"), False).pack(anchor="w")
            self.generate_btn.configure(state="disabled")
            self.copy_btn.configure(state="disabled")
            return
        self.generate_btn.configure(state="normal")
        self.copy_btn.configure(state="normal")

    def next_label(self) -> str:
        return t("close")

    def back_enabled(self) -> bool:
        return True

    def on_next(self) -> bool:
        self.app.root.destroy()
        return False
