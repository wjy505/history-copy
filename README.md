# 历史粘贴板

Windows 剪贴板历史管理软件。后台运行于系统托盘，自动记录复制的文字和图片，快捷键呼出面板，搜索、置顶、删除，双击粘贴。

## 功能

- 后台自动记录剪贴板文字和图片
- Ctrl+Shift+A 全局热键呼出面板
- 卡片式历史列表，时间倒序排列
- 全文模糊搜索
- 双击卡片自动粘贴到光标位置
- 置顶重要内容，永久保留
- 可设置 1/3/5 天存储期限，到期自动清理
- 单文件 exe，无需安装

## 截图

启动后系统托盘出现淡蓝色图标。点击图标或按 Ctrl+Shift+A 打开历史面板。

## 下载

从 [Releases](https://github.com/wjy505/history-copy/releases) 下载最新 `ClipboardHistory.exe`，双击运行。

## 开发

### 环境

- Python 3.11
- conda 环境：`clipboard-history`（或 `cliphist`）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行

```bash
python main.py
```

### 打包

```bash
pip install pyinstaller
pyinstaller ClipboardHistory.spec --clean --noconfirm
```

## 技术栈

Python 3.11 · PySide6 (Qt 6) · SQLite + FTS5 · pywin32 · Pillow · keyboard · PyInstaller

## 项目结构

```
├── main.py                  # 入口
├── src/
│   ├── app/application.py   # 应用控制器
│   ├── clipboard/           # 剪贴板读写监听
│   ├── hotkey/manager.py    # 全局热键
│   ├── storage/             # 数据库/图片/配置
│   ├── ui/                  # 主题/托盘/面板/卡片/搜索/设置
│   ├── paste/engine.py      # 粘贴引擎
│   └── cleanup/scheduler.py # 定时清理
├── docs/                    # 需求/技术/设计文档
├── devlog/                  # 开发日志
└── resources/               # 图标
```
