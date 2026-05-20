"""粘贴引擎 — 写入剪贴板 → 隐藏面板 → Ctrl+V"""
import time
import ctypes
from ctypes import wintypes

import win32con

from src.clipboard.writer import write_text, write_image

user32 = ctypes.windll.user32


class PasteEngine:
    def __init__(self):
        pass

    def paste_text(self, text: str):
        write_text(text)
        self._send_ctrl_v()

    def paste_image(self, image):
        write_image(image)
        self._send_ctrl_v()

    def _send_ctrl_v(self):
        """使用 SendInput 发送 Ctrl+V"""
        time.sleep(0.05)

        INPUT_KEYBOARD = 1
        KEYEVENTF_KEYUP = 0x0002

        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [
                ("wVk", wintypes.WORD),
                ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
            ]

        class INPUT(ctypes.Structure):
            class _INPUT(ctypes.Union):
                _fields_ = [("ki", KEYBDINPUT)]
            _anonymous_ = ("_input",)
            _fields_ = [
                ("type", wintypes.DWORD),
                ("_input", _INPUT),
            ]

        def press(vk):
            inp = INPUT()
            inp.type = INPUT_KEYBOARD
            inp.ki.wVk = vk
            inp.ki.dwFlags = 0
            user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

        def release(vk):
            inp = INPUT()
            inp.type = INPUT_KEYBOARD
            inp.ki.wVk = vk
            inp.ki.dwFlags = KEYEVENTF_KEYUP
            user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

        time.sleep(0.03)
        press(win32con.VK_CONTROL)
        time.sleep(0.03)
        press(0x56)  # V
        time.sleep(0.03)
        release(0x56)
        time.sleep(0.03)
        release(win32con.VK_CONTROL)
