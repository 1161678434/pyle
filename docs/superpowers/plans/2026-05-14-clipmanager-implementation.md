# ClipManager Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Windows system-tray app combining clipboard history management and scrolling screenshot capture.

**Architecture:** PyQt6 single-process desktop app. System tray icon drives a global hotkey system. ClipboardManager polls clipboard via QClipboard + Win32 hooks and persists to SQLite. ScreenshotEngine handles region selection and auto-scroll capture. AnnotationWindow is a fullscreen overlay for drawing on captures. ClipPopup is a borderless popup that follows cursor/focus. All modules communicate via Qt signals through `main.py`.

**Tech Stack:** Python 3.10+, PyQt6, Pillow, OpenCV (cv2), pywin32, SQLite (sqlite3 stdlib)

---

## File Structure

```
clipmanager/
├── main.py              # QApplication, wires all modules together
├── db.py                # SQLite schema, CRUD for clipboard/settings
├── hotkey.py            # Win32 RegisterHotKey + Qt integration
├── utils.py             # Paths, image compression, font helpers
├── clipboard_manager.py # Clipboard polling + dedup + persistence
├── clip_popup.py        # Borderless popup, cursor-following, keyboard nav
├── screenshot_engine.py # Region select overlay, scrolling capture + stitching
├── annotation_window.py # Fullscreen overlay, drawing tools (rect/arrow/text/mosaic)
├── tray_manager.py      # QSystemTrayIcon, right-click menu, hotkey wiring
└── settings_window.py   # QTabWidget: General / Hotkeys / Clipboard tabs
```

---

### Task 1: Project Setup

**Files:**
- Create: `clipmanager/requirements.txt`

- [ ] **Step 1: Create requirements.txt**

```text
PyQt6>=6.5.0
Pillow>=10.0.0
opencv-python>=4.8.0
pywin32>=306
```

- [ ] **Step 2: Install dependencies**

Run: `pip install -r clipmanager/requirements.txt`

- [ ] **Step 3: Commit**

```bash
git add clipmanager/requirements.txt
git commit -m "chore: add project dependencies"
```

---

### Task 2: Database Layer (db.py)

**Files:**
- Create: `clipmanager/db.py`

- [ ] **Step 1: Write db.py with schema and CRUD**

```python
import sqlite3
import os
import threading
from contextlib import contextmanager

DB_PATH = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "clipmanager", "clipmanager.db")

_local = threading.local()

def get_db_path():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return DB_PATH

def get_connection():
    if not hasattr(_local, "conn") or _local.conn is None:
        _local.conn = sqlite3.connect(get_db_path())
        _local.conn.execute("PRAGMA journal_mode=WAL")
        _local.conn.row_factory = sqlite3.Row
    return _local.conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clipboard_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL CHECK(type IN ('text','image')),
            content TEXT NOT NULL,
            size_bytes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_history_created
        ON clipboard_history(created_at DESC)
    """)
    conn.commit()

def add_clipboard_entry(entry_type, content, size_bytes=0):
    conn = get_connection()
    conn.execute(
        "INSERT INTO clipboard_history (type, content, size_bytes) VALUES (?, ?, ?)",
        (entry_type, content, size_bytes)
    )
    conn.commit()
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

def get_clipboard_history(limit=200, offset=0, search=None):
    conn = get_connection()
    if search:
        rows = conn.execute(
            "SELECT * FROM clipboard_history WHERE type='text' AND content LIKE ? "
            "ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (f"%{search}%", limit, offset)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM clipboard_history ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()
    return [dict(r) for r in rows]

def delete_clipboard_entry(entry_id):
    conn = get_connection()
    conn.execute("DELETE FROM clipboard_history WHERE id=?", (entry_id,))
    conn.commit()

def get_last_clipboard_entry():
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM clipboard_history ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    return dict(row) if row else None

def cleanup_old_entries(max_count=200, max_age_days=30):
    conn = get_connection()
    conn.execute(
        "DELETE FROM clipboard_history WHERE id NOT IN "
        "(SELECT id FROM clipboard_history ORDER BY created_at DESC LIMIT ?)",
        (max_count,)
    )
    conn.execute(
        "DELETE FROM clipboard_history WHERE created_at < datetime('now', ?)",
        (f'-{max_age_days} days',)
    )
    conn.commit()

def get_setting(key, default=None):
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default

def set_setting(key, value):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        (key, value)
    )
    conn.commit()

def get_all_settings():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM settings").fetchall()
    return {r["key"]: r["value"] for r in rows}

# Default settings
DEFAULTS = {
    "save_path": os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots"),
    "image_format": "PNG",
    "auto_start": "0",
    "play_sound": "1",
    "max_history": "200",
    "max_age_days": "30",
    "max_image_cache_mb": "50",
    "exclude_apps": "KeePass|1Password",
    "hotkeys": '{"area_screenshot":"Ctrl+Shift+A","long_screenshot":"Ctrl+Shift+L","clipboard_history":"Ctrl+Shift+V","quick_screen":"Print Scr","color_picker":"Ctrl+Shift+C"}',
    "scroll_max_attempts": "30",
}

def init_settings():
    for key, value in DEFAULTS.items():
        if get_setting(key) is None:
            set_setting(key, value)
```

- [ ] **Step 2: Commit**

```bash
git add clipmanager/db.py
git commit -m "feat: add database layer with schema and settings defaults"
```

---

### Task 3: Utilities (utils.py)

**Files:**
- Create: `clipmanager/utils.py`

- [ ] **Step 1: Write utils.py**

```python
import os
import json
from pathlib import Path
from PIL import Image, ImageFilter
from PyQt6.QtGui import QFont, QFontDatabase

def get_app_dir():
    path = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "clipmanager")
    os.makedirs(path, exist_ok=True)
    return path

def get_images_dir():
    path = os.path.join(get_app_dir(), "images")
    os.makedirs(path, exist_ok=True)
    return path

def get_default_save_path():
    path = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
    os.makedirs(path, exist_ok=True)
    return path

def compress_image(image_path, max_dimension=1200, quality=80, fmt="JPEG"):
    img = Image.open(image_path)
    img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > max_dimension:
        ratio = max_dimension / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    out_path = image_path.rsplit(".", 1)[0] + ".jpg"
    img.save(out_path, format=fmt, quality=quality)
    return out_path

def apply_mosaic(img, rect):
    x, y, w, h = rect
    if w <= 0 or h <= 0:
        return img
    region = img.crop((x, y, x+w, y+h))
    small = region.resize((max(1, w // 15), max(1, h // 15)), Image.NEAREST)
    mosaic = small.resize((w, h), Image.NEAREST)
    img.paste(mosaic, (x, y))
    return img

def load_hotkey_config(raw_json):
    try:
        return json.loads(raw_json)
    except (json.JSONDecodeError, TypeError):
        return {
            "area_screenshot": "Ctrl+Shift+A",
            "long_screenshot": "Ctrl+Shift+L",
            "clipboard_history": "Ctrl+Shift+V",
            "quick_screen": "Print Scr",
        }

def dump_hotkey_config(config):
    return json.dumps(config, ensure_ascii=False)

def get_yahei_font(size=12):
    font = QFont("Microsoft YaHei", size)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    return font

def format_bytes(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def relative_time(dt_str):
    from datetime import datetime
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    diff = (now - dt).total_seconds()
    if diff < 60:
        return "刚刚"
    elif diff < 3600:
        return f"{int(diff // 60)} 分钟前"
    elif diff < 86400:
        return f"{int(diff // 3600)} 小时前"
    elif diff < 2592000:
        return f"{int(diff // 86400)} 天前"
    else:
        return dt.strftime("%Y-%m-%d")
```

