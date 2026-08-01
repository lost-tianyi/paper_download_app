from __future__ import annotations

from tkinter import ttk

from core.config import APP_NAME, APP_VERSION
from gui.pages.base import BasePage


class WelcomePage(BasePage):
    title = f"欢迎使用 {APP_NAME}"
    subtitle = f"版本 {APP_VERSION} · 图形化安装向导"

    def build(self) -> None:
        lines = [
            "本向导将帮助你完成 AI 文献综述工作流的环境检测与 Skills 安装。",
            "",
            "安装包已内置全部 Skills 素材，安装过程离线复制，无需再联网下载。",
            "",
            "将安装的 Skills：",
            "  1. academic-search — 学术检索、DOI 核验、结构化导出",
            "  2. sciencedirect-live-session-fetcher — 合法会话下串行下载 PDF",
            "",
            "安装目标目录（按已检测应用）：",
            "  • Codex  → ~/.codex/skills/",
            "  • Claude → ~/.claude/skills/",
            "  • Cursor → ~/.cursor/skills/",
            "",
            "开始前请确保已安装：",
            "  • Codex / Claude Code / Cursor 至少之一",
            "  • Zotero",
            "",
            "点击「下一步」开始环境检测。",
        ]
        for line in lines:
            ttk.Label(self.body, text=line, style="Body.TLabel").pack(anchor="w", pady=1)

        ttk.Label(
            self.body,
            text="素材已打包在安装程序内（bundled/skills）",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(18, 0))

    def back_enabled(self) -> bool:
        return False
