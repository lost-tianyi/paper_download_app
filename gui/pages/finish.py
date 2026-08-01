from __future__ import annotations

from tkinter import ttk

from core.config import project_root
from gui.pages.base import BasePage
from gui.widgets import status_label


class FinishPage(BasePage):
    title = "安装完成"
    subtitle = "环境已就绪，可以开始文献综述工作流"

    def build(self) -> None:
        self.status_host = ttk.Frame(self.body, style="Panel.TFrame")
        self.status_host.pack(fill="x")

        steps = [
            "打开 Codex / Claude Code / Cursor。",
            "使用 academic-search 检索并导出 Excel。",
            "人工审阅，标记 Approved = Yes/No。",
            "机构权限场景下先在浏览器登录，再调用下载技能处理 Approved 记录。",
            "整理进 Zotero，并做最终对账。",
        ]
        ttk.Label(self.body, text="建议下一步：", style="Body.TLabel").pack(
            anchor="w", pady=(16, 6)
        )
        for i, line in enumerate(steps, 1):
            ttk.Label(
                self.body,
                text=f"{i}. {line}",
                style="Muted.TLabel",
            ).pack(anchor="w", pady=1)

        template = project_root() / "templates" / "search-prompt.md"
        ttk.Label(
            self.body,
            text=f"提示词模板：{template}",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(16, 0))

        ttk.Label(
            self.body,
            text="注意：不要向助手提供账号密码；仅使用你已授权的合法访问。",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(8, 0))

    def on_show(self) -> None:
        for child in self.status_host.winfo_children():
            child.destroy()
        ok = bool(self.app.install_ok and self.app.tests_ok)
        if ok:
            status_label(self.status_host, "安装完成：检测通过 · Skills 已就位 · 测试通过", True).pack(
                anchor="w"
            )
            self.title = "安装完成"
        else:
            status_label(self.status_host, "安装未完成：请返回查看日志并重试", False).pack(
                anchor="w"
            )

    def next_label(self) -> str:
        return "关闭"

    def back_enabled(self) -> bool:
        return True

    def on_next(self) -> bool:
        self.app.root.destroy()
        return False
