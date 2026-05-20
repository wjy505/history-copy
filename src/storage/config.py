"""配置文件管理 — 读写 %APPDATA%/ClipboardHistory/config.json"""
import json
import os
import sys
from typing import Any

DEFAULT_CONFIG = {
    "storage_duration_days": 3,
    "hotkey": "ctrl+shift+a",
    "max_image_width": 1200,
    "panel_width": 400,
    "panel_height": 600,
    "start_with_windows": False,
}


def _get_app_dir() -> str:
    """获取应用数据目录，不存在则创建"""
    appdata = os.getenv("APPDATA")
    if not appdata:
        appdata = os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
    path = os.path.join(appdata, "ClipboardHistory")
    os.makedirs(path, exist_ok=True)
    return path


def _get_images_dir() -> str:
    path = os.path.join(_get_app_dir(), "images")
    os.makedirs(path, exist_ok=True)
    return path


def get_db_path() -> str:
    return os.path.join(_get_app_dir(), "clipboard.db")


def get_images_dir() -> str:
    return _get_images_dir()


class ConfigManager:
    def __init__(self):
        self._config_path = os.path.join(_get_app_dir(), "config.json")
        self._data: dict[str, Any] = {}
        self._load()

    def _load(self):
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._data = {}
        # 合并默认值
        for key, value in DEFAULT_CONFIG.items():
            if key not in self._data:
                self._data[key] = value
        self._save()

    def _save(self):
        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        self._data[key] = value
        self._save()

    @property
    def storage_duration_days(self) -> int:
        return int(self.get("storage_duration_days", 3))

    @property
    def hotkey(self) -> str:
        return str(self.get("hotkey", "alt+v"))

    @property
    def max_image_width(self) -> int:
        return int(self.get("max_image_width", 1200))

    @property
    def panel_width(self) -> int:
        return int(self.get("panel_width", 400))

    @property
    def panel_height(self) -> int:
        return int(self.get("panel_height", 600))

    @property
    def start_with_windows(self) -> bool:
        return bool(self.get("start_with_windows", False))
