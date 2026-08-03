"""User-facing Chinese / English copy for the installer wizard."""

from __future__ import annotations

from typing import Any

_LANG = "zh"

STRINGS: dict[str, dict[str, str]] = {
    "zh": {
        "app_title": "文献综述助手安装程序",
        "back": "上一步",
        "next": "下一步",
        "close": "完成并关闭",
        "start_install": "开始安装",
        "sidebar_steps": "安装步骤",
        "sidebar_footer": "文献综述助手\n一键完成环境准备",
        "step_language": "语言",
        "step_welcome": "欢迎",
        "step_detect": "检查环境",
        "step_options": "确认安装",
        "step_progress": "正在安装",
        "step_tests": "安装检查",
        "step_finish": "开始使用",
        "lang_title": "请选择语言",
        "lang_subtitle": "安装过程将使用您选择的语言显示说明",
        "lang_zh": "中文",
        "lang_en": "English",
        "lang_hint": "如需更改，可随时返回本页重新选择。",
        "welcome_title": "欢迎使用文献综述助手",
        "welcome_subtitle": "版本 {version}  ·  几分钟完成准备",
        "welcome_hero": "用 AI 助手完成文献检索、筛选与整理",
        "welcome_hero_body": "本程序会为您配置所需功能，安装过程无需联网下载额外组件。",
        "welcome_body": (
            "安装完成后，您将获得：\n"
            "  1. 文献检索 — 按主题检索、核验并导出文献表\n"
            "  2. 全文下载 — 在合法访问权限下下载 PDF 并整理\n"
            "  3. 工作流程指南 — 标准步骤与可用提示词说明\n"
            "\n"
            "使用前请先准备：\n"
            "  • 至少一款 AI 助手：Codex、Claude Code 或 Cursor\n"
            "  • 文献管理软件：Zotero\n"
            "\n"
            "接下来请选择您要使用的 AI 助手，程序只会为所选助手完成配置。"
        ),
        "welcome_footer": "提示：安装内容已包含在本程序中，可安心离线完成。",
        "detect_title": "检查您的电脑环境",
        "detect_subtitle": "请选择要使用的 AI 助手；后续步骤只针对您的选择进行配置",
        "detect_choose": "请选择要配置的 AI 助手（可多选）：",
        "detect_kind_assistant": "AI 助手",
        "detect_kind_library": "文献管理",
        "detect_refresh": "重新检查",
        "detect_select_all": "全选已找到的助手",
        "detect_browse_zotero": "手动指定 Zotero 位置…",
        "detect_browse_short": "手动指定…",
        "detect_clear_manual": "清除手动指定",
        "detect_need_assistant": "未检测到 AI 助手，请先安装以下任一软件：",
        "detect_need_zotero": "未找到 Zotero。可先下载安装，或点击「手动指定 Zotero 位置」选择本机安装位置。",
        "detect_download_zotero": "下载 Zotero",
        "detect_not_ready": "请完成环境检查后再继续",
        "detect_ready": "已选择：{labels}。下一步将仅为这些助手完成配置。",
        "detect_pick_one": "请至少勾选一个已检测到的助手",
        "detect_zotero_missing_hint": "未找到。若已安装在其他位置，请点击「手动指定…」",
        "detect_zotero_manual": "Zotero（文献管理）· 已手动指定",
        "detect_zotero_found": "位置：{path}",
        "detect_found_at": "已找到：{path}",
        "options_title": "确认安装内容",
        "options_subtitle": "请核对将要配置的助手与功能，一般保持默认即可",
        "options_selected": "将配置的 AI 助手：",
        "options_none": "（尚未选择）",
        "options_features": "将安装的功能：",
        "options_locations": "配置位置：",
        "options_not_detected": "（尚未检查）",
        "options_no_target": "（没有可用配置位置，请返回重新选择助手）",
        "options_force": "如已安装过，重新覆盖更新",
        "options_skip_network": "跳过联网检查（可加快安装检查）",
        "options_skip_deps": "跳过可选组件（安装更快；下载全文功能可能不完整）",
        "options_note": "仅会为上一页勾选的助手完成配置与检查。",
        "progress_title": "正在安装",
        "progress_subtitle": "正在配置文献综述所需功能，请稍候",
        "progress_ready": "准备开始…",
        "progress_running": "安装进行中…",
        "progress_done": "安装完成，可进入下一步检查",
        "progress_fail": "安装未成功，请查看说明后返回重试",
        "progress_next": "开始检查",
        "progress_log_ok": "安装已完成，可继续下一步",
        "progress_log_fail": "安装未完成，请根据上方说明返回重试",
        "tests_title": "安装检查",
        "tests_subtitle": "确认功能已正确配置，可正常使用",
        "tests_ready": "准备开始检查…",
        "tests_running": "正在检查，请稍候…",
        "tests_done": "检查通过，可以开始使用",
        "tests_fail": "部分检查未通过，请查看说明；多数情况下仍可继续使用",
        "tests_start_banner": "正在确认功能是否可用…",
        "tests_next_ok": "开始使用",
        "tests_log_ok": "检查完成，可以开始使用",
        "tests_log_fail": "部分项目未通过，可返回重试，或先继续试用",
        "detect_dialog_bad_title": "未识别为 Zotero",
        "detect_dialog_bad_body": "所选位置不是有效的 Zotero 安装：\n{path}\n\n{tip}",
        "detect_dialog_ok_title": "已找到 Zotero",
        "detect_dialog_ok_body": "将使用以下位置：\n{path}",
        "detect_tip_mac": "请选择应用程序中的 Zotero（例如「应用程序」文件夹里的 Zotero）",
        "detect_tip_win": "请选择 Zotero 程序文件（通常名为 zotero.exe）",
        "detect_pick_title_mac": "请选择 Zotero（通常在「应用程序」中）",
        "detect_pick_title_win": "请选择 Zotero 程序",
        "miss_need_assistant": "请先安装 Codex、Claude Code 或 Cursor 中的至少一款",
        "miss_pick_assistant": "请至少勾选一个 AI 助手",
        "miss_assistant_missing": "所选助手尚未安装或未被识别：{labels}",
        "miss_need_zotero": "请先安装 Zotero，或手动指定其位置",
        "install_banner": "开始配置文献综述功能",
        "install_mode": "方式：使用安装程序内置组件（无需额外下载）",
        "install_selected": "将配置：{labels}",
        "install_prepare": "准备安装内容",
        "install_feature": "正在安装：{name}",
        "install_feature_ok": "已完成：{name}",
        "install_deps": "正在完成可选组件配置…",
        "install_verify": "正在确认安装结果…",
        "install_done": "全部配置完成",
        "install_fail": "配置未完成：{error}",
        "install_retry": "可返回上一步后重试",

        "finish_title": "可以开始使用了",
        "finish_subtitle": "接下来只需在 AI 助手里启动文献综述工作流",
        "finish_ok": "配置完成，可以开始使用",
        "finish_partial": "功能已安装。部分检查未通过，您仍可先按下面方式试用",
        "finish_fail": "尚未完成安装，请返回查看说明并重试",
        "finish_how_title": "如何开始（只需 3 步）",
        "finish_step_1": "打开您刚才选择的 AI 助手：Codex、Claude Code 或 Cursor。",
        "finish_step_2": "新建一个对话（或打开一个空白聊天窗口）。",
        "finish_step_3": "把下方生成的启动说明粘贴进去，发送即可。之后按助手的提示一步步操作。",
        "finish_topic_title": "填写主题并复制启动说明",
        "finish_topic_hint": "填写研究主题后点击「复制启动说明」，粘贴到 AI 助手对话中发送。后续检索、Excel 审阅、下载与最终质检都会由助手引导，您无需打开任何说明文件。",
        "finish_topic_label": "研究主题",
        "finish_topic_placeholder": "例如：大语言模型辅助系统综述筛选",
        "finish_generate": "生成启动说明",
        "finish_copy_recommended": "复制启动说明",
        "finish_copied_recommended": "已复制。请打开 AI 助手，粘贴到对话中并发送",
        "finish_need_topic": "请先填写研究主题",
        "finish_generated": "启动说明已生成，可点击复制",
        "finish_note": "之后跟着助手提示操作即可。请勿向助手提供账号密码。",
        "finish_preview": "将粘贴到 AI 助手的内容",
        # Friendly feature names shown to users
        "feat_academic_search": "文献检索 — 按主题检索、核验并导出文献表",
        "feat_download": "全文下载 — 在合法权限下下载 PDF 并整理",
        "feat_workflow": "工作流程指南 — 标准步骤与提示词说明",
    },
    "en": {
        "app_title": "Literature Review Setup",
        "back": "Back",
        "next": "Next",
        "close": "Done",
        "start_install": "Start setup",
        "sidebar_steps": "Setup steps",
        "sidebar_footer": "Literature Review Assistant\nGet ready in a few minutes",
        "step_language": "Language",
        "step_welcome": "Welcome",
        "step_detect": "Check setup",
        "step_options": "Confirm",
        "step_progress": "Installing",
        "step_tests": "Verify",
        "step_finish": "Get started",
        "lang_title": "Choose your language",
        "lang_subtitle": "Instructions will appear in the language you select",
        "lang_zh": "中文",
        "lang_en": "English",
        "lang_hint": "You can return here anytime to change the language.",
        "welcome_title": "Welcome to Literature Review Setup",
        "welcome_subtitle": "Version {version}  ·  Ready in a few minutes",
        "welcome_hero": "Search, screen, and organise literature with AI",
        "welcome_hero_body": "This app configures everything you need. No extra downloads are required during setup.",
        "welcome_body": (
            "After setup, you will have:\n"
            "  1. Literature search — find, verify, and export papers to a spreadsheet\n"
            "  2. Full-text download — download PDFs you are allowed to access\n"
            "  3. Workflow guide — clear steps and ready-to-use prompts\n"
            "\n"
            "Please install first:\n"
            "  • At least one AI assistant: Codex, Claude Code, or Cursor\n"
            "  • Zotero for your reference library\n"
            "\n"
            "Next, choose the assistants you use. Setup applies only to your selection."
        ),
        "welcome_footer": "Tip: All required components are included in this installer.",
        "detect_title": "Check your computer",
        "detect_subtitle": "Select the AI assistants you use. Later steps will configure only those.",
        "detect_choose": "Which AI assistants should we set up? (multiple allowed)",
        "detect_kind_assistant": "AI assistant",
        "detect_kind_library": "Reference manager",
        "detect_refresh": "Check again",
        "detect_select_all": "Select all found",
        "detect_browse_zotero": "Locate Zotero manually…",
        "detect_browse_short": "Locate…",
        "detect_clear_manual": "Clear manual location",
        "detect_need_assistant": "No AI assistant found. Please install one of the following:",
        "detect_need_zotero": "Zotero was not found. Download it, or click “Locate Zotero manually” to choose its location.",
        "detect_download_zotero": "Download Zotero",
        "detect_not_ready": "Please finish this check before continuing",
        "detect_ready": "Selected: {labels}. Setup will apply only to these assistants.",
        "detect_pick_one": "Please select at least one detected assistant",
        "detect_zotero_missing_hint": "Not found. If it is installed elsewhere, click “Locate…”",
        "detect_zotero_manual": "Zotero (reference manager) · manually located",
        "detect_zotero_found": "Location: {path}",
        "detect_found_at": "Found: {path}",
        "options_title": "Confirm what will be set up",
        "options_subtitle": "Review your choices. Defaults are fine for most users.",
        "options_selected": "AI assistants to configure:",
        "options_none": "(none selected)",
        "options_features": "Features to install:",
        "options_locations": "Setup location:",
        "options_not_detected": "(not checked yet)",
        "options_no_target": "(no valid location — go back and reselect assistants)",
        "options_force": "Replace existing features if already installed",
        "options_skip_network": "Skip online connectivity check (faster)",
        "options_skip_deps": "Skip optional components (faster; full-text download may be limited)",
        "options_note": "Only the assistants selected earlier will be configured and checked.",
        "progress_title": "Setting up",
        "progress_subtitle": "Configuring literature-review features. This may take a moment.",
        "progress_ready": "Ready to start…",
        "progress_running": "Setup in progress…",
        "progress_done": "Setup finished. Continue to verification.",
        "progress_fail": "Setup did not finish. Review the message, then go back and try again.",
        "progress_next": "Continue to verify",
        "progress_log_ok": "Setup finished. Continue to the next step.",
        "progress_log_fail": "Setup did not finish. Review the message above and try again.",
        "tests_title": "Verify setup",
        "tests_subtitle": "Confirm everything is ready to use",
        "tests_ready": "Ready to verify…",
        "tests_running": "Verifying, please wait…",
        "tests_done": "Verification passed. You are ready to begin.",
        "tests_fail": "Some checks did not pass. You can often still continue with recommended prompts.",
        "tests_start_banner": "Checking that everything is ready to use…",
        "tests_next_ok": "Get started",
        "tests_log_ok": "Verification complete. You can start now.",
        "tests_log_fail": "Some items did not pass. You can go back and retry, or continue to try the prompts.",
        "detect_dialog_bad_title": "Zotero not recognised",
        "detect_dialog_bad_body": "The selected location does not look like Zotero:\n{path}\n\n{tip}",
        "detect_dialog_ok_title": "Zotero found",
        "detect_dialog_ok_body": "We will use this location:\n{path}",
        "detect_tip_mac": "Please choose the Zotero app (usually in Applications)",
        "detect_tip_win": "Please choose the Zotero program file (usually zotero.exe)",
        "detect_pick_title_mac": "Choose Zotero (usually in Applications)",
        "detect_pick_title_win": "Choose the Zotero program",
        "miss_need_assistant": "Please install at least one of Codex, Claude Code, or Cursor",
        "miss_pick_assistant": "Please select at least one AI assistant",
        "miss_assistant_missing": "The selected assistant was not found: {labels}",
        "miss_need_zotero": "Please install Zotero, or locate it manually",
        "install_banner": "Setting up literature-review features",
        "install_mode": "Using components included in this installer (no extra download)",
        "install_selected": "Configuring: {labels}",
        "install_prepare": "Preparing install contents",
        "install_feature": "Installing: {name}",
        "install_feature_ok": "Finished: {name}",
        "install_deps": "Finishing optional components…",
        "install_verify": "Confirming setup…",
        "install_done": "Setup complete",
        "install_fail": "Setup did not finish: {error}",
        "install_retry": "You can go back and try again",

        "finish_title": "You’re ready to begin",
        "finish_subtitle": "Next: start the literature-review workflow in your AI assistant",
        "finish_ok": "Setup complete. You can start now.",
        "finish_partial": "Features are installed. Some checks failed, but you can still follow the steps below.",
        "finish_fail": "Setup is incomplete. Go back, review the message, and try again.",
        "finish_how_title": "How to start (3 steps)",
        "finish_step_1": "Open the AI assistant you selected: Codex, Claude Code, or Cursor.",
        "finish_step_2": "Start a new chat (or open a blank conversation).",
        "finish_step_3": "Paste the starter message below and send it. Then follow the assistant’s prompts step by step.",
        "finish_topic_title": "Add your topic and copy the starter message",
        "finish_topic_hint": "Enter your research topic, click “Copy starter message”, then paste it into your AI assistant chat. The assistant will guide search, Excel review, download, and the final quality check — you do not need to open any documentation files.",
        "finish_topic_label": "Research topic",
        "finish_topic_placeholder": "e.g. LLM-assisted systematic literature screening",
        "finish_generate": "Create starter message",
        "finish_copy_recommended": "Copy starter message",
        "finish_copied_recommended": "Copied. Open your AI assistant, paste it into the chat, and send",
        "finish_need_topic": "Please enter a research topic first",
        "finish_generated": "Starter message ready — click copy",
        "finish_note": "Just follow the assistant after that. Never share account passwords.",
        "finish_preview": "Message to paste into your AI assistant",
        "feat_academic_search": "Literature search — find, verify, and export papers",
        "feat_download": "Full-text download — download PDFs you may lawfully access",
        "feat_workflow": "Workflow guide — clear steps and prompt templates",
    },
}

# Map internal skill package names → user-facing feature keys
FEATURE_KEYS = {
    "academic-search": "feat_academic_search",
    "sciencedirect-live-session-fetcher": "feat_download",
    "literature-review-workflow": "feat_workflow",
}


def get_language() -> str:
    return _LANG


def set_language(lang: str) -> None:
    global _LANG
    _LANG = "en" if lang == "en" else "zh"


def t(key: str, **kwargs: Any) -> str:
    table = STRINGS.get(_LANG) or STRINGS["zh"]
    text = table.get(key) or STRINGS["zh"].get(key) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    return text


def feature_label(skill_name: str, fallback: str = "") -> str:
    key = FEATURE_KEYS.get(skill_name)
    if key:
        return t(key)
    return fallback or skill_name


def wizard_steps() -> tuple[str, ...]:
    return (
        t("step_language"),
        t("step_welcome"),
        t("step_detect"),
        t("step_options"),
        t("step_progress"),
        t("step_tests"),
        t("step_finish"),
    )
