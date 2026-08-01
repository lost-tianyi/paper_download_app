from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.config import DOWNLOAD_URLS
from core.detect import ASSISTANT_KEYS, ASSISTANT_LABELS, detect_environment
from gui.pages.base import BasePage
from gui.widgets import COLORS, open_url, status_label


class DetectPage(BasePage):
    title = "环境检测"
    subtitle = "勾选你要使用的 AI 编程助手；后续安装与测试只针对勾选项"

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

        self._add_hit(result.codex, "编码助手")
        self._add_hit(result.claude, "编码助手")
        self._add_hit(result.cursor, "编码助手")
        self._add_hit(result.zotero, "文献管理")

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
                text="请安装 Zotero：",
                style="Muted.TLabel",
            ).pack(anchor="w", pady=(10, 0))
            self._link_button("下载 Zotero", DOWNLOAD_URLS["zotero"])

        self.app.update_nav_state()

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
        self._sync_selection_to_app()
        if not self._ready:
            return False
        return True
