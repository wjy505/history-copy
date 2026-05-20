"""剪贴板写入 — 将文字或图片写入 Windows 剪贴板"""
import io
import win32clipboard
import win32con
from PIL import Image


def write_text(text: str):
    """将文字写入剪贴板"""
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()


def write_image(image: Image.Image):
    """将 PIL Image 以 DIB 格式写入剪贴板"""
    # 转换为 DIB 格式（去掉 BMP 文件头）
    output = io.BytesIO()
    image.save(output, format="BMP")
    bmp_data = output.getvalue()
    # BMP 文件头 14 字节，DIB 从偏移 14 开始
    dib_data = bmp_data[14:]

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32con.CF_DIB, dib_data)
    win32clipboard.CloseClipboard()
