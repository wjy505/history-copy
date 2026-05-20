"""图片文件管理 — 保存、缩略图、删除"""
import os
from PIL import Image
from .config import get_images_dir


THUMB_WIDTH = 200


def save_image(pil_image: Image.Image, item_id: int, max_width: int = 1200) -> tuple[str, str]:
    """
    保存全尺寸图片和缩略图。
    返回 (image_path, thumbnail_path) 的绝对路径。
    """
    images_dir = get_images_dir()

    # 如果图片过宽，等比缩小
    if pil_image.width > max_width:
        ratio = max_width / pil_image.width
        new_height = int(pil_image.height * ratio)
        pil_image = pil_image.resize((max_width, new_height), Image.LANCZOS)

    # 保存全尺寸图
    img_filename = f"{item_id}.png"
    img_path = os.path.join(images_dir, img_filename)
    # 确保 RGB 模式（RGBA 转 RGB 用白色背景）
    if pil_image.mode in ("RGBA", "P", "LA"):
        bg = Image.new("RGB", pil_image.size, (255, 255, 255))
        if pil_image.mode == "P":
            pil_image = pil_image.convert("RGBA")
        bg.paste(pil_image, mask=pil_image.split()[-1] if pil_image.mode == "RGBA" else None)
        pil_image = bg
    elif pil_image.mode != "RGB":
        pil_image = pil_image.convert("RGB")
    pil_image.save(img_path, "PNG")

    # 保存缩略图
    thumb_filename = f"{item_id}_thumb.png"
    thumb_path = os.path.join(images_dir, thumb_filename)
    thumb = pil_image.copy()
    if thumb.width > THUMB_WIDTH:
        ratio = THUMB_WIDTH / thumb.width
        thumb_height = int(thumb.height * ratio)
        thumb = thumb.resize((THUMB_WIDTH, thumb_height), Image.LANCZOS)
    thumb.save(thumb_path, "PNG")

    return img_path, thumb_path


def delete_images(item_id: int):
    """删除指定 item 的图片和缩略图"""
    images_dir = get_images_dir()
    for filename in [f"{item_id}.png", f"{item_id}_thumb.png"]:
        filepath = os.path.join(images_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)


def delete_all_images():
    """清空图片目录"""
    images_dir = get_images_dir()
    for filename in os.listdir(images_dir):
        filepath = os.path.join(images_dir, filename)
        if os.path.isfile(filepath):
            os.remove(filepath)


def image_exists(item_id: int) -> bool:
    return os.path.exists(os.path.join(get_images_dir(), f"{item_id}.png"))
