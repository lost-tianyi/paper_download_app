from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.config import SKILLS
from core.detect import ASSISTANT_LABELS
from core.install_skills import InstallOptions
from gui.pages.base import BasePage


class OptionsPage(BasePage):
    title = "安装选项"
    subtitle = "确认将写入的目录与可选行为"

    def build(self) -> None:
        self.dirs_frame = ttk.Frame(self.body, style="Panel.TFrame")
        self.dirs_frame.pack(fill="x")

        ttk.Label(self.body, text="将安装的 Skills：", style="Body.TLabel").pack(
            anchor="w", pady=(16, 4)
        )
        for spec in SKILLS:
            ttk.Label(
                self.body,
                text=f"• {spec.name} — {spec.description}",
                style="Muted.TLabel",
            ).pack(anchor="w")

        self.force_var = tk.BooleanVar(value=False)
        self.skip_network_var = tk.BooleanVar(value=False)
        self.skip_python_deps_var = tk.BooleanVar(value=False)

        opts = ttk.Frame(self.body, style="Panel.TFrame")
        opts.pack(fill="x", pady=(20, 0))
        ttk.Checkbutton(
            opts,
            text="强制覆盖已安装的 Skills（默认也会覆盖同名技能）",
            variable=self.force_var,
        ).pack(anchor="w")
        ttk.Checkbutton(
            opts,
            text="跳过 Crossref 网络探测测试",
            variable=self.skip_network_var,
        ).pack(anchor="w", pady=(6, 0))
        ttk.Checkbutton(
            opts,
            text="跳过可选 Python 依赖安装（更快；仅下载 PDF 脚本需要）",
            variable=self.skip_python_deps_var,
        ).pack(anchor="w", pady=(6, 0))

        ttk.Label(
            self.body,
            text="下一步只为上一页勾选的 AI 助手安装 Skills；测试阶段也只验证这些助手。",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(18, 0))

    def on_show(self) -> None:
        for child in self.dirs_frame.winfo_children():
            child.destroy()
        detection = self.app.detection
        selected = tuple(getattr(self.app, "selected_assistants", ()) or ())

        ttk.Label(self.dirs_frame, text="已勾选的 AI 助手：", style="Body.TLabel").pack(
            anchor="w"
        )
        if selected:
            labels = "、".join(ASSISTANT_LABELS.get(k, k) for k in selected)
            ttk.Label(self.dirs_frame, text=f"• {labels}", style="Muted.TLabel").pack(
                anchor="w"
            )
        else:
            ttk.Label(self.dirs_frame, text="• （尚未勾选）", style="Muted.TLabel").pack(
                anchor="w"
            )

        ttk.Label(
            self.dirs_frame, text="目标 Skills 目录：", style="Body.TLabel"
        ).pack(anchor="w", pady=(10, 0))
        if detection is None:
            ttk.Label(self.dirs_frame, text="（尚未检测）", style="Muted.TLabel").pack(
                anchor="w"
            )
            return
        targets = detection.target_skill_dirs(selected)
        if not targets:
            ttk.Label(
                self.dirs_frame,
                text="（无匹配目录，请返回重新勾选）",
                style="Muted.TLabel",
            ).pack(anchor="w")
            return
        for path in targets:
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
        return "开始安装"