- [ ] **Step 2: Commit**

```bash
git add clipmanager/utils.py
git commit -m "feat: add utility functions for paths, images, fonts"
```

---

### Task 4: Global Hotkey Manager (hotkey.py)

**Files:**
- Create: `clipmanager/hotkey.py`

- [ ] **Step 1: Write hotkey.py**

```python
import ctypes
import ctypes.wintypes
from PyQt6.QtCore import QAbstractNativeEventFilter, QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

MOD_MAP = {
    "Ctrl": 0x0002,
    "Shift": 0x0004,
    "Alt": 0x0001,
    "Win": 0x0008,
}

VK_MAP = {
    "A": 0x41, "B": 0x42, "C": 0x43, "D": 0x44, "E": 0x45,
    "F": 0x46, "G": 0x47, "H": 0x48, "I": 0x49, "J": 0x4A,
    "K": 0x4B, "L": 0x4C, "M": 0x4D, "N": 0x4E, "O": 0x4F,
    "P": 0x50, "Q": 0x51, "R": 0x52, "S": 0x53, "T": 0x54,
    "U": 0x55, "V": 0x56, "W": 0x57, "X": 0x58, "Y": 0x59,
    "Z": 0x5A,
    "0": 0x30, "1": 0x31, "2": 0x32, "3": 0x33, "4": 0x34,
    "5": 0x35, "6": 0x36, "7": 0x37, "8": 0x38, "9": 0x39,
    "F1": 0x70, "F2": 0x71, "F3": 0x72, "F4": 0x73,
    "F5": 0x74, "F6": 0x75, "F7": 0x76, "F8": 0x77,
    "F9": 0x78, "F10": 0x79, "F11": 0x7A, "F12": 0x7B,
    "Print Scr": 0x2C,
}

WM_HOTKEY = 0x0312

class HotkeyManager(QObject):
    hotkey_triggered = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._ids = {}
        self._next_id = 1
        self._filter = _HotkeyFilter(self)
        self._registered = {}

    def install(self, app):
        app.installNativeEventFilter(self._filter)

    def register(self, name, hotkey_str):
        mod, vk = self._parse(hotkey_str)
        if mod is None or vk is None:
            return False
        hid = self._next_id
        self._next_id += 1
        ok = ctypes.windll.user32.RegisterHotKey(None, hid, mod, vk)
        if ok:
            self._ids[name] = hid
            self._registered[hid] = name
            return True
        return False

    def unregister(self, name):
        hid = self._ids.pop(name, None)
        if hid is not None:
            ctypes.windll.user32.UnregisterHotKey(None, hid)
            self._registered.pop(hid, None)

    def unregister_all(self):
        for hid in list(self._registered.keys()):
            ctypes.windll.user32.UnregisterHotKey(None, hid)
        self._ids.clear()
        self._registered.clear()

    def _parse(self, s):
        parts = [p.strip() for p in s.split("+")]
        mod = 0
        vk = None
        for p in parts:
            if p in MOD_MAP:
                mod |= MOD_MAP[p]
            elif p.upper() in VK_MAP:
                vk = VK_MAP[p.upper()]
            elif len(p) == 1 and p.isalpha():
                vk = VK_MAP.get(p.upper())
        return mod | 0x4000, vk

    def handle_native_event(self, msg):
        if msg.message == WM_HOTKEY:
            hid = msg.wParam
            name = self._registered.get(hid)
            if name:
                self.hotkey_triggered.emit(name)
            return True, 0
        return False, 0

class _HotkeyFilter(QAbstractNativeEventFilter):
    def __init__(self, manager):
        super().__init__()
        self._mgr = manager

    def nativeEventFilter(self, event_type, message):
        return self._mgr.handle_native_event(message)
```

- [ ] **Step 2: Commit**

```bash
git add clipmanager/hotkey.py
git commit -m "feat: add global hotkey manager with Win32 RegisterHotKey"
```

---

### Task 5: Clipboard Manager (clipboard_manager.py)

**Files:**
- Create: `clipmanager/clipboard_manager.py`

- [ ] **Step 1: Write clipboard_manager.py**

```python
import time
import os
import uuid
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtGui import QClipboard
import db
from utils import get_images_dir, compress_image

class ClipboardManager(QObject):
    content_added = pyqtSignal(dict)

    def __init__(self, app):
        super().__init__()
        self._clipboard = app.clipboard()
        self._last_content = ""
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._poll)
        self._timer.setInterval(500)
        db.init_db()
        db.init_settings()
        self._load_exclusions()

    def start(self):
        self._timer.start()

    def stop(self):
        self._timer.stop()

    def _load_exclusions(self):
        import re
        raw = db.get_setting("exclude_apps", "KeePass|1Password")
        try:
            self._exclude_pattern = re.compile(raw, re.IGNORECASE)
        except re.error:
            self._exclude_pattern = re.compile("")

    def _poll(self):
        try:
            mime = self._clipboard.mimeData()
            if mime.hasImage():
                img = mime.imageData()
                if img is None:
                    return
                tmp_name = str(uuid.uuid4())[:8] + ".png"
                tmp_path = os.path.join(get_images_dir(), "tmp_" + tmp_name)
                img.save(tmp_path, "PNG")
                final_path = compress_image(tmp_path)
                os.remove(tmp_path)
                content_key = final_path
                if content_key == self._last_content:
                    return
                self._last_content = content_key
                size = os.path.getsize(final_path)
                eid = db.add_clipboard_entry("image", final_path, size)
                self.content_added.emit({"id": eid, "type": "image", "content": final_path})
                self._trim()
            elif mime.hasText():
                text = mime.text()
                if not text or text == self._last_content:
                    return
                self._last_content = text
                eid = db.add_clipboard_entry("text", text, len(text.encode("utf-8")))
                self.content_added.emit({"id": eid, "type": "text", "content": text})
                self._trim()
        except Exception:
            pass

    def _trim(self):
        try:
            max_count = int(db.get_setting("max_history", "200"))
            max_days = int(db.get_setting("max_age_days", "30"))
        except ValueError:
            max_count = 200
            max_days = 30
        db.cleanup_old_entries(max_count, max_days)

    def get_history(self, limit=200, offset=0, search=None):
        return db.get_clipboard_history(limit, offset, search)

    def delete_entry(self, entry_id):
        db.delete_clipboard_entry(entry_id)

    def paste_to_active(self, entry):
        from PyQt6.QtWidgets import QApplication
        cl = QApplication.clipboard()
        if entry["type"] == "text":
            cl.setText(entry["content"])
        elif entry["type"] == "image":
            from PyQt6.QtGui import QImage
            img = QImage(entry["content"])
            cl.setImage(img)
```

