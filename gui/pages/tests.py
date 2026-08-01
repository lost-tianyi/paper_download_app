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
        self.status = ttk.Label(
            self.body,
            text="准备开始测试…",
            style="Body.TLabel",
        )
        self.status.pack(anchor="w", pady=(0, 8))
        self.log = LogView(self.body, height=16)
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
        self.status.configure(text="测试进行中，请查看下方日志…")
        self.log.append("============================================================")
        self.log.append("开始标准化测试（用于确认 Skills 可用）")
        self.log.append("============================================================")
        self.progress.start(12)
        self.app.set_busy(True)
        thread = threading.Thread(target=self._run_tests, daemon=True)
        thread.start()

    def _run_tests(self) -> None:
        def log(msg: str) -> None:
            self.app.root.after(0, lambda m=msg: self._append_log(m))

        options = self.app.options or InstallOptions()
        assistants = options.assistants or tuple(
            getattr(self.app, "selected_assistants", ()) or ()
        )
        result = run_standardized_tests(
            detection=self.app.detection,
            skip_network_test=options.skip_network_test,
            assistants=assistants,
            log=log,
        )
        self.app.root.after(0, lambda: self._finish(result.ok))

    def _append_log(self, msg: str) -> None:
        self.log.append(msg)
        if msg.startswith("测试 ") or msg.startswith("[步骤"):
            self.status.configure(text=f"当前：{msg}")

    def _finish(self, ok: bool) -> None:
        self.progress.stop()
        self._done = True
        self._ok = ok
        self.app.tests_ok = ok
        self.app.set_busy(False)
        if ok:
            self.status.configure(text="全部测试通过")
            self.log.append("[OK] 可以进入完成页")
        else:
            self.status.configure(text="部分测试失败，请查看日志")
            self.log.append("[FAIL] 请根据上方失败项排查后返回重试")
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
