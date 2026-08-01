# AI Literature Review Workflow Installer

图形化双平台安装向导，用于检测环境、安装并验证文献综述工作流所需的两个 Skills：

1. [`academic-search`](https://github.com/ustc-ai4science/academic-search)
2. [`sciencedirect-live-session-fetcher`](https://github.com/Given-Dream/sciencedirect-live-session-fetcher)

工作流参考：`AI_Based_Literature_Review_Workflow_Refined-20260730.docx`

**离线安装**：安装包内已包含 `bundled/skills` 与依赖 wheels，安装时只做本地复制，不再从 GitHub 克隆。

## 普通用户：图形安装包

| 系统 | 安装文件 |
|------|----------|
| macOS | `dist/LiteratureReviewInstaller-macOS.dmg` |
| Windows | `dist/LiteratureReviewInstaller-windows.exe` |

使用步骤：

1. 双击打开对应平台的安装文件  
2. 按向导完成：语言（中/英）→ 欢迎 → 环境检测 → 安装选项 → 安装进度 → 标准化测试 → 完成  
3. 检测要求：至少安装 **Codex / Claude Code / Cursor** 之一，以及 **Zotero**  
4. 完成页只需填写研究主题并复制「启动说明」，粘贴到 Codex / Cursor 对话即可开始；后续由助手引导  
5. 安装会附带文献综述工作流能力，由助手在对话中逐步引导，用户无需自行打开说明文件

下载地址（检测失败时向导内也会提供）：

- Codex: https://chatgpt.com/codex  
- Claude Code: https://docs.anthropic.com/en/docs/claude-code/overview  
- Cursor: https://cursor.com/download  
- Zotero: https://www.zotero.org/download/

说明：安装包默认未签名。macOS 首次打开可能需要「右键 → 打开」或在「系统设置 → 隐私与安全性」中允许；Windows 可能被 SmartScreen 拦截，选择「仍要运行」即可。

## 开发者：本地运行向导

```bash
cd /path/to/paper_download_app
python3 run_gui.py
```

依赖：系统 Python 3.10+（使用标准库 `tkinter`）、`node`（academic-search 自检）。Skills 本体来自仓库内 `bundled/`，运行安装向导不再需要 git/联网。

## 打包安装文件

### macOS（在 Mac 上执行）

```bash
bash build/build_macos.sh
```

产物：

- `dist/LiteratureReviewInstaller-macOS.dmg`
- `dist/LiteratureReviewInstaller.app`

### Windows（必须在 Windows 上执行）

macOS **无法**直接打出可用的 Windows `.exe`（PyInstaller 不支持可靠交叉编译 GUI）。请任选其一：

**方式 A：本机 Windows**

```powershell
cd path\to\paper_download_app
powershell -ExecutionPolicy Bypass -File build\build_windows.ps1
```

产物：`dist\LiteratureReviewInstaller-windows.exe`

**方式 B：GitHub Actions（推荐）**

1. 将本仓库推送到 GitHub  
2. 打开 Actions → **Build Installers** → **Run workflow**  
3. 结束后下载产物 `LiteratureReviewInstaller-windows`

构建依赖见 `requirements-gui.txt`（仅打包机需要）。

## CLI 备用（macOS / Linux）

```bash
bash ./install.sh
bash ./install.sh --detect-only
bash ./uninstall.sh
```

## 安装后 Skills 位置

- Codex → `~/.codex/skills/`
- Claude Code → `~/.claude/skills/`
- Cursor → `~/.cursor/skills/`

Windows 下对应 `%USERPROFILE%\.codex\skills` 等。

## 推荐使用流程

见 `templates/search-prompt.md`。概要：

1. 用 `academic-search` 检索并导出 Excel  
2. 人工审阅，标记 `Approved = Yes/No`  
3. 浏览器中自行登录机构权限后，用下载技能抓取 PDF  
4. 整理进 Zotero，并做最终对账  