- [ ] **Step 2: Commit**

```bash
git add clipmanager/clipboard_manager.py
git commit -m "feat: add clipboard manager with polling, dedup, and persistence"
```

---

### Task 6: Clipboard Popup (clip_popup.py)

**Files:**
- Create: `clipmanager/clip_popup.py`

- [ ] **Step 1: Write clip_popup.py**

```python
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QApplication, QFrame, QLineEdit
)
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal, QEvent
from PyQt6.QtGui import QKeyEvent, QPixmap, QFont
from utils import get_yahei_font, relative_time

class ClipPopup(QWidget):
    entry_selected = pyqtSignal(dict)

    def __init__(self, clipboard_manager):
        super().__init__()
        self._mgr = clipboard_manager
        self._entries = []
        self._selected_idx = -1
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Popup |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setStyleSheet("background: white; border: 1px solid #e0e0e0; border-radius: 8px;")
        self._build_ui()
        self.setFixedWidth(340)
        self.setMaximumHeight(420)

    def _build_ui(self):
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # header
        hdr = QHBoxLayout()
        hdr.setContentsMargins(12, 10, 12, 10)
        title = QLabel("剪贴板")
        title.setFont(get_yahei_font(13))
        title.setStyleSheet("font-weight: 600; color: #333; border: none;")
        hdr.addWidget(title)
        hdr.addStretch()
        self._count_label = QLabel("0 条")
        self._count_label.setFont(get_yahei_font(11))
        self._count_label.setStyleSheet("color: #aaa; background: #f5f5f5; padding: 2px 8px; border-radius: 3px; border: none;")
        hdr.addWidget(self._count_label)
        hdr_w = QWidget()
        hdr_w.setLayout(hdr)
        hdr_w.setStyleSheet("background: white; border: none;")
        self._layout.addWidget(hdr_w)

        # search
        self._search = QLineEdit()
        self._search.setPlaceholderText("搜索历史...")
        self._search.setFont(get_yahei_font(12))
        self._search.setStyleSheet(
            "QLineEdit { border: none; border-top: 1px solid #f0f0f0; "
            "padding: 8px 12px; background: #fafafa; }"
        )
        self._search.textChanged.connect(self._on_search)
        self._layout.addWidget(self._search)

        # list area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("QScrollArea { border: none; }")
        self._list_widget = QWidget()
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(0)
        self._list_layout.addStretch()
        self._scroll.setWidget(self._list_widget)
        self._layout.addWidget(self._scroll)

        # footer
        ft = QHBoxLayout()
        ft.setContentsMargins(12, 6, 12, 6)
        f_texts = ["↑↓ 选择", "Enter 粘贴", "Del 删除", "Esc 关闭"]
        for t in f_texts:
            lbl = QLabel(t)
            lbl.setFont(get_yahei_font(10))
            lbl.setStyleSheet("color: #bbb; border: none;")
            ft.addWidget(lbl)
            if t != f_texts[-1]:
                ft.addStretch()
        ft_w = QWidget()
        ft_w.setLayout(ft)
        ft_w.setStyleSheet("background: #fafafa; border: none; border-top: 1px solid #f0f0f0;")
        self._layout.addWidget(ft_w)

    def show_at_cursor(self):
        self._load_entries()
        pos = self._get_popup_pos()
        self.move(pos)
        self.show()
        self._search.setFocus()
        self._search.clear()

    def _get_popup_pos(self):
        widget = QApplication.focusWidget()
        if widget:
            cursor_pos = widget.mapToGlobal(
                widget.cursorRect().bottomLeft()
            )
            screen = QApplication.screenAt(cursor_pos)
        else:
            cursor_pos = self.cursor().pos()
            screen = QApplication.screenAt(cursor_pos)
        if screen is None:
            screen = QApplication.primaryScreen()
        geo = screen.availableGeometry()
        x = cursor_pos.x()
        y = cursor_pos.y() + 10
        if x + self.width() > geo.right():
            x = geo.right() - self.width()
        if y + self.height() > geo.bottom():
            y = cursor_pos.y() - self.height() - 10
        return QPoint(x, y)

    def _load_entries(self, search=None):
        self._entries = self._mgr.get_history(limit=50, search=search)
        self._selected_idx = 0 if self._entries else -1
        self._rebuild_list()

    def _rebuild_list(self):
        for i in reversed(range(self._list_layout.count())):
            item = self._list_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        for idx, entry in enumerate(self._entries):
            row = self._make_row(entry, idx)
            self._list_layout.insertWidget(self._list_layout.count() - 1, row)
        self._count_label.setText(f"{len(self._entries)} 条")

    def _make_row(self, entry, idx):
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame { background: white; border: none; }" if idx != self._selected_idx else
            "QFrame { background: #f0f4ff; border: none; }"
        )
        frame.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        icon = QLabel("📝" if entry["type"] == "text" else "🖼️")
        icon.setFont(get_yahei_font(14))
        icon.setFixedWidth(24)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("border: none;")
        layout.addWidget(icon)

        content_w = QWidget()
        content_l = QVBoxLayout(content_w)
        content_l.setContentsMargins(0, 0, 0, 0)
        content_l.setSpacing(4)

        if entry["type"] == "image":
            preview = QLabel()
            pix = QPixmap(entry["content"])
            if not pix.isNull():
                pix = pix.scaledToWidth(80, Qt.TransformationMode.SmoothTransformation)
            preview.setPixmap(pix)
            preview.setStyleSheet("border: none;")
            content_l.addWidget(preview)
        else:
            text = entry["content"].replace("\n", " ")[:120]
            lbl = QLabel(text)
            lbl.setFont(get_yahei_font(12))
            lbl.setStyleSheet("color: #1a1a1a; border: none; line-height: 1.5;")
            lbl.setWordWrap(True)
            content_l.addWidget(lbl)

        time_lbl = QLabel(relative_time(entry.get("created_at", "")))
        time_lbl.setFont(get_yahei_font(10))
        time_lbl.setStyleSheet("color: #999; border: none;")
        content_l.addWidget(time_lbl)

        layout.addWidget(content_w, 1)

        frame.mousePressEvent = lambda e, eid=entry["id"]: self._on_click(eid)
        return frame

    def _on_click(self, entry_id):
        for e in self._entries:
            if e["id"] == entry_id:
                self._mgr.paste_to_active(e)
                self.entry_selected.emit(e)
                break
        self.hide()

    def _on_search(self, text):
        self._load_entries(search=text if text else None)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key.Key_Escape:
            self.hide()
        elif key == Qt.Key.Key_Down:
            if self._selected_idx < len(self._entries) - 1:
                self._selected_idx += 1
                self._rebuild_list()
        elif key == Qt.Key.Key_Up:
            if self._selected_idx > 0:
                self._selected_idx -= 1
                self._rebuild_list()
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self._selected_idx >= 0 and self._selected_idx < len(self._entries):
                e = self._entries[self._selected_idx]
                self._mgr.paste_to_active(e)
                self.entry_selected.emit(e)
                self.hide()
        elif key == Qt.Key.Key_Delete:
            if self._selected_idx >= 0 and self._selected_idx < len(self._entries):
                eid = self._entries[self._selected_idx]["id"]
                self._mgr.delete_entry(eid)
                del self._entries[self._selected_idx]
                self._selected_idx = min(self._selected_idx, len(self._entries) - 1)
                self._rebuild_list()
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event):
        self.hide()
```

