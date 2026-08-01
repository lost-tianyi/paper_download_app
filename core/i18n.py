"""Minimal Chinese / English strings for the installer wizard."""

from __future__ import annotations

from typing import Any

_LANG = "zh"

STRINGS: dict[str, dict[str, str]] = {
    "zh": {
        "app_title": "Literature Review Installer",
        "back": "上一步",
        "next": "下一步",
        "close": "关闭",
        "sidebar_steps": "安装步骤",
        "sidebar_footer": "AI 文献综述工作流\n离线 Skills 安装向导",
        "step_language": "语言",
        "step_welcome": "欢迎",
        "step_detect": "环境检测",
        "step_options": "安装选项",
        "step_progress": "安装进度",
        "step_tests": "标准化测试",
        "step_finish": "完成",
        "lang_title": "选择语言 / Language",
        "lang_subtitle": "请选择安装向导使用的语言",
        "lang_zh": "中文",
        "lang_en": "English",
        "lang_hint": "选择后可随时返回本页切换语言。",
        "welcome_title": "欢迎使用 Literature Review Installer",
        "welcome_subtitle": "版本 {version} · 图形化离线安装向导",
        "welcome_hero": "AI 文献综述工作流 · 一键就绪",
        "welcome_hero_body": "安装包已内置全部 Skills 素材，安装过程本地复制，无需再联网拉取仓库。",
        "welcome_body": (
            "将安装的 Skills：\n"
            "  1. academic-search — 学术检索、DOI 核验、结构化导出\n"
            "  2. sciencedirect-live-session-fetcher — 合法会话下串行下载 PDF\n"
            "  3. literature-review-workflow — 工作流说明与提示词模板（供助手参考）\n"
            "\n"
            "安装目标目录（按你勾选的助手）：\n"
            "  • Codex  → ~/.codex/skills/\n"
            "  • Claude → ~/.claude/skills/\n"
            "  • Cursor → ~/.cursor/skills/\n"
            "\n"
            "开始前请确保已安装：\n"
            "  • 至少一个你要用的 AI 编程助手（Codex / Claude Code / Cursor）\n"
            "  • Zotero\n"
            "\n"
            "下一步可勾选要使用的助手；安装与测试只针对勾选项。"
        ),
        "welcome_footer": "素材目录：bundled/skills（已打入安装程序）",
        "detect_title": "环境检测",
        "detect_subtitle": "勾选你要使用的 AI 编程助手；后续安装与测试只针对勾选项",
        "options_title": "安装选项",
        "options_subtitle": "确认将写入的目录与可选行为",
        "progress_title": "安装进度",
        "progress_subtitle": "正在从安装包复制 Skills（离线）",
        "tests_title": "标准化测试",
        "tests_subtitle": "验证 Skills 布局与基础能力",
        "finish_title": "安装完成",
        "finish_subtitle": "环境已就绪，可以开始文献综述工作流",
        "finish_ok": "安装完成：检测通过 · Skills 已就位 · 测试通过",
        "finish_partial": "Skills 已安装；部分测试未通过，仍可生成/复制提示词试用",
        "finish_fail": "安装未完成：请返回查看日志并重试",
        "finish_next_steps": "建议下一步：",
        "finish_step_1": "打开你勾选的 AI 编程助手（Codex / Claude Code / Cursor）。",
        "finish_step_2": "输入检索主题，生成并复制推荐提示词，用 academic-search 检索并导出 Excel。",
        "finish_step_3": "人工审阅，标记 Approved = Yes/No。",
        "finish_step_4": "机构权限场景下先在浏览器登录，再粘贴下载提示词处理 Approved 记录。",
        "finish_step_5": "整理进 Zotero，并做最终对账。可参考已安装的 literature-review-workflow 技能。",
        "finish_topic_title": "按主题生成推荐提示词",
        "finish_topic_hint": "输入你的检索主题，将按工作流模板自动替换关键词并生成可复制的检索提示词。",
        "finish_topic_label": "检索主题",
        "finish_topic_placeholder": "例如：LLM-assisted systematic literature review",
        "finish_generate": "生成推荐提示词",
        "finish_copy_recommended": "复制推荐提示词",
        "finish_copy_search": "复制通用检索模板",
        "finish_copy_download": "复制下载提示词",
        "finish_copied_recommended": "已复制推荐提示词到剪贴板",
        "finish_copied_search": "已复制检索模板到剪贴板",
        "finish_copied_download": "已复制下载提示词到剪贴板",
        "finish_need_topic": "请先输入检索主题",
        "finish_generated": "已根据主题生成推荐提示词",
        "finish_template_path": "完整模板文件：{path}",
        "finish_note": "注意：不要向助手提供账号密码；仅使用你已授权的合法访问。",
        "finish_preview": "推荐提示词预览",
    },
    "en": {
        "app_title": "Literature Review Installer",
        "back": "Back",
        "next": "Next",
        "close": "Close",
        "sidebar_steps": "Steps",
        "sidebar_footer": "AI literature-review workflow\nOffline skills installer",
        "step_language": "Language",
        "step_welcome": "Welcome",
        "step_detect": "Detect",
        "step_options": "Options",
        "step_progress": "Install",
        "step_tests": "Tests",
        "step_finish": "Finish",
        "lang_title": "Choose language / 选择语言",
        "lang_subtitle": "Select the language for this installer",
        "lang_zh": "中文",
        "lang_en": "English",
        "lang_hint": "You can return here later to switch languages.",
        "welcome_title": "Welcome to Literature Review Installer",
        "welcome_subtitle": "Version {version} · Offline graphical installer",
        "welcome_hero": "AI literature-review workflow · ready in one pass",
        "welcome_hero_body": "All skill packages are bundled offline. Installation copies locally and does not clone from GitHub.",
        "welcome_body": (
            "Skills to install:\n"
            "  1. academic-search — search, DOI verification, structured export\n"
            "  2. sciencedirect-live-session-fetcher — lawful serial PDF download via live browser session\n"
            "  3. literature-review-workflow — workflow guide and prompt templates for assistants\n"
            "\n"
            "Install targets (for the assistants you select):\n"
            "  • Codex  → ~/.codex/skills/\n"
            "  • Claude → ~/.claude/skills/\n"
            "  • Cursor → ~/.cursor/skills/\n"
            "\n"
            "Before you start, please install:\n"
            "  • At least one coding assistant (Codex / Claude Code / Cursor)\n"
            "  • Zotero\n"
            "\n"
            "Next you can select assistants; install and tests apply only to your selection."
        ),
        "welcome_footer": "Bundle path: bundled/skills (shipped inside the installer)",
        "detect_title": "Environment check",
        "detect_subtitle": "Select the AI coding assistants to use; later steps follow this selection",
        "options_title": "Install options",
        "options_subtitle": "Confirm target folders and optional behaviour",
        "progress_title": "Installation progress",
        "progress_subtitle": "Copying skills from the offline bundle",
        "tests_title": "Standard tests",
        "tests_subtitle": "Validate skill layout and basic capabilities",
        "finish_title": "Installation complete",
        "finish_subtitle": "Your environment is ready for the literature-review workflow",
        "finish_ok": "Done: detection passed · skills installed · tests passed",
        "finish_partial": "Skills installed; some tests failed — you can still generate/copy prompts",
        "finish_fail": "Install incomplete: go back, check logs, and retry",
        "finish_next_steps": "Suggested next steps:",
        "finish_step_1": "Open your selected assistant (Codex / Claude Code / Cursor).",
        "finish_step_2": "Enter a research topic, generate the recommended prompt, then run academic-search and export Excel.",
        "finish_step_3": "Human review: mark Approved = Yes/No.",
        "finish_step_4": "For institutional access, sign in via the browser yourself, then run the download prompt on Approved rows.",
        "finish_step_5": "Organise into Zotero and reconcile. See the installed literature-review-workflow skill for reference.",
        "finish_topic_title": "Generate a topic-specific prompt",
        "finish_topic_hint": "Enter your research topic. Placeholders in the workflow template will be filled automatically.",
        "finish_topic_label": "Research topic",
        "finish_topic_placeholder": "e.g. LLM-assisted systematic literature review",
        "finish_generate": "Generate recommended prompt",
        "finish_copy_recommended": "Copy recommended prompt",
        "finish_copy_search": "Copy generic search template",
        "finish_copy_download": "Copy download prompt",
        "finish_copied_recommended": "Recommended prompt copied",
        "finish_copied_search": "Search template copied",
        "finish_copied_download": "Download prompt copied",
        "finish_need_topic": "Please enter a research topic first",
        "finish_generated": "Recommended prompt generated from your topic",
        "finish_template_path": "Full template file: {path}",
        "finish_note": "Do not give passwords to the assistant. Use only access you are authorised to use.",
        "finish_preview": "Recommended prompt preview",
    },
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
