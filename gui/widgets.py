"""Shared installer wizard widgets."""

from __future__ import annotations

import sys
import tkinter as tk
from tkinter import ttk
from typing import Iterable, Optional


# Professional research-tool palette
COLORS = {
    "bg": "#EEF1F4",
    "panel": "#FFFFFF",
    "sidebar": "#15202B",
    "sidebar_text": "#C5CDD6",
    "sidebar_active": "#FFFFFF",
    "sidebar_done": "#5EEAD4",
    "accent": "#0F766E",
    "accent_hover": "#0D9488",
    "accent_soft": "#CCFBF1",
    "text": "#0F172A",
    "muted": "#64748B",
    "ok": "#047857",
    "fail": "#B91C1C",
    "warn": "#B45309",
    "border": "#D8DEE6",
    "log_bg": "#0B1220",
    "log_fg": "#E2E8F0",
}


def ui_font(size: int = 12, weight: str = "normal") -> tuple:
    if sys.platform == "darwin":
        family = "SF Pro Text"
    elif sys.platform == "win32":
        family = "Segoe UI"
    else:
        family = "Helvetica"
    if weight == "bold":
        return (family, size, "bold")
    return (family, size)


def ui_mono(size: int = 11) -> tuple:
    if sys.platform == "darwin":
        return ("Menlo", size)
    if sys.platform == "win32":
        return ("Consolas", size)
    return ("monospace", size)


