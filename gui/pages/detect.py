from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.config import DOWNLOAD_URLS
from core.detect import DetectionResult, detect_environment
from gui.pages.base import BasePage
from gui.widgets import COLORS, open_url, status_label


class DetectPage(BasePage):
    title = "环境检测"
    subtitle = "需要至少一个编码助手，以及 Zotero"

    def build(self) -> None:
        self.status_frame = ttk.Frame(self.body, style="Panel.TFrame")
        self.status_frame.pack(fill="both", expand=True)

        btn_row = ttk.Frame(self.body, style="Panel.TFrame")
        btn_row.pack(fill="x", pady=(12, 0))
        ttk.Button(btn_row, text="重新检测", command=self.refresh, style="Nav.TButton").pack(
            side="left"
        )

        self.link_frame = ttk.Frame(self.body, style="Panel.TFrame")
        self.link_frame.pack(fill="x", pady=(16, 0))
        self._ready = False

    def on_show(self) -> None:
        self.refresh()

    def refresh(self) -> None:
        for child in self.status_frame.winfo_children():
            child.destroy()
        for child in self.link_frame.winfo_children():
            child.destroy()

        result = detect_environment()
        self.app.detection = result
        self._ready = result.ok

        self._add_hit(result.codex, "编码助手")
        self._add_hit(result.claude, "编码助手")
        self._add_hit(result.cursor, "编码助手")
        self._add_hit(result.zotero, "文献管理")

        summary = ttk.Label(self.status_frame, style="Body.TLabel")
        if result.ok:
            summary.configure(
                text=f"检测通过：编码助手 {result.assistant_count} 个 + Zotero",
                foreground=COLORS["ok"],
            )
        else:
            summary.configure(
                text="检测未通过：请安装缺失应用后点击「重新检测」",
                foreground=COLORS["fail"],
            )
        summary.pack(anchor="w", pady=(14, 0))

        if result.assistant_count == 0:
            ttk.Label(
                self.link_frame,
                text="请至少安装以下任一编码助手：",
                style="Muted.TLabel",
            ).pack(anchor="w")
            self._link_button("下载 Codex", DOWNLOAD_URLS["codex"])
            self._link_button("下载 Claude Code", DOWNLOAD_URLS["claude"])
            self._link_button("下载 Cursor", DOWNLOAD_URLS["cursor"])

        if not result.zotero.found:
            ttk.Label(
                self.link_frame,
                text="请安装 Zotero：",
                style="Muted.TLabel",
            ).pack(anchor="w", pady=(10, 0))
            self._link_button("下载 Zotero", DOWNLOAD_URLS["zotero"])

        self.app.update_nav_state()

    def _add_hit(self, hit, kind: str) -> None:
        box = ttk.Frame(self.status_frame, style="Panel.TFrame")
        box.pack(fill="x", pady=4)
        status_label(
            box,
            f"{hit.name}（{kind}）",
            ok=hit.found,
        ).pack(anchor="w")
        detail = []
        if hit.app_path:
            detail.append(f"App: {hit.app_path}")
        if hit.cli_path:
            detail.append(f"CLI: {hit.cli_path}")
        if hit.skills_dir and hit.found:
            detail.append(f"Skills: {hit.skills_dir}")
        if detail:
            ttk.Label(
                box,
                text="    " + "  |  ".join(detail),
                style="Muted.TLabel",
            ).pack(anchor="w")

    def _link_button(self, text: str, url: str) -> None:
        ttk.Button(
            self.link_frame,
            text=text,
            style="Nav.TButton",
            command=lambda u=url: open_url(u),
        ).pack(side="left", padx=(0, 8), pady=4)

    def can_continue(self) -> bool:
        return self._ready

    def on_next(self) -> bool:
        if not self._ready:
            return False
        return True
