from __future__ import annotations

import threading
from tkinter import ttk

from core.i18n import t
from core.install_skills import install_all_skills
from gui.pages.base import BasePage
from gui.widgets import LogView


class ProgressPage(BasePage):
    title_key = "progress_title"
    subtitle_key = "progress_subtitle"

    def build(self) -> None:
        self.status = ttk.Label(
            self.body,
            text=t("progress_ready"),
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
        self.refresh_header()
        if self._started:
            self.app.update_nav_state()
            return
        self._started = True
        self._done = False
        self._ok = False
        self.log.clear()
        self.status.configure(text=t("progress_running"))
        self.progress.start(12)
        self.app.set_busy(True)
        thread = threading.Thread(target=self._run_install, daemon=True)
        thread.start()

    def _run_install(self) -> None:
        def log(msg: str) -> None:
            self.app.root.after(0, lambda m=msg: self._append_log(m))

        result = install_all_skills(
            detection=self.app.detection,
            options=self.app.options,
            log=log,
        )
        self.app.root.after(0, lambda: self._finish(result.ok))

    def _append_log(self, msg: str) -> None:
        self.log.append(msg)
        if msg.startswith("[") and ("/" in msg[:12] or msg.startswith("[步骤")):
            self.status.configure(text=msg)

    def _finish(self, ok: bool) -> None:
        self.progress.stop()
        self._done = True
        self._ok = ok
        self.app.install_ok = ok
        self.app.set_busy(False)
        if ok:
            self.status.configure(text=t("progress_done"))
            self.log.append("[OK] " + t("progress_log_ok"))
        else:
            self.status.configure(text=t("progress_fail"))
            self.log.append("[FAIL] " + t("progress_log_fail"))
        self.app.update_nav_state()

    def can_continue(self) -> bool:
        return self._done and self._ok

    def back_enabled(self) -> bool:
        return self._done and not self.app.busy

    def next_label(self) -> str:
        return t("progress_next")
