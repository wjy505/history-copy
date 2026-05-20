# 执行步骤清单

## 第 0 阶段：项目初始化 ✅ 已完成

- [x] 创建目录结构
- [x] 编写 requirements.txt
- [x] 安装依赖（conda 环境 clipboard-history）
- [x] 创建 src 子包 __init__.py
- [x] 编写 docs/requirements.md
- [x] 编写 docs/technical.md
- [x] 编写 docs/design.md
- [x] 编写 docs/roadmap.md
- [x] 编写 docs/changelog.md
- [x] 编写 CLAUDE.md
- [x] 创建首条开发日志

## 第 1 阶段：存储层 ✅ 已完成

- [x] 实现 src/storage/config.py
- [x] 实现 src/storage/database.py
- [x] 实现 src/storage/image_store.py
- [x] 编写数据层测试脚本并验证

## 第 2 阶段：剪贴板核心 ✅ 已完成

- [x] 实现 src/clipboard/reader.py
- [x] 实现 src/clipboard/writer.py
- [x] 实现 src/clipboard/monitor.py
- [x] 测试剪贴板读写

## 第 3 阶段：UI 基础 ✅ 已完成

- [x] 实现 src/ui/theme.py
- [x] 实现 src/ui/tray.py
- [x] 实现 main.py（最小可运行版本）
- [x] 测试：托盘运行、剪贴板静默记录

## 第 4 阶段：面板 UI ✅ 已完成

- [x] 实现 src/ui/card.py
- [x] 实现 src/ui/search_bar.py
- [x] 实现 src/ui/panel.py
- [x] 连接应用信号：面板显隐/数据刷新

## 第 5 阶段：粘贴与热键 ✅ 已完成

- [x] 实现 src/hotkey/manager.py
- [x] 实现 src/paste/engine.py
- [x] 连接信号：热键→面板、双击→粘贴
- [ ] 在记事本和浏览器中测试

## 第 6 阶段：高级功能

- [ ] 实现置顶/取消置顶
- [ ] 实现删除（二次确认）
- [ ] 实现 src/cleanup/scheduler.py
- [ ] 实现 src/ui/settings_dialog.py

## 第 7 阶段：打磨与测试

- [ ] 边界情况处理
- [ ] 窗口失去焦点自动隐藏
- [ ] 多屏 DPI 适配
- [ ] 整体功能走查

## 第 8 阶段：打包发布

- [ ] 编写 build.spec
- [ ] PyInstaller 打包
- [ ] 干净环境测试
- [ ] 编写用户使用说明
