from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from core.config import DOWNLOAD_URLS
from core.detect import (
    ASSISTANT_KEYS,
    ASSISTANT_LABELS,
    detect_environment,
    resolve_zotero_path,
)
from gui.pages.base import BasePage
from gui.widgets import COLORS, open_url, status_label


class DetectPage(BasePage):
    title_key = "detect_title"
    subtitle_key = "detect_subtitle"

    def build(self) -> None:
        self.status_frame = ttk.Frame(self.body, style="Panel.TFrame")
        self.status_frame.pack(fill="both", expand=True)

        ttk.Label(
            self.body,
            text="选择要安装 Skills 的 AI 编程助手（可多选）：",
            style="Body.TLabel",
        ).pack(anchor="w", pady=(12, 4))

        self.choice_frame = ttk.Frame(self.body, style="Panel.TFrame")
        self.choice_frame.pack(fill="x")

        self.assistant_vars: dict[str, tk.BooleanVar] = {
            key: tk.BooleanVar(value=False) for key in ASSISTANT_KEYS
        }
        self.assistant_checks: dict[str, ttk.Checkbutton] = {}
        for key in ASSISTANT_KEYS:
            var = self.assistant_vars[key]
            chk = ttk.Checkbutton(
                self.choice_frame,
                text=ASSISTANT_LABELS[key],
                variable=var,
                command=self._on_choice_changed,
            )
            chk.pack(anchor="w", pady=2)
            self.assistant_checks[key] = chk

        self.hint = ttk.Label(self.body, style="Muted.TLabel")
        self.hint.pack(anchor="w", pady=(8, 0))

        btn_row = ttk.Frame(self.body, style="Panel.TFrame")
        btn_row.pack(fill="x", pady=(12, 0))
        ttk.Button(btn_row, text="重新检测", command=self.refresh, style="Nav.TButton").pack(
            side="left"
        )
        ttk.Button(
            btn_row,
            text="全选已检测",
            command=self._select_all_found,
            style="Nav.TButton",
        ).pack(side="left", padx=(8, 0))
        ttk.Button(
            btn_row,
            text="浏览选择 Zotero…",
            command=self._browse_zotero,
            style="Accent.TButton",
        ).pack(side="left", padx=(8, 0))

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

        manual = str(getattr(self.app, "manual_zotero_path", "") or "")
        result = detect_environment(manual_zotero_path=manual)
        self.app.detection = result

        self._add_hit(result.codex, "编码助手")
        self._add_hit(result.claude, "编码助手")
        self._add_hit(result.cursor, "编码助手")
        self._add_zotero_hit(result.zotero, manual=bool(manual and result.zotero.found))

        previous = set(getattr(self.app, "selected_assistants", ()) or ())
        for key in ASSISTANT_KEYS:
            found = result.hit(key).found
            self.assistant_checks[key].configure(state=("normal" if found else "disabled"))
            if not found:
                self.assistant_vars[key].set(False)
            elif previous:
                self.assistant_vars[key].set(key in previous)
            else:
                # First visit: default-select every detected assistant.
                self.assistant_vars[key].set(True)

        # If previous selection became empty after redetect, fall back to all found.
        if result.found_assistant_keys() and not any(
            self.assistant_vars[k].get() for k in result.found_assistant_keys()
        ):
            for key in result.found_assistant_keys():
                self.assistant_vars[key].set(True)

        self._sync_selection_to_app()
        self._update_ready_ui()

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
                text="未找到 Zotero：可下载安装，或点击上方「浏览选择 Zotero…」指定本机路径。",
                style="Muted.TLabel",
            ).pack(anchor="w", pady=(10, 0))
            row = ttk.Frame(self.link_frame, style="Panel.TFrame")
            row.pack(fill="x", pady=(4, 0))
            self._link_button("下载 Zotero", DOWNLOAD_URLS["zotero"], parent=row)
            ttk.Button(
                row,
                text="浏览选择 Zotero…",
                style="Accent.TButton",
                command=self._browse_zotero,
            ).pack(side="left", padx=(0, 8), pady=4)

        self.app.update_nav_state()

    def _browse_zotero(self) -> None:
        if sys.platform == "darwin":
            path = filedialog.askdirectory(
                parent=self.app.root,
                title="选择 Zotero.app（通常在「应用程序」文件夹）",
                initialdir="/Applications",
                mustexist=True,
            )
        elif sys.platform == "win32":
            import os

            initial = os.environ.get("ProgramFiles", r"C:\Program Files")
            path = filedialog.askopenfilename(
                parent=self.app.root,
                title="选择 zotero.exe",
                initialdir=initial,
                filetypes=[
                    ("Zotero", "zotero.exe"),
                    ("可执行文件", "*.exe"),
                    ("所有文件", "*.*"),
                ],
            )
        else:
            path = filedialog.askopenfilename(
                parent=self.app.root,
                title="选择 Zotero 可执行文件",
                filetypes=[("所有文件", "*.*")],
            )

        if not path:
            return

        hit = resolve_zotero_path(path)
        if not hit.found:
            # On macOS, user might select Applications folder by mistake.
            guess = Path(path)
            if sys.platform == "darwin" and guess.is_dir():
                candidate = guess / "Zotero.app"
                if candidate.exists():
                    hit = resolve_zotero_path(candidate)
            if sys.platform == "win32" and guess.is_dir():
                candidate = guess / "zotero.exe"
                if candidate.exists():
                    hit = resolve_zotero_path(candidate)

        if not hit.found:
            tip = (
                "请选择 Zotero.app（例如 /Applications/Zotero.app）"
                if sys.platform == "darwin"
                else "请选择 zotero.exe（例如 C:\\Program Files\\Zotero\\zotero.exe）"
            )
            messagebox.showerror(
                "无法识别为 Zotero",
                f"所选路径无法确认为 Zotero 安装：\n{path}\n\n{tip}",
                parent=self.app.root,
            )
            return

        self.app.manual_zotero_path = hit.app_path
        self.refresh()
        messagebox.showinfo(
            "已指定 Zotero",
            f"已使用手动路径：\n{hit.app_path}",
            parent=self.app.root,
        )

    def _clear_manual_zotero(self) -> None:
        self.app.manual_zotero_path = ""
        self.refresh()

    def _select_all_found(self) -> None:
        detection = self.app.detection
        if detection is None:
            return
        for key in ASSISTANT_KEYS:
            self.assistant_vars[key].set(detection.hit(key).found)
        self._on_choice_changed()

    def _on_choice_changed(self) -> None:
        self._sync_selection_to_app()
        self._update_ready_ui()
        self.app.update_nav_state()

    def _current_selection(self) -> tuple[str, ...]:
        return tuple(key for key in ASSISTANT_KEYS if self.assistant_vars[key].get())

    def _sync_selection_to_app(self) -> None:
        self.app.selected_assistants = self._current_selection()

    def _update_ready_ui(self) -> None:
        detection = self.app.detection
        selected = self._current_selection()
        if detection is None:
            self._ready = False
            self.hint.configure(text="尚未完成检测")
            return

        self._ready = detection.ok_for_selection(selected)
        if self._ready:
            labels = "、".join(ASSISTANT_LABELS[k] for k in selected)
            self.hint.configure(
                text=f"已选择：{labels}。下一步将只为这些助手安装并测试 Skills。",
                foreground=COLORS["ok"],
            )
        else:
            msgs = detection.missing_messages(selected)
            self.hint.configure(
                text="；".join(msgs) if msgs else "请勾选至少一个已检测到的助手",
                foreground=COLORS["fail"],
            )

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

    def _add_zotero_hit(self, hit, manual: bool = False) -> None:
        box = ttk.Frame(self.status_frame, style="Panel.TFrame")
        box.pack(fill="x", pady=4)
        label = "Zotero（文献管理）"
        if hit.found and manual:
            label += " · 手动指定"
        status_label(box, label, ok=hit.found).pack(anchor="w")
        if hit.app_path:
            ttk.Label(
                box,
                text=f"    App: {hit.app_path}",
                style="Muted.TLabel",
            ).pack(anchor="w")
        elif not hit.found:
            ttk.Label(
                box,
                text="    未找到。若已安装在自定义位置，请点击「浏览选择 Zotero…」",
                style="Muted.TLabel",
            ).pack(anchor="w")

        action = ttk.Frame(box, style="Panel.TFrame")
        action.pack(anchor="w", pady=(2, 0))
        ttk.Button(
            action,
            text="浏览选择…",
            style="Nav.TButton",
            command=self._browse_zotero,
        ).pack(side="left")
        if manual and hit.found:
            ttk.Button(
                action,
                text="清除手动路径",
                style="Nav.TButton",
                command=self._clear_manual_zotero,
            ).pack(side="left", padx=(8, 0))

    def _link_button(
        self, text: str, url: str, parent: ttk.Frame | None = None
    ) -> None:
        host = parent or self.link_frame
        ttk.Button(
            host,
            text=text,
            style="Nav.TButton",
            command=lambda u=url: open_url(u),
        ).pack(side="left", padx=(0, 8), pady=4)

    def can_continue(self) -> bool:
        return self._ready

    def on_next(self) -> bool:
        self._sync_selection_to_app()
        if not self._ready:
            return False
        return True
