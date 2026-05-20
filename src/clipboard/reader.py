"""剪贴板读取 — 使用 Qt QClipboard 读取文字，pywin32 读取图片"""
import hashlib
import win32clipboard
import win32con
from PySide6.QtWidgets import QApplication
from PIL import Image
import io


def read_text() -> str | None:
    """通过 QClipboard 读取文字"""
    app = QApplication.instance()
    if app is None:
        return None
    clipboard = app.clipboard()
    text = clipboard.text()
    if text:
        return text
    return None


def read_image_raw() -> bytes | None:
    """通过 pywin32 读取剪贴板中的 DIB 图片数据"""
    try:
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_DIB):
            data = win32clipboard.GetClipboardData(win32con.CF_DIB)
            win32clipboard.CloseClipboard()
            return data
        win32clipboard.CloseClipboard()
        return None
    except Exception:
        try:
            win32clipboard.CloseClipboard()
        except Exception:
            pass
        return None


def read_image() -> Image.Image | None:
    """通过 pywin32 读取剪贴板中的图片"""
    try:
        data = read_image_raw()
        if data:
            return _dib_to_pil(data)
    except Exception:
        pass
    return None


def _dib_to_pil(data: bytes) -> Image.Image | None:
    """DIB 数据转 PIL Image"""
    import struct
    try:
        bmp_header = (
            b"BM"
            + struct.pack("<I", len(data) + 14)
            + b"\x00\x00\x00\x00"
            + struct.pack("<I", 14 + 40)
        )
        return Image.open(io.BytesIO(bmp_header + data))
    except Exception:
        try:
            return Image.open(io.BytesIO(data))
        except Exception:
            return None


def compute_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_image_hash(image: Image.Image) -> str:
    raw = image.tobytes()
    return hashlib.sha256(raw).hexdigest()


def read_clipboard() -> dict | None:
    """读取剪贴板。优先图片，其次文字。"""
    # 先检查图片
    image = read_image()
    if image is not None:
        return {
            "type": "image",
            "image": image,
            "hash": compute_image_hash(image),
        }

    # 再检查文字（用 QClipboard，最可靠）
    text = read_text()
    if text:
        return {
            "type": "text",
            "text": text,
            "hash": compute_text_hash(text),
        }

    return None
