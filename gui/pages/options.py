from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.config import SKILLS
from core.detect import ASSISTANT_LABELS
from core.i18n import feature_label, t
from core.install_skills import InstallOptions
from gui.pages.base import BasePage


class OptionsPage(BasePage):
    title_key = "options_title"
    subtitle_key = "options_subtitle"

    def build(self) -> None:
        self.dirs_frame = ttk.Frame(self.body, style="Panel.TFrame")
        self.dirs_frame.pack(fill="x")

        self.features_title = ttk.Label(
            self.body, text=t("options_features"), style="Body.TLabel"
        )
        self.features_title.pack(anchor="w", pady=(16, 4))
        self.feature_labels: list[ttk.Label] = []
        for spec in SKILLS:
            lbl = ttk.Label(
                self.body,
                text=f"• {feature_label(spec.name, spec.description)}",
                style="Muted.TLabel",
            )
            lbl.pack(anchor="w")
            self.feature_labels.append(lbl)

        self.force_var = tk.BooleanVar(value=False)
        self.skip_network_var = tk.BooleanVar(value=False)
        self.skip_python_deps_var = tk.BooleanVar(value=False)

        opts = ttk.Frame(self.body, style="Panel.TFrame")
        opts.pack(fill="x", pady=(20, 0))
        self.force_chk = ttk.Checkbutton(
            opts, text=t("options_force"), variable=self.force_var
        )
        self.force_chk.pack(anchor="w")
        self.skip_net_chk = ttk.Checkbutton(
            opts, text=t("options_skip_network"), variable=self.skip_network_var
        )
        self.skip_net_chk.pack(anchor="w", pady=(6, 0))
        self.skip_deps_chk = ttk.Checkbutton(
            opts, text=t("options_skip_deps"), variable=self.skip_python_deps_var
        )
        self.skip_deps_chk.pack(anchor="w", pady=(6, 0))

        self.note = ttk.Label(self.body, text=t("options_note"), style="Muted.TLabel")
        self.note.pack(anchor="w", pady=(18, 0))

    def on_show(self) -> None:
        self.refresh_header()
        self.features_title.configure(text=t("options_features"))
        for spec, lbl in zip(SKILLS, self.feature_labels):
            lbl.configure(text=f"• {feature_label(spec.name, spec.description)}")
        self.force_chk.configure(text=t("options_force"))
        self.skip_net_chk.configure(text=t("options_skip_network"))
        self.skip_deps_chk.configure(text=t("options_skip_deps"))
        self.note.configure(text=t("options_note"))

        for child in self.dirs_frame.winfo_children():
            child.destroy()
        detection = self.app.detection
        selected = tuple(getattr(self.app, "selected_assistants", ()) or ())

        ttk.Label(self.dirs_frame, text=t("options_selected"), style="Body.TLabel").pack(
            anchor="w"
        )
        if selected:
            labels = "、".join(ASSISTANT_LABELS.get(k, k) for k in selected)
            if getattr(self.app, "lang", "zh") == "en":
                labels = ", ".join(ASSISTANT_LABELS.get(k, k) for k in selected)
            ttk.Label(self.dirs_frame, text=f"• {labels}", style="Muted.TLabel").pack(
                anchor="w"
            )
        else:
            ttk.Label(
                self.dirs_frame, text=f"• {t('options_none')}", style="Muted.TLabel"
            ).pack(anchor="w")

        ttk.Label(
            self.dirs_frame, text=t("options_locations"), style="Body.TLabel"
        ).pack(anchor="w", pady=(10, 0))
        if detection is None:
            ttk.Label(
                self.dirs_frame, text=t("options_not_detected"), style="Muted.TLabel"
            ).pack(anchor="w")
            return
        targets = detection.target_skill_dirs(selected)
        if not targets:
            ttk.Label(
                self.dirs_frame,
                text=t("options_no_target"),
                style="Muted.TLabel",
            ).pack(anchor="w")
            return
        for path in targets:
            # Show assistant-friendly location, not raw skills jargon
            ttk.Label(self.dirs_frame, text=f"• {path}", style="Muted.TLabel").pack(
                anchor="w"
            )

    def on_next(self) -> bool:
        selected = tuple(getattr(self.app, "selected_assistants", ()) or ())
        self.app.options = InstallOptions(
            force=bool(self.force_var.get()),
            skip_network_test=bool(self.skip_network_var.get()),
            skip_python_deps=bool(self.skip_python_deps_var.get()),
            assistants=selected,
        )
        return True

    def next_label(self) -> str:
        return t("start_install")
