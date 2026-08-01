from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk

from core.install_skills import install_all_skills
from gui.pages.base import BasePage
from gui.widgets import LogView


class ProgressPage(BasePage):
    title = "安装进度"
    subtitle = "正在从安装包内置素材复制 Skills（离线）"

    def build(self) -> None:
        self.log = LogView(self.body, height=18)
        self.log.pack(fill="both", expand=True)
        self.progress = ttk.Progressbar(self.body, mode="indeterminate")
        self.progress.pack(fill="x", pady=(12, 0))
        self._done = False
        self._ok = False
        self._started = False

    def on_show(self) -> None:
        if self._started:
            self.app.update_nav_state()
            return
        self._started = True
        self._done = False
        self._ok = False
        self.log.clear()
        self.progress.start(12)
        self.app.set_busy(True)
        thread = threading.Thread(target=self._run_install, daemon=True)
        thread.start()

    def _run_install(self) -> None:
        def log(msg: str) -> None:
            self.app.root.after(0, lambda m=msg: self.log.append(m))

        result = install_all_skills(
            detection=self.app.detection,
            options=self.app.options,
            log=log,
        )
        self.app.root.after(0, lambda: self._finish(result.ok))

    def _finish(self, ok: bool) -> None:
        self.progress.stop()
        self._done = True
        self._ok = ok
        self.app.install_ok = ok
        self.app.set_busy(False)
        if ok:
            self.log.append("[OK] 安装阶段完成，可进入测试")
        else:
            self.log.append("[FAIL] 安装失败，请返回检查网络/Git 后重试")
        self.app.update_nav_state()

    def can_continue(self) -> bool:
        return self._done and self._ok

    def back_enabled(self) -> bool:
        return self._done and not self.app.busy

    def next_label(self) -> str:
        return "运行测试"