- [ ] **Step 2: Commit**

```bash
git add clipmanager/clip_popup.py
git commit -m "feat: add clipboard history popup with keyboard navigation"
```

---

### Task 7: Screenshot Engine (screenshot_engine.py)

**Files:**
- Create: `clipmanager/screenshot_engine.py`

- [ ] **Step 1: Write screenshot_engine.py - RegionSelector overlay**

```python
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from utils import get_yahei_font

class RegionSelector(QWidget):
    region_selected = pyqtSignal(QRect)

    def __init__(self):
        super().__init__()
        self._start = QPoint()
        self._end = QPoint()
        self._selecting = False
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def start(self):
        screen = QApplication.primaryScreen()
        self._screenshot = screen.grabWindow(0)
        self._screen_geo = screen.geometry()
        self.setGeometry(self._screen_geo)
        self._selecting = False
        self.showFullScreen()
        self.grabKeyboard()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._start = event.pos()
            self._end = self._start
            self._selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        if self._selecting:
            self._end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._selecting:
            self._selecting = False
            rect = QRect(self._start, self._end).normalized()
            if rect.width() > 5 and rect.height() > 5:
                self.releaseKeyboard()
                self.hide()
                self.region_selected.emit(rect)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.releaseKeyboard()
            self.hide()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._screenshot)
        mask = QColor(0, 0, 0, 120)
        painter.fillRect(self.rect(), mask)
        if self._selecting:
            rect = QRect(self._start, self._end).normalized()
            painter.drawPixmap(rect, self._screenshot, rect)
            pen = QPen(QColor("#2196F3"), 2)
            painter.setPen(pen)
            painter.drawRect(rect)
            # size label
            size_text = f"{rect.width()} × {rect.height()}"
            painter.setFont(get_yahei_font(13))
            painter.setPen(QColor("white"))
            label_rect = painter.boundingRect(
                rect.right() + 10, rect.bottom() + 5, 200, 24, 0, size_text
            )
            painter.fillRect(
                label_rect.adjusted(-4, -2, 4, 2),
                QColor(0, 0, 0, 180)
            )
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, size_text)
```

- [ ] **Step 2: Add ScrollingCaptureEngine to screenshot_engine.py**

Append to the same file:

```python
import cv2
import numpy as np
import win32gui
import win32ui
import win32con
from PIL import Image
from PyQt6.QtCore import QThread, pyqtSignal

class ScrollingCaptureEngine(QThread):
    progress_update = pyqtSignal(str, int)
    capture_finished = pyqtSignal(Image.Image)
    capture_error = pyqtSignal(str)

    def __init__(self, hwnd, max_scrolls=30):
        super().__init__()
        self._hwnd = hwnd
        self._max_scrolls = max_scrolls
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            frames = []
            prev_frame = None
            for i in range(self._max_scrolls):
                if self._cancelled:
                    return
                self.progress_update.emit("capturing", i + 1)
                img = self._capture_window()
                if img is None:
                    break
                frames.append(img)
                if prev_frame is not None and self._is_bottom_reached(prev_frame, img):
                    break
                self._scroll_window()
                prev_frame = img
                self.msleep(300)
            self.progress_update.emit("stitching", 0)
            result = self._stitch_frames(frames)
            self.capture_finished.emit(result)
        except Exception as e:
            self.capture_error.emit(str(e))

    def _capture_window(self):
        try:
            left, top, right, bottom = win32gui.GetWindowRect(self._hwnd)
            w, h = right - left, bottom - top
            if w <= 0 or h <= 0:
                return None
            hdc = win32gui.GetWindowDC(self._hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hdc)
            save_dc = mfc_dc.CreateCompatibleDC()
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfc_dc, w, h)
            save_dc.SelectObject(bitmap)
            save_dc.BitBlt((0, 0), (w, h), mfc_dc, (0, 0), win32con.SRCCOPY)
            bmp_info = bitmap.GetInfo()
            bmp_str = bitmap.GetBitmapBits(True)
            img = Image.frombuffer(
                "RGB", (bmp_info["bmWidth"], bmp_info["bmHeight"]),
                bmp_str, "raw", "BGRX", 0, 1
            )
            win32gui.DeleteObject(bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(self._hwnd, hdc)
            return img
        except Exception:
            return None

    def _scroll_window(self):
        try:
            import win32gui as wg
            wg.SendMessage(self._hwnd, 0x0115, 3, 0)
        except Exception:
            pass

    def _is_bottom_reached(self, prev, curr):
        prev_arr = np.array(prev.convert("L"))
        curr_arr = np.array(curr.convert("L"))
        diff = np.mean(np.abs(prev_arr.astype(int) - curr_arr.astype(int)))
        return diff < 2.0

    def _stitch_frames(self, frames):
        if not frames:
            return None
        if len(frames) == 1:
            return frames[0]
        result = frames[0]
        for i in range(1, len(frames)):
            result = self._stitch_pair(result, frames[i])
        return result

    def _stitch_pair(self, img1, img2):
        arr1 = np.array(img1.convert("L"))
        arr2 = np.array(img2.convert("L"))
        orb = cv2.ORB_create(nfeatures=500)
        kp1, des1 = orb.detectAndCompute(arr1, None)
        kp2, des2 = orb.detectAndCompute(arr2, None)
        if des1 is None or des2 is None or len(des1) < 2 or len(des2) < 2:
            return _simple_concat(img1, img2)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        if len(matches) < 4:
            return _simple_concat(img1, img2)
        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        matrix, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
        if matrix is None:
            return _simple_concat(img1, img2)
        h1, w1 = arr1.shape
        h2, w2 = arr2.shape
        corners2 = np.float32([[0, 0], [0, h2], [w2, h2], [w2, 0]]).reshape(-1, 1, 2)
        warped_corners = cv2.perspectiveTransform(corners2, matrix)
        corners1 = np.float32([[0, 0], [0, h1], [w1, h1], [w1, 0]]).reshape(-1, 1, 2)
        all_c = np.concatenate((corners1, warped_corners), axis=0)
        x_min, y_min = np.int32(all_c.min(axis=0).ravel())
        x_max, y_max = np.int32(all_c.max(axis=0).ravel())
        translation = np.array([
            [1, 0, -x_min],
            [0, 1, -y_min],
            [0, 0, 1]
        ])
        result = cv2.warpPerspective(np.array(img2), translation.dot(matrix), (x_max - x_min, y_max - y_min))
        result[-y_min:h1 - y_min, -x_min:w1 - x_min] = np.array(img1)
        return Image.fromarray(result)

def _simple_concat(img1, img2):
    w1, h1 = img1.size
    w2, h2 = img2.size
    result = Image.new("RGB", (max(w1, w2), h1 + h2))
    result.paste(img1, (0, 0))
    result.paste(img2, (0, h1))
    return result
```

