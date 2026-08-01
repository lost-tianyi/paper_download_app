from __future__ import annotations

import threading
from tkinter import ttk

from core.install_skills import InstallOptions
from core.test_suite import run_standardized_tests
from gui.pages.base import BasePage
from gui.widgets import LogView


class TestsPage(BasePage):
    title = "标准化测试"
    subtitle = "验证 Skills 布局、CLI 与脚本可用性"

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
        thread = threading.Thread(target=self._run_tests, daemon=True)
        thread.start()

    def _run_tests(self) -> None:
        def log(msg: str) -> None:
            self.app.root.after(0, lambda m=msg: self.log.append(m))

        options = self.app.options or InstallOptions()
        result = run_standardized_tests(
            detection=self.app.detection,
            skip_network_test=options.skip_network_test,
            log=log,
        )
        self.app.root.after(0, lambda: self._finish(result.ok))

    def _finish(self, ok: bool) -> None:
        self.progress.stop()
        self._done = True
        self._ok = ok
        self.app.tests_ok = ok
        self.app.set_busy(False)
        self.app.update_nav_state()

    def can_continue(self) -> bool:
        return self._done and self._ok

    def back_enabled(self) -> bool:
        return self._done and not self.app.busy

    def next_label(self) -> str:
        return "完成" if self._ok else "下一步"

    def retry(self) -> None:
        self._started = False
        self.on_show()
