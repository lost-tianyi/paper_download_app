from __future__ import annotations

import threading
from tkinter import ttk

from core.i18n import t
from core.install_skills import InstallOptions
from core.test_suite import run_standardized_tests
from gui.pages.base import BasePage
from gui.widgets import LogView


class TestsPage(BasePage):
    title_key = "tests_title"
    subtitle_key = "tests_subtitle"

    def build(self) -> None:
        self.status = ttk.Label(
            self.body,
            text=t("tests_ready"),
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
        self.status.configure(text=t("tests_running"))
        self.log.append(t("tests_start_banner"))
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

    def _finish(self, ok: bool) -> None:
        self.progress.stop()
        self._done = True
        self._ok = ok
        self.app.tests_ok = ok
        self.app.set_busy(False)
        if ok:
            self.status.configure(text=t("tests_done"))
            self.log.append("[OK] " + t("tests_log_ok"))
        else:
            self.status.configure(text=t("tests_fail"))
            self.log.append("[FAIL] " + t("tests_log_fail"))
        self.app.update_nav_state()

    def can_continue(self) -> bool:
        # Allow continue even if some checks failed — finish page handles soft state.
        return self._done

    def back_enabled(self) -> bool:
        return self._done and not self.app.busy

    def next_label(self) -> str:
        return t("tests_next_ok") if self._ok else t("next")

    def retry(self) -> None:
        self._started = False
        self.on_show()
