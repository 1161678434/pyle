# clipmanager - Windows 剪贴板 + 截长图工具

## 概述

一个常驻 Windows 系统托盘的 PyQt6 桌面工具，集成剪贴板历史管理和截长图两大功能。

## 技术栈

- **UI**: PyQt6（原生 Windows 桌面）
- **图像**: Pillow + OpenCV（截图拼接、标注渲染）
- **系统**: pywin32（剪贴板监听、全局热键、窗口操作）
- **存储**: SQLite（剪贴板历史、配置）
- **打包**: PyInstaller → 单 exe

## 架构

```
┌─────────────────────────────────────────┐
│              PyQt6 主进程                │
│                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │TrayManager│ │Clipboard │ │Screenshot│ │
│  │托盘/热键  │ │ Manager  │ │ Engine   │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ │
│       │            │            │       │
│  ┌────┴────────────┴────────────┴─────┐ │
│  │         事件 / 数据总线             │ │
│  └────┬────────────┬────────────┬─────┘ │
│  ┌────┴─────┐ ┌────┴──────┐ ┌───┴─────┐ │
│  │Annotator │ │ClipPopup │ │Settings │ │
│  │标注 Overlay│ │历史弹窗  │ │设置窗口 │ │
│  └──────────┘ └──────────┘ └─────────┘ │
└─────────────────────────────────────────┘
```

## 模块设计

### 1. TrayManager — 系统托盘 + 全局热键

- 托盘图标右键菜单：截长图、区域截图、剪贴板历史、设置、退出
- 注册全局热键，所有热键可在设置中自定义
- 热键触发 → 发射对应信号到主控制器

### 2. ClipboardManager — 剪贴板监听

- 使用 `QClipboard.dataChanged` 和 Win32 剪贴板链监听
- 捕获文本和图片（忽略文件、特殊格式）
- 内容去重：连续相同内容不重复记录
- 图片自动压缩存储（长边 ≤ 1200px，JPEG quality 80）
- 超出上限自动清理最旧记录
- 排除规则：匹配正则的应用不记录（默认：KeePass、1Password）

### 3. ScreenshotEngine — 截图引擎

**区域截图**：
- 全屏半透明蒙版，鼠标拖拽选区
- 选区实时显示尺寸（W×H px）
- 支持吸附窗口边缘、吸附选区边缘

**截长图**：
- 选择目标窗口 → 自动滚动 → 逐帧捕获
- OpenCV 特征匹配拼接相邻帧
- 进度条显示（捕获中 / 拼接中）
- 可手动设置最大滚动次数

### 4. AnnotationWindow — 标注编辑器

全屏 overlay，截图区域高亮，周围半透明黑色蒙版。字体统一使用微软雅黑。

| 工具 | 快捷键 | 说明 |
|------|--------|------|
| 矩形框 | R | 拖拽绘制，红色 2px 边框 |
| 箭头 | A | 拖拽线段，终点带箭头 |
| 文字 | T | 点击放置，6~48px 可调，无衬线字体 |
| 马赛克 | M | 拖拽矩形，高斯模糊 r=15 |
| 撤销 | Ctrl+Z | 撤销上一个标注 |
| 确认 | Enter | 复制到剪贴板 + 保存文件 |
| 取消 | Esc | 放弃 |

### 5. ClipPopup — 剪贴板历史弹窗

**方案 A：大预览 + 类型图标**，全局字体微软雅黑。

```
┌──────────────────────────────┐
│  📋 剪贴板           [6 条]  │
├──────────────────────────────┤
│ 📝  item["price"]*item["qty"]│
│     3 分钟前                 │  ← 选中项（蓝色背景）
│ 📝  def process_data(df):    │
│     12 分钟前                │
│ 🖼️  [缩略图预览]             │
│     28 分钟前                │
│ 📝  https://github.com/...   │
│     1 小时前                 │
├──────────────────────────────┤
│ ↑↓ 选择  Enter 粘贴  Del 删除│
└──────────────────────────────┘
```

- 定位：有焦点输入框→光标位置；否则→鼠标位置
- 超出屏幕自动翻转（上下/左右）
- 交互：↑↓ 选择、Enter/双击粘贴、Del 删除、Esc 关闭
- 输入即搜索过滤
- 图片条目显示缩略图而非原始图标

### 6. SettingsWindow — 设置窗口

三个标签页：常规 / 热键 / 剪贴板

**常规**：保存路径、图片格式（PNG/JPEG/WebP）、开机自启、截图提示音

**热键**：全部热键可点击重录，默认值：

| 功能 | 默认热键 |
|------|---------|
| 区域截图 | Ctrl+Shift+A |
| 截长图 | Ctrl+Shift+L |
| 剪贴板历史 | Ctrl+Shift+V |
| 快速截屏到剪贴板 | Print Scr |

**剪贴板**：最大记录数（默认 200）、自动清理天数（默认 30）、图片最大缓存（默认 50MB）、排除应用正则

## 数据模型 (SQLite)

```sql
CREATE TABLE clipboard_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK(type IN ('text','image')),
    content TEXT,           -- 文本内容或图片文件路径
    size_bytes INTEGER,     -- 原始大小
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

图片以文件形式存储在 `%APPDATA%/clipmanager/images/`，数据库只存路径。

## 配置持久化

设置保存在 SQLite `settings` 表，热键序列化为 JSON 存储。首次运行写入默认值。

## 错误处理

- 全局热键注册失败 → 弹窗提示冲突，建议修改热键
- 截长图窗口失去响应 → 超时 30s 自动取消
- 剪贴板监听异常 → 自动重试，不提示用户
- 磁盘空间不足 → 保存时弹窗警告

## 项目结构（目标）

```
clipmanager/
├── main.py              # 入口，初始化 QApplication
├── tray_manager.py      # 托盘 + 热键
├── clipboard_manager.py # 剪贴板监听 + 存储
├── screenshot_engine.py # 区域截图 + 截长图
├── annotation_window.py # 标注编辑器
├── clip_popup.py        # 剪贴板历史弹窗
├── settings_window.py   # 设置面板
├── db.py                # 数据库操作
├── hotkey.py            # 全局热键工具
└── utils.py             # 通用工具
```

## 非功能需求

- 内存占用：静默时 < 50MB
- 启动速度：冷启动 < 2s
- 打包：单个 exe，< 80MB