- [ ] **Step 3: Commit**

```bash
git add clipmanager/screenshot_engine.py
git commit -m "feat: add region selection overlay and scrolling capture engine"
```

---

### Task 8: Annotation Window (annotation_window.py)

**Files:**
- Create: `clipmanager/annotation_window.py`

- [ ] **Step 1: Write annotation_window.py**

```python
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QRect, QPoint, QRectF, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QFont, QPixmap, QImage, QPolygonF,
    QPainterPath
)
from utils import get_yahei_font, apply_mosaic
from PIL import Image
import math

class AnnotationWindow(QWidget):
    editing_finished = pyqtSignal(Image.Image)
    cancelled = pyqtSignal()

    TOOL_RECT = "rect"
    TOOL_ARROW = "arrow"
    TOOL_TEXT = "text"
    TOOL_MOSAIC = "mosaic"

    def __init__(self):
        super().__init__()
        self._annotations = []
        self._current_tool = self.TOOL_RECT
        self._drawing = False
        self._start = QPoint()
        self._end = QPoint()
        self._text_input = ""
        self._text_pos = None
        self._pending_text = False
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def load_image(self, pil_image):
        self._original = pil_image
        from io import BytesIO
        buf = BytesIO()
        pil_image.save(buf, format="PNG")
        self._pixmap = QPixmap()
        self._pixmap.loadFromData(buf.getvalue())
        self._annotations.clear()
        self._text_input = ""
        self._pending_text = False

    def show_for_rect(self, screen_rect):
        self.setGeometry(screen_rect)
        self._roi = QRect(0, 0, screen_rect.width(), screen_rect.height())
        self.showFullScreen()
        self.grabKeyboard()
        self.setFocus()

    def set_tool(self, tool):
        self._current_tool = tool

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 160))
        if self._pixmap and not self._pixmap.isNull():
            painter.drawPixmap(self._roi, self._pixmap)

        for ann in self._annotations:
            self._draw_annotation(painter, ann)

        if self._drawing:
            self._draw_preview(painter)

        if self._pending_text and self._text_pos:
            painter.setFont(get_yahei_font(16))
            painter.setPen(QColor("#FF0000"))
            cursor_x = self._text_pos.x() + (len(self._text_input) * 10 if self._text_input else 0)
            painter.drawLine(cursor_x, self._text_pos.y() - 10, cursor_x, self._text_pos.y() + 10)
            if self._text_input:
                painter.drawText(self._text_pos, self._text_input)

    def _draw_annotation(self, painter, ann):
        t = ann["type"]
        if t == self.TOOL_RECT:
            pen = QPen(QColor("#FF0000"), 2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(QRectF(
                ann["x"], ann["y"], ann["w"], ann["h"]
            ))
        elif t == self.TOOL_ARROW:
            pen = QPen(QColor("#FF0000"), 2)
            painter.setPen(pen)
            painter.drawLine(ann["x1"], ann["y1"], ann["x2"], ann["y2"])
            angle = math.atan2(ann["y2"] - ann["y1"], ann["x2"] - ann["x1"])
            al = 12
            arrow_p1 = QPoint(
                int(ann["x2"] - al * math.cos(angle - 0.5)),
                int(ann["y2"] - al * math.sin(angle - 0.5))
            )
            arrow_p2 = QPoint(
                int(ann["x2"] - al * math.cos(angle + 0.5)),
                int(ann["y2"] - al * math.sin(angle + 0.5))
            )
            path = QPainterPath()
            path.moveTo(ann["x2"], ann["y2"])
            path.lineTo(arrow_p1)
            path.lineTo(arrow_p2)
            path.closeSubpath()
            painter.fillPath(path, QColor("#FF0000"))
        elif t == self.TOOL_TEXT:
            painter.setFont(get_yahei_font(ann.get("size", 16)))
            painter.setPen(QColor("#FF0000"))
            painter.drawText(QPoint(ann["x"], ann["y"]), ann["text"])
        elif t == self.TOOL_MOSAIC:
            painter.fillRect(
                QRectF(ann["x"], ann["y"], ann["w"], ann["h"]),
                QColor(180, 180, 180, 200)
            )

    def _draw_preview(self, painter):
        rect = QRect(self._start, self._end).normalized()
        pen = QPen(QColor("#FF0000"), 2, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._current_tool == self.TOOL_TEXT:
                self._text_pos = event.pos()
                self._text_input = ""
                self._pending_text = True
                self.update()
            else:
                self._start = event.pos()
                self._end = self._start
                self._drawing = True

    def mouseMoveEvent(self, event):
        if self._drawing:
            self._end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._drawing:
            self._drawing = False
            rect = QRect(self._start, self._end).normalized()
            if self._current_tool == self.TOOL_RECT:
                self._annotations.append({
                    "type": self.TOOL_RECT,
                    "x": rect.x(), "y": rect.y(),
                    "w": rect.width(), "h": rect.height(),
                })
            elif self._current_tool == self.TOOL_ARROW:
                self._annotations.append({
                    "type": self.TOOL_ARROW,
                    "x1": self._start.x(), "y1": self._start.y(),
                    "x2": self._end.x(), "y2": self._end.y(),
                })
            elif self._current_tool == self.TOOL_MOSAIC:
                self._annotations.append({
                    "type": self.TOOL_MOSAIC,
                    "x": rect.x(), "y": rect.y(),
                    "w": rect.width(), "h": rect.height(),
                })
            self.update()

    def keyPressEvent(self, event):
        key = event.key()
        mods = event.modifiers()

        if key == Qt.Key.Key_Escape:
            if self._pending_text:
                self._pending_text = False
                self._text_input = ""
                self._text_pos = None
                self.update()
            else:
                self.releaseKeyboard()
                self.hide()
                self.cancelled.emit()

        elif self._pending_text:
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self._annotations.append({
                    "type": self.TOOL_TEXT,
                    "x": self._text_pos.x(), "y": self._text_pos.y(),
                    "text": self._text_input, "size": 16,
                })
                self._pending_text = False
                self._text_input = ""
                self._text_pos = None
                self.update()
            elif key == Qt.Key.Key_Backspace:
                self._text_input = self._text_input[:-1]
                self.update()
            elif len(event.text()) > 0:
                self._text_input += event.text()
                self.update()
            return

        # tool switching
        tool_keys = {
            Qt.Key.Key_R: self.TOOL_RECT,
            Qt.Key.Key_A: self.TOOL_ARROW,
            Qt.Key.Key_T: self.TOOL_TEXT,
            Qt.Key.Key_M: self.TOOL_MOSAIC,
        }
        if key in tool_keys:
            self._current_tool = tool_keys[key]
            return

        if key == Qt.Key.Key_Z and mods == Qt.KeyboardModifier.ControlModifier:
            if self._annotations:
                self._annotations.pop()
                self.update()
            return

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self._annotations:
                result = self._render_annotations()
                self.releaseKeyboard()
                self.hide()
                self.editing_finished.emit(result)
            return

    def _render_annotations(self):
        if not self._original:
            return None
        img = self._original.copy()
        for ann in self._annotations:
            if ann["type"] == self.TOOL_MOSAIC:
                apply_mosaic(img, (ann["x"], ann["y"], ann["w"], ann["h"]))
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        for ann in self._annotations:
            if ann["type"] == self.TOOL_RECT:
                draw.rectangle(
                    [ann["x"], ann["y"], ann["x"] + ann["w"], ann["y"] + ann["h"]],
                    outline="#FF0000", width=2
                )
            elif ann["type"] == self.TOOL_ARROW:
                draw.line(
                    [ann["x1"], ann["y1"], ann["x2"], ann["y2"]],
                    fill="#FF0000", width=2
                )
            elif ann["type"] == self.TOOL_TEXT:
                try:
                    font = ImageFont.truetype("msyh.ttc", ann.get("size", 16))
                except Exception:
                    font = ImageFont.load_default()
                draw.text((ann["x"], ann["y"]), ann["text"], fill="#FF0000", font=font)
        return img
```

