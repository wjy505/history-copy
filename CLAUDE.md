# CLAUDE.md — 历史粘贴板项目指引

## 项目简介

Windows 剪贴板历史管理软件。后台静默运行于系统托盘，自动记录文字/图片复制内容。快捷键 Alt+V 呼出面板，可搜索、置顶、删除，双击粘贴。

- **用户**：非技术人员（面向普通用户）
- **平台**：Windows 11
- **语言**：界面和文档均为中文
- **技术栈**：Python 3.11 + PySide6 + SQLite + pywin32 + Pillow

## 标准文件路径

| 文件 | 路径 | 说明 |
|---|---|---|
| 开发计划 | `C:\Users\tianxuan3plus\.claude\plans\window1-1-3-5-binary-leaf.md` | 完整计划文件 |
| 需求规格 | [docs/requirements.md](docs/requirements.md) | 功能需求与非功能需求 |
| 技术说明 | [docs/technical.md](docs/technical.md) | 技术选型、架构、数据流 |
| 设计规范 | [docs/design.md](docs/design.md) | UI 色彩、组件、动效规范 |
| 执行步骤 | [docs/roadmap.md](docs/roadmap.md) | 分阶段任务清单 |
| 变更日志 | [docs/changelog.md](docs/changelog.md) | 版本变更记录 |
| 开发日志 | [devlog/](devlog/) | 按日期命名的每日开发日志 |

## 开发规范

1. **每阶段开始前**：查看 [docs/roadmap.md](docs/roadmap.md) 确认当前阶段任务
2. **写 UI 代码前**：查看 [docs/design.md](docs/design.md) 确认色彩和组件规范
3. **每次会话结束前**：更新当天的 [devlog/YYYY-MM-DD.md](devlog/) 开发日志
4. **完成每个阶段后**：更新 [docs/roadmap.md](docs/roadmap.md) 勾选已完成项
5. **代码风格**：所有注释和 UI 文字使用中文
6. **不要一口气做太多**：每个阶段完成后停下来验证，再进入下一阶段
7. **项目目录**：所有路径相对于 `c:\Users\tianxuan3plus\Desktop\历史粘贴\`

## 项目结构
```
src/
  app/application.py      # 应用控制器
  clipboard/              # 剪贴板读写监听
  hotkey/manager.py       # 全局热键
  storage/                # 数据库/图片/配置
  ui/                     # 主题/托盘/面板/卡片/搜索/设置
  paste/engine.py         # 粘贴引擎
  cleanup/scheduler.py    # 定时清理
```

## 运行方式

开发阶段直接运行 `python main.py`，最终阶段用 PyInstaller 打包为单 exe。
