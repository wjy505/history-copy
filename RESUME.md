# 历史粘贴板 — 项目简历

## 项目介绍

Windows 剪贴板历史管理桌面软件，面向非技术用户。运行于系统托盘，后台静默监控剪贴板变化，自动记录所有复制的文字和图片内容。用户通过全局热键（Ctrl+Shift+A）呼出历史面板，以卡片形式按时间倒序浏览、搜索、置顶、删除历史记录，双击卡片即可将内容自动粘贴回光标所在位置。支持 1/3/5 天存储期限设置，到期自动清理。最终通过 PyInstaller 打包为 57MB 单文件 exe，无需安装，双击即用。

## 技术栈

| 层面 | 技术 | 说明 |
|---|---|---|
| 语言 | Python 3.11 | 跨平台，生态丰富 |
| UI 框架 | PySide6 (Qt 6) | 原生 Windows 系统托盘、QSS 样式表、卡片式组件 |
| Windows API | pywin32 / ctypes | 剪贴板读写、前台窗口切换、按键模拟 |
| 全局热键 | keyboard 库 | 低级键盘钩子，无管理员权限 |
| 数据库 | SQLite + FTS5 | 嵌入式全文搜索，WAL 模式崩溃安全 |
| 图片处理 | Pillow (PIL) | 图片缩放、缩略图生成、格式转换 |
| 打包分发 | PyInstaller | --onefile + --windowed，单 exe 输出 |

## 技术亮点

### 1. 跨线程剪贴板监听方案

Windows 剪贴板 API（`OpenClipboard`）要求调用线程拥有有效的窗口句柄和消息泵。最初尝试在后台线程中轮询 `GetClipboardSequenceNumber()`，但剪贴板读取频繁因缺少 HWND 而静默失败。最终采用 **QTimer 主线程轮询 + QClipboard 文本读取 + pywin32 图片读取** 的混合方案：文字通过 `QApplication.clipboard().text()` 读取（Qt 内部持有有效 HWND），图片通过 `win32clipboard` API 先检测 CF_DIB 格式再 DIB→PIL 转换。通过 SHA256 哈希比对最近一条记录实现连续复制去重，300ms 防抖避免高频磁盘写入。

### 2. 全局热键的跨线程信号传递

`keyboard` 库的低级键盘钩子回调在后台线程执行，无法直接操作 Qt 控件或发射信号到主线程的事件循环。设计了一个 **标志位 + QTimer 轮询** 的轻量级桥接方案：回调线程仅设置原子布尔标志位，主线程 QTimer 每 50ms 检查标志位，置位时触发 `HotkeyManager.triggered` 信号。避免了 `QMetaObject.invokeMethod` 的序列化开销和 `QueuedConnection` 的潜在丢信号问题。

### 3. 双击事件冒泡模拟

卡片组件内部包含 QLabel 子控件用于显示文字预览，而 Qt 默认不会将子控件上的鼠标事件冒泡到父级。用户在文字区域双击时，事件被 QLabel 消耗，`QFrame.mouseDoubleClickEvent` 从未触发。通过 **安装 `eventFilter` 到内部内容容器**，在 `eventFilter()` 中检测 `MouseButtonDblClick` 事件类型，主动触发卡片的 `double_clicked` 信号，实现了"点击子控件即触发卡片双击"的交互效果。

### 4. 无标题栏面板的焦点管理

历史面板采用 `Qt.FramelessWindowHint | Qt.Tool` 无边框工具窗口，需要实现"失去焦点自动隐藏"的用户体验。通过在 `focusOutEvent` 中启动 200ms 延迟检查 `isActiveWindow()`，并同时检测是否有模态对话框（如设置窗口）处于打开状态，避免了以下场景的误隐藏：① 子控件间焦点转移导致面板闪现后消失；② 右键菜单弹出时意外隐藏；③ 设置对话框打开后面板被提前关闭。

### 5. 前台窗口自动粘贴

双击卡片后需要将内容粘贴回用户此前工作的窗口。由于 Windows 对 `SetForegroundWindow` 有严格的安全限制（仅前台进程可更改前台窗口），放弃了主动切换窗口的方案，改为更简洁的策略：**先隐藏面板 → 等待焦点自动回归 → SendInput/低级键盘钩子发送 Ctrl+V**。利用 `Qt.Tool` 窗口隐藏后 Windows 自动将焦点归还给上一个活动窗口的机制，避免了 `AttachThreadInput` 的复杂性和兼容性风险。

### 6. 单实例互斥体保护

使用 Win32 命名 `Mutex`（`CreateMutex`）在进程启动时检查 `ERROR_ALREADY_EXISTS`，防止用户双击 exe 产生重复托盘图标和剪贴板监听线程。这是 Windows 桌面应用的标准做法，确保系统托盘只有一个实例运行。

### 7. PyInstaller 打包的 DLL 依赖修复

打包后的 exe 运行时抛出 `ImportError: DLL load failed while importing _sqlite3`，原因是 PyInstaller 未自动收集 conda 环境中的 `sqlite3.dll` 和 `_sqlite3.pyd`。通过在 `.spec` 文件的 `binaries` 字段中显式指定路径，将 SQLite 动态库嵌入到 .exe 的 CArchive 中，解决了打包后的运行时依赖缺失问题。
