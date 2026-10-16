"""
crop_preview.py —— 裁剪并放大图片区域，便于人工核对布局。
用法: python crop_preview.py <img> <x> <y> <w> <h> <scale> <out>
"""
import sys
from PIL import Image

img, x, y, w, h, scale, out = (sys.argv[1], *map(int, sys.argv[2:6]), float(sys.argv[6]), sys.argv[7])
im = Image.open(img).convert("RGB")
crop = im.crop((x, y, x + w, y + h))
crop = crop.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
crop.save(out)
print("saved", out, crop.size)