- [ ] **Step 2: Commit**

```bash
git add clipmanager/annotation_window.py
git commit -m "feat: add annotation overlay with rect, arrow, text, mosaic tools"
```

---

### Task 9: Settings Window (settings_window.py)

**Files:**
- Create: `clipmanager/settings_window.py`

- [ ] **Step 1: Write settings_window.py**

```python
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QLineEdit, QPushButton, QFileDialog, QComboBox, QCheckBox,
    QSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence
from PyQt6.QtCore import pyqtSignal
from utils import get_yahei_font
import db
import json
import os

class SettingsWindow(QWidget):
    hotkeys_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._hotkey_buttons = {}
        self.setWindowTitle("ClipManager 设置")
        self.setFixedSize(460, 420)
        self.setFont(get_yahei_font(11))
        self._build_ui()
        self._load_values()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        tabs.addTab(self._general_tab(), "常规")
        tabs.addTab(self._hotkey_tab(), "热键")
        tabs.addTab(self._clipboard_tab(), "剪贴板")
        layout.addWidget(tabs)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._save)
        save_btn.setStyleSheet(
            "QPushButton { background: #2196F3; color: white; padding: 6px 24px; "
            "border-radius: 4px; border: none; }"
        )
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _general_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setSpacing(14)

        l.addWidget(self._row("截图保存路径", [
            (self._save_path_input := QLineEdit(), 1),
            (self._browse_btn := QPushButton("浏览"), 0)
        ]))
        self._browse_btn.clicked.connect(self._browse_path)

        l.addWidget(self._row("默认图片格式", [
            (self._format_combo := QComboBox(), 1)
        ]))
        self._format_combo.addItems(["PNG", "JPEG", "WebP"])

        self._auto_start_cb = QCheckBox("开机自动启动")
        l.addWidget(self._auto_start_cb)

        self._sound_cb = QCheckBox("截图后播放声音")
        l.addWidget(self._sound_cb)

        l.addStretch()
        return w

    def _hotkey_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setSpacing(10)

        actions = [
            ("area_screenshot", "区域截图"),
            ("long_screenshot", "截长图"),
            ("clipboard_history", "剪贴板历史"),
            ("quick_screen", "快速截屏到剪贴板"),
        ]
        for key, label in actions:
            l.addLayout(self._hotkey_row(key, label))
        l.addStretch()
        return w

    def _hotkey_row(self, key, label_text):
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setFixedWidth(140)
        row.addWidget(lbl)
        btn = QPushButton()
        btn.setFixedWidth(160)
        btn.setStyleSheet(
            "QPushButton { background: #f0f0f0; padding: 4px 12px; "
            "border-radius: 3px; border: 1px solid #ddd; }"
        )
        btn.clicked.connect(lambda checked, k=key, b=btn: self._record_hotkey(k, b))
        self._hotkey_buttons[key] = btn
        row.addWidget(btn)
        row.addStretch()
        return row

    def _clipboard_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setSpacing(14)

        l.addWidget(self._row("最大历史记录数", [
            (self._max_hist := QSpinBox(), 1)
        ]))
        self._max_hist.setRange(10, 10000)

        l.addWidget(self._row("自动清除超过 (天)", [
            (self._max_age := QSpinBox(), 1)
        ]))
        self._max_age.setRange(1, 365)

        l.addWidget(self._row("图片最大缓存 (MB)", [
            (self._max_cache := QSpinBox(), 1)
        ]))
        self._max_cache.setRange(10, 5000)

        l.addWidget(self._row("排除应用 (正则)", [
            (self._exclude_input := QLineEdit(), 1)
        ]))
        l.addStretch()
        return w

    def _row(self, label, widgets):
        h = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setFixedWidth(130)
        h.addWidget(lbl)
        for wgt, stretch in widgets:
            h.addWidget(wgt, stretch)
        return h

    def _browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择保存路径")
        if path:
            self._save_path_input.setText(path)

    def _record_hotkey(self, key, button):
        from PyQt6.QtCore import QEventLoop
        button.setText("按下新快捷键...")
        button.setStyleSheet(
            "QPushButton { background: #FFEB3B; padding: 4px 12px; "
            "border-radius: 3px; border: 1px solid #FBC02D; }"
        )
        self._recording = True
        self._record_key = key
        self._record_button = button

    def keyPressEvent(self, event):
        if not getattr(self, "_recording", False):
            super().keyPressEvent(event)
            return
        mods = event.modifiers()
        key = event.key()
        parts = []
        if mods & Qt.KeyboardModifier.ControlModifier:
            parts.append("Ctrl")
        if mods & Qt.KeyboardModifier.ShiftModifier:
            parts.append("Shift")
        if mods & Qt.KeyboardModifier.AltModifier:
            parts.append("Alt")
        if mods & Qt.KeyboardModifier.MetaModifier:
            parts.append("Win")
        name = QKeySequence(key).toString()
        if name and name not in ("Ctrl", "Shift", "Alt", "Meta"):
            parts.append(name)
        if parts:
            hotkey_str = "+".join(parts)
            self._record_button.setText(hotkey_str)
            self._record_button.setStyleSheet(
                "QPushButton { background: #f0f0f0; padding: 4px 12px; "
                "border-radius: 3px; border: 1px solid #ddd; }"
            )
            self._recording = False

    def _load_values(self):
        self._save_path_input.setText(
            db.get_setting("save_path", os.path.expanduser("~/Pictures/Screenshots"))
        )
        fmt = db.get_setting("image_format", "PNG")
        idx = self._format_combo.findText(fmt)
        if idx >= 0:
            self._format_combo.setCurrentIndex(idx)
        self._auto_start_cb.setChecked(db.get_setting("auto_start", "0") == "1")
        self._sound_cb.setChecked(db.get_setting("play_sound", "1") == "1")
        self._max_hist.setValue(int(db.get_setting("max_history", "200")))
        self._max_age.setValue(int(db.get_setting("max_age_days", "30")))
        self._max_cache.setValue(int(db.get_setting("max_image_cache_mb", "50")))
        self._exclude_input.setText(db.get_setting("exclude_apps", "KeePass|1Password"))

        hotkeys = json.loads(db.get_setting("hotkeys", "{}"))
        for key, btn in self._hotkey_buttons.items():
            btn.setText(hotkeys.get(key, ""))

    def _save(self):
        db.set_setting("save_path", self._save_path_input.text())
        db.set_setting("image_format", self._format_combo.currentText())
        db.set_setting("auto_start", "1" if self._auto_start_cb.isChecked() else "0")
        db.set_setting("play_sound", "1" if self._sound_cb.isChecked() else "0")
        db.set_setting("max_history", str(self._max_hist.value()))
        db.set_setting("max_age_days", str(self._max_age.value()))
        db.set_setting("max_image_cache_mb", str(self._max_cache.value()))
        db.set_setting("exclude_apps", self._exclude_input.text())

        hotkeys = {}
        for key, btn in self._hotkey_buttons.items():
            hotkeys[key] = btn.text()
        db.set_setting("hotkeys", json.dumps(hotkeys, ensure_ascii=False))

        self.hotkeys_changed.emit()
        QMessageBox.information(self, "保存成功", "设置已保存，部分更改可能需要重启后生效。")
        self.hide()

```