class StepSidebar(ttk.Frame):
    def __init__(self, master: tk.Misc, steps: Iterable[str], **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.steps = list(steps)
        self._labels: list[tk.Label] = []
        self._dots: list[tk.Label] = []
        self.configure(style="Sidebar.TFrame")

        brand = tk.Frame(self, bg=COLORS["sidebar"])
        brand.pack(fill="x", padx=18, pady=(20, 10))

        self.logo_label = tk.Label(brand, bg=COLORS["sidebar"])
        self.logo_label.pack(side="left", padx=(0, 10))
        self._load_logo()

        titles = tk.Frame(brand, bg=COLORS["sidebar"])
        titles.pack(side="left", fill="x", expand=True)
        tk.Label(
            titles,
            text="Literature Review",
            bg=COLORS["sidebar"],
            fg=COLORS["sidebar_active"],
            font=ui_font(13, "bold"),
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            titles,
            text="Installer",
            bg=COLORS["sidebar"],
            fg=COLORS["sidebar_done"],
            font=ui_font(11),
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            self,
            text="安装步骤",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=ui_font(10),
            anchor="w",
        ).pack(fill="x", padx=20, pady=(8, 4))

        for idx, name in enumerate(self.steps, start=1):
            row = tk.Frame(self, bg=COLORS["sidebar"])
            row.pack(fill="x", padx=16, pady=3)
            dot = tk.Label(
                row,
                text=str(idx),
                width=2,
                bg=COLORS["sidebar"],
                fg=COLORS["sidebar_text"],
                font=ui_font(10, "bold"),
            )
            dot.pack(side="left", padx=(0, 8))
            lbl = tk.Label(
                row,
                text=name,
                bg=COLORS["sidebar"],
                fg=COLORS["sidebar_text"],
                font=ui_font(12),
                anchor="w",
            )
            lbl.pack(side="left", fill="x")
            self._labels.append(lbl)
            self._dots.append(dot)

        footer = tk.Label(
            self,
            text="AI 文献综述工作流\n离线 Skills 安装向导",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=ui_font(10),
            justify="left",
            anchor="sw",
            padx=20,
            pady=18,
        )
        footer.pack(side="bottom", fill="x")

    def _load_logo(self) -> None:
        try:
            from pathlib import Path
            from core.config import project_root

            candidates = [
                project_root() / "assets" / "app-icon-64.png",
                project_root() / "assets" / "app-icon.png",
                Path(__file__).resolve().parents[1] / "assets" / "app-icon-64.png",
            ]
            path = next((p for p in candidates if p.is_file()), None)
            if path is None:
                self.logo_label.configure(text="LR", fg=COLORS["sidebar_done"], font=ui_font(14, "bold"))
                return
            img = tk.PhotoImage(file=str(path))
            if img.width() > 48:
                factor = max(1, img.width() // 40)
                img = img.subsample(factor, factor)
            self._logo_img = img
            self.logo_label.configure(image=img)
        except Exception:
            self.logo_label.configure(text="LR", fg=COLORS["sidebar_done"], font=ui_font(14, "bold"))

    def set_active(self, index: int) -> None:
        for i, (lbl, dot) in enumerate(zip(self._labels, self._dots)):
            if i == index:
                lbl.configure(fg=COLORS["sidebar_active"], font=ui_font(12, "bold"))
                dot.configure(fg=COLORS["sidebar_done"], text="●")
            elif i < index:
                lbl.configure(fg=COLORS["sidebar_done"], font=ui_font(12))
                dot.configure(fg=COLORS["sidebar_done"], text="✓")
            else:
                lbl.configure(fg=COLORS["sidebar_text"], font=ui_font(12))
                dot.configure(fg=COLORS["sidebar_text"], text=str(i + 1))


class LogView(tk.Text):
    def __init__(self, master: tk.Misc, **kwargs) -> None:
        kwargs.setdefault("height", 16)
        kwargs.setdefault("wrap", "word")
        kwargs.setdefault("bg", COLORS["log_bg"])
        kwargs.setdefault("fg", COLORS["log_fg"])
        kwargs.setdefault("insertbackground", COLORS["log_fg"])
        kwargs.setdefault("relief", "flat")
        kwargs.setdefault("bd", 0)
        kwargs.setdefault("padx", 10)
        kwargs.setdefault("pady", 10)
        kwargs.setdefault("font", ui_mono(11))
        super().__init__(master, **kwargs)
        self.configure(state="disabled", highlightthickness=1, highlightbackground=COLORS["border"])
        self.tag_configure("ok", foreground="#6EE7B7")
        self.tag_configure("fail", foreground="#FCA5A5")
        self.tag_configure("warn", foreground="#FCD34D")
        self.tag_configure("info", foreground="#93C5FD")
        self.tag_configure("step", foreground="#FDE68A")

    def append(self, message: str) -> None:
        tag = "info"
        if message.startswith("[OK]"):
            tag = "ok"
        elif message.startswith("[FAIL]"):
            tag = "fail"
        elif message.startswith("[WARN]"):
            tag = "warn"
        elif message.startswith("[步骤"):
            tag = "step"
        elif message.startswith("==>") or message.startswith("===="):
            tag = "info"
        self.configure(state="normal")
        self.insert("end", message + "\n", tag)
        self.see("end")
        self.configure(state="disabled")
        self.update_idletasks()

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
        font=ui_font(22, "bold"),
    )
    style.configure(
        "Body.TLabel",
        background=COLORS["panel"],
        foreground=COLORS["text"],
        font=ui_font(12),
    )
    style.configure(
        "Muted.TLabel",
        background=COLORS["panel"],
        foreground=COLORS["muted"],
        font=ui_font(11),
    )
    style.configure(
        "Accent.TButton",
        font=ui_font(12, "bold"),
        padding=(18, 9),
        background=COLORS["accent"],
        foreground="#FFFFFF",
        borderwidth=0,
    )
    style.map(
        "Accent.TButton",
        background=[
            ("pressed", "#115E59"),
            ("active", COLORS["accent_hover"]),
            ("disabled", "#94A3B8"),
            ("!disabled", COLORS["accent"]),
        ],
        foreground=[("disabled", "#F8FAFC"), ("!disabled", "#FFFFFF")],
    )
    style.configure(
        "Nav.TButton",
        font=ui_font(11),
        padding=(14, 8),
        background="#E2E8F0",
        foreground=COLORS["text"],
        borderwidth=0,
    )
    style.map(
        "Nav.TButton",
        background=[
            ("pressed", "#CBD5E1"),
            ("active", "#Dbe3ee"),
            ("disabled", "#F1F5F9"),
            ("!disabled", "#E2E8F0"),
        ],
    )
    style.configure(
        "Card.TFrame",
        background=COLORS["panel"],
        relief="flat",
    )
    style.configure(
        "TCheckbutton",
        background=COLORS["panel"],
        foreground=COLORS["text"],
        font=ui_font(12),
    )
    style.map("TCheckbutton", background=[("active", COLORS["panel"])])
    style.configure(
        "Horizontal.TProgressbar",
        troughcolor="#E2E8F0",
        background=COLORS["accent"],
        bordercolor="#E2E8F0",
        lightcolor=COLORS["accent"],
        darkcolor=COLORS["accent"],
        thickness=8,
    )


def open_url(url: str) -> None:
    import webbrowser

    webbrowser.open(url)


def copy_to_clipboard(root: tk.Tk, text: str) -> None:
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update_idletasks()


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
        font=ui_font(12),
        anchor="w",
        justify="left",
    )
