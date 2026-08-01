from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.config import project_root
from core.prompts import load_example_prompts
from gui.pages.base import BasePage
from gui.widgets import COLORS, copy_to_clipboard, status_label, ui_font


class FinishPage(BasePage):
    title = "安装完成"
    subtitle = "环境已就绪，可以开始文献综述工作流"

    def build(self) -> None:
        self.status_host = ttk.Frame(self.body, style="Panel.TFrame")
        self.status_host.pack(fill="x")

        steps = [
            "打开你勾选的 AI 编程助手（Codex / Claude Code / Cursor）。",
            "粘贴检索示例提示词，用 academic-search 检索并导出 Excel。",
            "人工审阅，标记 Approved = Yes/No。",
            "机构权限场景下先在浏览器登录，再粘贴下载示例提示词处理 Approved 记录。",
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

        prompt_box = tk.Frame(
            self.body,
            bg=COLORS["accent_soft"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        prompt_box.pack(fill="x", pady=(18, 0))

        tk.Label(
            prompt_box,
            text="示例提示词",
            bg=COLORS["accent_soft"],
            fg=COLORS["text"],
            font=ui_font(12, "bold"),
            anchor="w",
        ).pack(fill="x", padx=14, pady=(12, 4))
        tk.Label(
            prompt_box,
            text="点击下方按钮即可复制到剪贴板，粘贴给已安装 Skills 的助手使用。",
            bg=COLORS["accent_soft"],
            fg=COLORS["muted"],
            font=ui_font(11),
            anchor="w",
            justify="left",
        ).pack(fill="x", padx=14, pady=(0, 10))

        btn_row = tk.Frame(prompt_box, bg=COLORS["accent_soft"])
        btn_row.pack(fill="x", padx=14, pady=(0, 12))

        self.copy_search_btn = ttk.Button(
            btn_row,
            text="复制检索示例提示词",
            style="Accent.TButton",
            command=self._copy_search_prompt,
        )
        self.copy_search_btn.pack(side="left")

        self.copy_download_btn = ttk.Button(
            btn_row,
            text="复制下载示例提示词",
            style="Nav.TButton",
            command=self._copy_download_prompt,
        )
        self.copy_download_btn.pack(side="left", padx=(10, 0))

        self.copy_feedback = tk.Label(
            prompt_box,
            text="",
            bg=COLORS["accent_soft"],
            fg=COLORS["ok"],
            font=ui_font(11),
            anchor="w",
        )
        self.copy_feedback.pack(fill="x", padx=14, pady=(0, 12))

        template = project_root() / "templates" / "search-prompt.md"
        ttk.Label(
            self.body,
            text=f"完整模板文件：{template}",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(14, 0))

        ttk.Label(
            self.body,
            text="注意：不要向助手提供账号密码；仅使用你已授权的合法访问。",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(8, 0))

        self._search_prompt, self._download_prompt = load_example_prompts()

    def _flash(self, message: str) -> None:
        self.copy_feedback.configure(text=message, fg=COLORS["ok"])
        self.app.root.after(
            2500, lambda: self.copy_feedback.configure(text="")
        )

    def _copy_search_prompt(self) -> None:
        copy_to_clipboard(self.app.root, self._search_prompt)
        self._flash("已复制检索示例提示词到剪贴板")

    def _copy_download_prompt(self) -> None:
        copy_to_clipboard(self.app.root, self._download_prompt)
        self._flash("已复制下载示例提示词到剪贴板")

    def on_show(self) -> None:
        for child in self.status_host.winfo_children():
            child.destroy()
        self._search_prompt, self._download_prompt = load_example_prompts()
        installed = bool(self.app.install_ok)
        tested = bool(self.app.tests_ok)
        if installed and tested:
            status_label(
                self.status_host,
                "安装完成：检测通过 · Skills 已就位 · 测试通过",
                True,
            ).pack(anchor="w")
        elif installed:
            status_label(
                self.status_host,
                "Skills 已安装；部分测试未通过，仍可复制示例提示词试用",
                None,
            ).pack(anchor="w")
        else:
            status_label(
                self.status_host,
                "安装未完成：请返回查看日志并重试",
                False,
            ).pack(anchor="w")
            self.copy_search_btn.configure(state="disabled")
            self.copy_download_btn.configure(state="disabled")
            return
        # Allow copying prompts whenever Skills were installed successfully.
        self.copy_search_btn.configure(state="normal")
        self.copy_download_btn.configure(state="normal")

    def next_label(self) -> str:
        return "关闭"

    def back_enabled(self) -> bool:
        return True

    def on_next(self) -> bool:
        self.app.root.destroy()
        return False