- [ ] **Step 2: Commit**

```bash
git add clipmanager/settings_window.py
git commit -m "feat: add settings window with general, hotkey, clipboard tabs"
```

---

### Task 10: Tray Manager (tray_manager.py)

**Files:**
- Create: `clipmanager/tray_manager.py`

- [ ] **Step 1: Write tray_manager.py**

```python
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import QObject, pyqtSignal
from hotkey import HotkeyManager
import db
import json
from utils import get_yahei_font, load_hotkey_config

class TrayManager(QObject):
    area_screenshot = pyqtSignal()
    long_screenshot = pyqtSignal()
    clipboard_history = pyqtSignal()
    quick_screen = pyqtSignal()
    open_settings = pyqtSignal()
    quit_app = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._hotkey_mgr = HotkeyManager()
        self._tray = QSystemTrayIcon()
        self._build_icon()
        self._build_menu()
        self._tray.show()
        self._register_hotkeys()

    def install(self, app):
        self._hotkey_mgr.install(app)
        self._hotkey_mgr.hotkey_triggered.connect(self._on_hotkey)

    def _build_icon(self):
        pix = QPixmap(32, 32)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setBrush(QColor("#2196F3"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(2, 2, 28, 28, 6, 6)
        painter.setPen(QColor("white"))
        font = QFont("Microsoft YaHei", 13, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, "C")
        painter.end()
        self._tray.setIcon(QIcon(pix))
        self._tray.setToolTip("ClipManager")

    def _build_menu(self):
        menu = QMenu()
        menu.setFont(get_yahei_font(11))

        actions = [
            ("📋 剪贴板历史", self._emit_clipboard),
            ("✂️ 区域截图", self._emit_area),
            ("📜 截长图", self._emit_long),
            ("⚙️ 设置", self._emit_settings),
            ("🚪 退出", self._emit_quit),
        ]
        for text, slot in actions:
            if text.startswith("🚪"):
                menu.addSeparator()
            action = QAction(text)
            action.triggered.connect(slot)
            menu.addAction(action)

        self._tray.setContextMenu(menu)

    def _emit_clipboard(self):
        self.clipboard_history.emit()

    def _emit_area(self):
        self.area_screenshot.emit()

    def _emit_long(self):
        self.long_screenshot.emit()

    def _emit_settings(self):
        self.open_settings.emit()

    def _emit_quit(self):
        self._hotkey_mgr.unregister_all()
        self._tray.hide()
        self.quit_app.emit()

    def _register_hotkeys(self):
        hotkeys = load_hotkey_config(db.get_setting("hotkeys"))
        action_map = {
            "area_screenshot": "area_screenshot",
            "long_screenshot": "long_screenshot",
            "clipboard_history": "clipboard_history",
            "quick_screen": "quick_screen",
        }
        for action_id, hotkey_id in action_map.items():
            hk = hotkeys.get(action_id)
            if hk:
                self._hotkey_mgr.register(hotkey_id, hk)

    def _on_hotkey(self, hotkey_id):
        mapping = {
            "area_screenshot": self.area_screenshot,
            "long_screenshot": self.long_screenshot,
            "clipboard_history": self.clipboard_history,
            "quick_screen": self.quick_screen,
        }
        if hotkey_id in mapping:
            mapping[hotkey_id].emit()

    def reload_hotkeys(self):
        self._hotkey_mgr.unregister_all()
        self._register_hotkeys()
```

- [ ] **Step 2: Commit**

```bash
git add clipmanager/tray_manager.py
git commit -m "feat: add system tray manager with global hotkey integration"
```

---

### Task 11: Main Entry Point (main.py)

**Files:**
- Create: `clipmanager/main.py`

- [ ] **Step 1: Write main.py**

