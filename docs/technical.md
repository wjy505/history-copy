# 技术选型与架构说明

## 技术栈

| 层面 | 选择 | 版本 | 说明 |
|---|---|---|---|
| 语言 | Python | 3.11.7 | 系统已安装 |
| UI 框架 | PySide6 | ≥6.5.0 | Qt for Python，LGPL 许可 |
| Windows API | pywin32 | ≥306 | 剪贴板操作、窗口管理 |
| 图片处理 | Pillow | ≥10.0.0 | 图片缩放与缩略图 |
| 数据库 | SQLite3 + FTS5 | Python 内置 | 嵌入式、全文搜索 |
| 打包 | PyInstaller | 最新 | 单 exe 输出 |

## 选型理由

### 为什么不用 Electron？
- Electron 打包后体积 150MB+，启动慢，内存占用高
- 对于后台常驻的剪贴板工具来说过于臃肿
- PySide6 打包约 50-60MB，内存占用更低

### 为什么不用 tkinter？
- tkinter 无法实现现代化的卡片式 UI
- QSS（Qt Style Sheets）可以实现更好的视觉效果
- PySide6 原生支持系统托盘 `QSystemTrayIcon`

### 为什么用 SQLite 而不是纯文件存储？
- 全文搜索（FTS5）开箱即用
- 结构化查询效率高
- WAL 模式保证崩溃安全
- 无需单独的数据库进程

## 架构概览

```
main.py (入口)
  └── Application (src/app/application.py)
        ├── ConfigManager (src/storage/config.py)
        ├── ClipboardDatabase (src/storage/database.py)
        ├── ImageStore (src/storage/image_store.py)
        ├── ClipboardMonitor (src/clipboard/monitor.py)
        │     ├── ClipboardReader (src/clipboard/reader.py)
        │     └── ClipboardWriter (src/clipboard/writer.py)
        ├── HotkeyManager (src/hotkey/manager.py)
        ├── PasteEngine (src/paste/engine.py)
        ├── CleanupScheduler (src/cleanup/scheduler.py)
        ├── SystemTray (src/ui/tray.py)
        ├── HistoryPanel (src/ui/panel.py)
        │     ├── ClipboardCard (src/ui/card.py)
        │     └── SearchBar (src/ui/search_bar.py)
        ├── SettingsDialog (src/ui/settings_dialog.py)
        └── Theme (src/ui/theme.py)
```

## 数据流

### 剪贴板捕获
```
用户按 Ctrl+C → Windows 剪贴板更新 → WM_DRAWCLIPBOARD 消息
→ ClipboardMonitor 读取格式 → ClipboardReader 提取内容
→ 计算 SHA256 → 去重判断 → ClipboardDatabase.insert_item()
→ (如果是图片) ImageStore.save_image()
→ 发送信号 (若面板可见则刷新列表)
```

### 粘贴流程
```
用户按 Alt+V → HotkeyManager 记录前台窗口 HWND
→ HistoryPanel 显示 → 用户双击卡片
→ ClipboardWriter 设置剪贴板
→ PasteEngine 恢复前台窗口 → 模拟 Ctrl+V
→ HistoryPanel 隐藏
```

## 存储结构

### 数据库 (clipboard.db)
```sql
CREATE TABLE clipboard_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type    TEXT NOT NULL CHECK(content_type IN ('text', 'image')),
    text_content    TEXT,
    image_path      TEXT,
    thumbnail_path  TEXT,
    app_source      TEXT,
    content_hash    TEXT,
    is_pinned       INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    accessed_at     TEXT
);

CREATE VIRTUAL TABLE items_fts USING fts5(
    text_content, content='clipboard_items', content_rowid='id'
);
```

### 文件存储
```
%APPDATA%/ClipboardHistory/
  ├── clipboard.db          # SQLite 数据库
  ├── config.json           # 用户配置
  └── images/
      ├── 1.png             # 全尺寸图片 (id=1)
      ├── 1_thumb.png       # 缩略图 (200px)
      ├── 3.png
      └── 3_thumb.png
```

### 配置文件格式 (config.json)
```json
{
    "storage_duration_days": 3,
    "hotkey": "alt+v",
    "max_image_width": 1200,
    "panel_width": 400,
    "panel_height": 600,
    "start_with_windows": false
}
```

## 线程模型

- **主线程**：Qt 事件循环、UI 渲染、用户交互
- **剪贴板监听**：独立线程，Win32 消息循环
- **线程间通信**：Qt Signals/Slots（线程安全）
- **数据库访问**：SQLite 连接仅主线程使用（通过信号传递数据）

## 关键 Windows API

| 用途 | API |
|---|---|
| 剪贴板读取 | `win32clipboard.OpenClipboard()`, `GetClipboardData()` |
| 剪贴板写入 | `win32clipboard.EmptyClipboard()`, `SetClipboardData()` |
| 剪贴板监听 | `SetClipboardViewer()`, `WM_DRAWCLIPBOARD`, `WM_CHANGECBCHAIN` |
| 窗口管理 | `win32gui.GetForegroundWindow()`, `SetForegroundWindow()` |
| 全局热键 | `win32gui.RegisterHotKey()`, `WM_HOTKEY` |
| 按键模拟 | `win32api.keybd_event()` 或 `SendInput` |
| 单实例 | `win32event.CreateMutex()` |

## 打包配置

- 工具：PyInstaller 6.x
- 模式：`--onefile --windowed`
- 图标：`resources/icon.ico`（256×256 多分辨率）
- 预期大小：50-60 MB
- 隐藏导入：pywin32 子模块、Pillow 子模块
