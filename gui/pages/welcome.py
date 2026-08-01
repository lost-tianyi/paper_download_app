from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.config import APP_NAME, APP_VERSION
from gui.pages.base import BasePage
from gui.widgets import COLORS, ui_font


class WelcomePage(BasePage):
    title = f"欢迎使用 {APP_NAME}"
    subtitle = f"版本 {APP_VERSION} · 图形化离线安装向导"

    def build(self) -> None:
        hero = tk.Frame(
            self.body,
            bg=COLORS["accent_soft"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        hero.pack(fill="x", pady=(0, 16))
        tk.Label(
            hero,
            text="AI 文献综述工作流 · 一键就绪",
            bg=COLORS["accent_soft"],
            fg=COLORS["text"],
            font=ui_font(14, "bold"),
            anchor="w",
        ).pack(fill="x", padx=16, pady=(14, 4))
        tk.Label(
            hero,
            text="安装包已内置全部 Skills 素材，安装过程本地复制，无需再联网拉取仓库。",
            bg=COLORS["accent_soft"],
            fg=COLORS["muted"],
            font=ui_font(11),
            anchor="w",
            justify="left",
            wraplength=620,
        ).pack(fill="x", padx=16, pady=(0, 14))

        lines = [
            "将安装的 Skills：",
            "  1. academic-search — 学术检索、DOI 核验、结构化导出",
            "  2. sciencedirect-live-session-fetcher — 合法会话下串行下载 PDF",
            "",
            "安装目标目录（按你勾选的助手）：",
            "  • Codex  → ~/.codex/skills/",
            "  • Claude → ~/.claude/skills/",
            "  • Cursor → ~/.cursor/skills/",
            "",
            "开始前请确保已安装：",
            "  • 至少一个你要用的 AI 编程助手（Codex / Claude Code / Cursor）",
            "  • Zotero",
            "",
            "下一步可勾选要使用的助手；安装与测试只针对勾选项。",
        ]
        for line in lines:
            ttk.Label(self.body, text=line, style="Body.TLabel").pack(anchor="w", pady=1)

        ttk.Label(
            self.body,
            text="素材目录：bundled/skills（已打入安装程序）",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(18, 0))

    def back_enabled(self) -> bool:
        return False
