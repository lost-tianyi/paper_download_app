"""Main installer wizard application."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional

from core.config import APP_NAME, WIZARD_STEPS
from core.detect import DetectionResult
from core.install_skills import InstallOptions
from gui.pages import (
    DetectPage,
    FinishPage,
    OptionsPage,
    ProgressPage,
    TestsPage,
    WelcomePage,
)
from gui.pages.base import BasePage
from gui.widgets import COLORS, StepSidebar, configure_styles


class InstallerApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry("960x640")
        self.root.minsize(900, 600)
        self.root.configure(bg=COLORS["bg"])
        self._set_window_icon()

        configure_styles(self.root)

        self.detection: Optional[DetectionResult] = None
        self.options: InstallOptions = InstallOptions()
        self.selected_assistants: tuple[str, ...] = ()
        self.install_ok = False
        self.tests_ok = False
        self.busy = False
        self.index = 0

        shell = ttk.Frame(self.root, style="Root.TFrame")
        shell.pack(fill="both", expand=True)

        self.sidebar = StepSidebar(shell, WIZARD_STEPS, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self.sidebar.configure(width=230)

        right = ttk.Frame(shell, style="Root.TFrame")
        right.pack(side="left", fill="both", expand=True, padx=16, pady=16)

        self.page_host = ttk.Frame(right, style="Panel.TFrame")
        self.page_host.pack(fill="both", expand=True)

        nav = ttk.Frame(right, style="Root.TFrame")
        nav.pack(fill="x", pady=(12, 0))

        self.back_btn = ttk.Button(
            nav, text="上一步", style="Nav.TButton", command=self.go_back
        )
        self.back_btn.pack(side="left")

        self.next_btn = ttk.Button(
            nav, text="下一步", style="Accent.TButton", command=self.go_next
        )
        self.next_btn.pack(side="right")

        self.pages: list[BasePage] = [
            WelcomePage(self.page_host, self),
            DetectPage(self.page_host, self),
            OptionsPage(self.page_host, self),
            ProgressPage(self.page_host, self),
            TestsPage(self.page_host, self),
            FinishPage(self.page_host, self),
        ]
        for page in self.pages:
            page.place(in_=self.page_host, x=0, y=0, relwidth=1, relheight=1)

        self.show_page(0)

    def _set_window_icon(self) -> None:
        try:
            from pathlib import Path
            from core.config import project_root

            candidates = [
                project_root() / "assets" / "app-icon-256.png",
                project_root() / "assets" / "app-icon.png",
                Path(__file__).resolve().parents[1] / "assets" / "app-icon-256.png",
            ]
            path = next((p for p in candidates if p.is_file()), None)
            if path is None:
                return
            self._icon_img = tk.PhotoImage(file=str(path))
            self.root.iconphoto(True, self._icon_img)
        except Exception:
            pass

    def set_busy(self, busy: bool) -> None:
        self.busy = busy
        self.update_nav_state()

    def show_page(self, index: int) -> None:
        self.index = index
        for i, page in enumerate(self.pages):
            if i == index:
                page.lift()
                page.on_show()
            # keep others packed via place
        self.sidebar.set_active(index)
        page = self.pages[index]
        self.next_btn.configure(text=page.next_label())
        self.update_nav_state()

    def update_nav_state(self) -> None:
        page = self.pages[self.index]
        back_state = "normal" if page.back_enabled() and not self.busy else "disabled"
        next_state = (
            "normal" if page.can_continue() and not self.busy else "disabled"
        )
        # Finish page always allows close when shown
        if isinstance(page, FinishPage):
            next_state = "normal"
        # Welcome always allows next
        if isinstance(page, WelcomePage):
            next_state = "normal" if not self.busy else "disabled"
        self.back_btn.configure(state=back_state)
        self.next_btn.configure(state=next_state)
        self.next_btn.configure(text=page.next_label())

    def go_back(self) -> None:
        if self.busy or self.index <= 0:
            return
        # Allow retrying install/tests by recreating those pages when going back
        if self.index in (3, 4):
            self._reset_page(self.index)
        self.show_page(self.index - 1)

    def go_next(self) -> None:
        if self.busy:
            return
        page = self.pages[self.index]
        if not page.on_next():
            return
        if self.index >= len(self.pages) - 1:
            return
        # Reset progress/tests pages when entering them fresh after options
        nxt = self.index + 1
        if nxt in (3, 4):
            self._reset_page(nxt)
        self.show_page(nxt)

    def _reset_page(self, index: int) -> None:
        cls = type(self.pages[index])
        old = self.pages[index]
        old.destroy()
        new_page = cls(self.page_host, self)
        new_page.place(in_=self.page_host, x=0, y=0, relwidth=1, relheight=1)
        self.pages[index] = new_page

    def run(self) -> None:
        self.root.mainloop()


def run_wizard() -> None:
    app = InstallerApp()
    app.run()


if __name__ == "__main__":
    run_wizard()
