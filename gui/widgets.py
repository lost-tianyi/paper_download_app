"""Shared installer wizard widgets."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Iterable, Optional


# Calm installer palette (avoid purple/glow AI defaults)
COLORS = {
    "bg": "#F3F4F6",
    "panel": "#FFFFFF",
    "sidebar": "#1F2937",
    "sidebar_text": "#E5E7EB",
    "sidebar_active": "#F9FAFB",
    "accent": "#0F766E",
    "accent_hover": "#0D9488",
    "text": "#111827",
    "muted": "#6B7280",
    "ok": "#047857",
    "fail": "#B91C1C",
    "warn": "#B45309",
    "border": "#D1D5DB",
    "log_bg": "#111827",
    "log_fg": "#E5E7EB",
}


class StepSidebar(ttk.Frame):
    def __init__(self, master: tk.Misc, steps: Iterable[str], **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.steps = list(steps)
        self._labels: list[tk.Label] = []
        self.configure(style="Sidebar.TFrame")

        title = tk.Label(
            self,
            text="安装向导",
            bg=COLORS["sidebar"],
            fg=COLORS["sidebar_active"],
            font=("Helvetica", 16, "bold"),
            anchor="w",
            padx=20,
            pady=18,
        )
        title.pack(fill="x")

        for idx, name in enumerate(self.steps, start=1):
            lbl = tk.Label(
                self,
                text=f"{idx}. {name}",
                bg=COLORS["sidebar"],
                fg=COLORS["sidebar_text"],
                font=("Helvetica", 12),
                anchor="w",
                padx=24,
                pady=8,
            )
            lbl.pack(fill="x")
            self._labels.append(lbl)

        footer = tk.Label(
            self,
            text="Literature Review\nWorkflow",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=("Helvetica", 10),
            justify="left",
            anchor="sw",
            padx=20,
            pady=16,
        )
        footer.pack(side="bottom", fill="x")

    def set_active(self, index: int) -> None:
        for i, lbl in enumerate(self._labels):
            if i == index:
                lbl.configure(
                    fg=COLORS["sidebar_active"],
                    font=("Helvetica", 12, "bold"),
                )
            elif i < index:
                lbl.configure(fg="#99F6E4", font=("Helvetica", 12))
            else:
                lbl.configure(fg=COLORS["sidebar_text"], font=("Helvetica", 12))


class LogView(tk.Text):
    def __init__(self, master: tk.Misc, **kwargs) -> None:
        kwargs.setdefault("height", 16)
        kwargs.setdefault("wrap", "word")
        kwargs.setdefault("bg", COLORS["log_bg"])
        kwargs.setdefault("fg", COLORS["log_fg"])
        kwargs.setdefault("insertbackground", COLORS["log_fg"])
        kwargs.setdefault("relief", "flat")
        kwargs.setdefault("font", ("Menlo", 11) if tk.TkVersion else ("Consolas", 10))
        super().__init__(master, **kwargs)
        self.configure(state="disabled")
        self.tag_configure("ok", foreground="#6EE7B7")
        self.tag_configure("fail", foreground="#FCA5A5")
        self.tag_configure("warn", foreground="#FCD34D")
        self.tag_configure("info", foreground="#93C5FD")

    def append(self, message: str) -> None:
        tag = "info"
        if message.startswith("[OK]"):
            tag = "ok"
        elif message.startswith("[FAIL]"):
            tag = "fail"
        elif message.startswith("[WARN]"):
            tag = "warn"
        elif message.startswith("==>"):
            tag = "info"
        self.configure(state="normal")
        self.insert("end", message + "\n", tag)
        self.see("end")
        self.configure(state="disabled")

    def clear(self) -> None:
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")


def configure_styles(root: tk.Tk) -> None:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("Sidebar.TFrame", background=COLORS["sidebar"])
    style.configure("Panel.TFrame", background=COLORS["panel"])
    style.configure("Root.TFrame", background=COLORS["bg"])
    style.configure(
        "Title.TLabel",
        background=COLORS["panel"],
        foreground=COLORS["text"],
        font=("Helvetica", 20, "bold"),
    )
    style.configure(
        "Body.TLabel",
        background=COLORS["panel"],
        foreground=COLORS["text"],
        font=("Helvetica", 12),
    )
    style.configure(
        "Muted.TLabel",
        background=COLORS["panel"],
        foreground=COLORS["muted"],
        font=("Helvetica", 11),
    )
    style.configure(
        "Accent.TButton",
        font=("Helvetica", 12, "bold"),
        padding=(16, 8),
    )
    style.map(
        "Accent.TButton",
        background=[("active", COLORS["accent_hover"]), ("!disabled", COLORS["accent"])],
        foreground=[("!disabled", "#FFFFFF")],
    )
    style.configure("Nav.TButton", font=("Helvetica", 11), padding=(14, 7))


def open_url(url: str) -> None:
    import webbrowser

    webbrowser.open(url)


def status_label(master: tk.Misc, text: str, ok: Optional[bool] = None) -> tk.Label:
    if ok is True:
        color = COLORS["ok"]
        prefix = "✓ "
    elif ok is False:
        color = COLORS["fail"]
        prefix = "✗ "
    else:
        color = COLORS["muted"]
        prefix = "• "
    return tk.Label(
        master,
        text=prefix + text,
        bg=COLORS["panel"],
        fg=color,
        font=("Helvetica", 12),
        anchor="w",
        justify="left",
    )