```python
import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QClipboard
from tray_manager import TrayManager
from clipboard_manager import ClipboardManager
from clip_popup import ClipPopup
from screenshot_engine import RegionSelector, ScrollingCaptureEngine
from annotation_window import AnnotationWindow
from settings_window import SettingsWindow
from utils import get_default_save_path
import db
from datetime import datetime

class ClipManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setApplicationName("ClipManager")

        db.init_db()
        db.init_settings()

        self.tray = TrayManager()
        self.tray.install(self.app)

        self.clipboard = ClipboardManager(self.app)
        self.clipboard.start()

        self.popup = ClipPopup(self.clipboard)
        self.settings_win = SettingsWindow()

        self._connect_signals()

    def _connect_signals(self):
        self.tray.area_screenshot.connect(self._area_screenshot)
        self.tray.long_screenshot.connect(self._long_screenshot)
        self.tray.clipboard_history.connect(self._show_popup)
        self.tray.quick_screen.connect(self._quick_screenshot)
        self.tray.open_settings.connect(self._show_settings)
        self.tray.quit_app.connect(self.app.quit)
        self.settings_win.hotkeys_changed.connect(self.tray.reload_hotkeys)

    def _area_screenshot(self):
        selector = RegionSelector()
        selector.region_selected.connect(self._on_region_selected)
        selector.start()

    def _on_region_selected(self, rect):
        screen = self.app.primaryScreen()
        pixmap = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())
        from PIL import Image
        from io import BytesIO
        buf = BytesIO()
        pixmap.save(buf, "PNG")
        img = Image.open(buf)
        self._open_annotator(img)

    def _quick_screenshot(self):
        screen = self.app.primaryScreen()
        pixmap = screen.grabWindow(0)
        from io import BytesIO
        buf = BytesIO()
        pixmap.save(buf, "PNG")
        from PyQt6.QtGui import QImage
        self.app.clipboard().setPixmap(pixmap)

    def _long_screenshot(self):
        import win32gui
        hwnd = win32gui.GetForegroundWindow()
        self._capture_engine = ScrollingCaptureEngine(hwnd, max_scrolls=30)
        self._capture_engine.capture_finished.connect(self._on_long_finished)
        self._capture_engine.capture_error.connect(
            lambda e: QMessageBox.warning(None, "截长图失败", f"截图出错：{e}")
        )
        self._capture_engine.start()

    def _on_long_finished(self, pil_image):
        if pil_image is None:
            return
        self._open_annotator(pil_image)

    def _open_annotator(self, pil_image):
        self._annotator = AnnotationWindow()
        self._annotator.load_image(pil_image)
        self._annotator.editing_finished.connect(self._on_edit_finished)
        self._annotator.cancelled.connect(lambda: None)
        screen_geo = self.app.primaryScreen().geometry()
        self._annotator.show_for_rect(screen_geo)

    def _on_edit_finished(self, pil_image):
        from io import BytesIO
        buf = BytesIO()
        pil_image.save(buf, "PNG")
        qimg = self._pil_to_qimage(pil_image)
        self.app.clipboard().setImage(qimg)

        save_path = db.get_setting("save_path", get_default_save_path())
        os.makedirs(save_path, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"screenshot_{ts}.png"
        fpath = os.path.join(save_path, fname)
        pil_image.save(fpath, "PNG")

    def _pil_to_qimage(self, pil_img):
        from io import BytesIO
        from PyQt6.QtGui import QImage
        buf = BytesIO()
        pil_img.save(buf, "PNG")
        qimg = QImage()
        qimg.loadFromData(buf.getvalue())
        return qimg

    def _show_popup(self):
        self.popup.show_at_cursor()

    def _show_settings(self):
        self.settings_win.show()
        self.settings_win.raise_()
        self.settings_win.activateWindow()

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app = ClipManager()
    app.run()
```

- [ ] **Step 2: Commit**

```bash
git add clipmanager/main.py
git commit -m "feat: add main entry point wiring all modules together"
```

---

### Task 12: Integration Testing

**Files:**
- Create: `clipmanager/test_clipmanager.py`

- [ ] **Step 1: Write basic integration tests**

```python
import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

def test_db_init():
    import db
    db.init_db()
    db.init_settings()
    assert db.get_setting("max_history") == "200"
    assert db.get_setting("nonexistent", "fallback") == "fallback"

def test_db_clipboard_crud():
    import db
    db.init_db()
    eid = db.add_clipboard_entry("text", "test content", 12)
    assert eid > 0
    rows = db.get_clipboard_history(limit=10)
    assert len(rows) > 0
    assert rows[0]["content"] == "test content"
    db.delete_clipboard_entry(eid)
    rows2 = db.get_clipboard_history(limit=10)
    assert all(r["id"] != eid for r in rows2)

def test_settings_crud():
    import db
    db.set_setting("test_key", "hello")
    assert db.get_setting("test_key") == "hello"

def test_utils_relative_time():
    from utils import relative_time
    from datetime import datetime, timedelta
    ts = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    assert "分钟前" in relative_time(ts)

    ts = (datetime.now() - timedelta(seconds=30)).strftime("%Y-%m-%d %H:%M:%S")
    assert "刚刚" == relative_time(ts)

def test_utils_format_bytes():
    from utils import format_bytes
    assert format_bytes(500) == "500 B"
    assert "KB" in format_bytes(2048)
    assert "MB" in format_bytes(3 * 1024 * 1024)

def test_hotkey_parse():
    from hotkey import HotkeyManager
    hm = HotkeyManager()
    mod, vk = hm._parse("Ctrl+Shift+A")
    assert vk == 0x41
    assert mod & 0x0002
    assert mod & 0x0004

def test_load_hotkey_config():
    from utils import load_hotkey_config
    config = load_hotkey_config('{"area_screenshot":"Ctrl+Shift+A"}')
    assert config["area_screenshot"] == "Ctrl+Shift+A"
    config2 = load_hotkey_config(None)
    assert "area_screenshot" in config2
```

- [ ] **Step 2: Run tests**

Run: `python -m pytest clipmanager/test_clipmanager.py -v`
Expected: All PASS

- [ ] **Step 3: Commit**

```bash
git add clipmanager/test_clipmanager.py
git commit -m "test: add integration tests for db, utils, hotkey"
```

---

### Task 13: Run and Smoke Test

**Files:**
- No new files. Run the app interactively.

- [ ] **Step 1: Verify app launches**

Run: `python clipmanager/main.py`
Expected: App starts, tray icon appears in system tray

- [ ] **Step 2: Smoke check features**

Manual checks:
1. Right-click tray icon → menu appears with all options
2. Press Ctrl+Shift+V → clipboard popup appears
3. Press Ctrl+Shift+A → area selector overlay appears
4. Esc cancels the selector
5. Settings window opens and saves

---

## Implementation Notes

1. **Order matters**: Tasks 1-4 (setup, db, utils, hotkey) must complete before Tasks 5-10.
2. **Tasks 5-10 can run in parallel** since they are independent modules sharing only `db` and `utils`.
3. **Task 11 (main.py) must be last** since it imports all modules.
4. **Task 12 (tests)** can run after Task 4, then re-run after Task 11.
5. All image files are stored in `%APPDATA%/clipmanager/images/`; SQLite DB in `%APPDATA%/clipmanager/clipmanager.db`.
6. OCR for text in images is out of scope for v1.
7. AnnotationWindow `_render_annotations` draws mosaic on PIL image directly, then renders vector annotations (rect, arrow, text) with PIL ImageDraw. This order ensures mosaic obscures content underneath.
