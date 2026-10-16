"""
contact_sheet.py —— 把切出的透明帧拼到洋红背景上，人工校验抠图质量。
"""
import os
import sys
from PIL import Image

SPR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "sprites")

CELL_W, CELL_H = 90, 110
chars = ["hero", "fuji", "karen"]
actions = ["idle", "walk", "run", "shoot"]

sheet = Image.new("RGB", (CELL_W * 12, CELL_H * len(chars)), (255, 0, 255))
for r, char in enumerate(chars):
    col = 0
    for action in actions:
        for f in range(3):
            name = f"{char}_{action}_{f}.png"
            path = os.path.join(SPR, name)
            if not os.path.exists(path):
                continue
            im = Image.open(path).convert("RGBA")
            scale = min((CELL_W - 10) / im.width, (CELL_H - 10) / im.height)
            im = im.resize((int(im.width * scale), int(im.height * scale)), Image.NEAREST)
            x = col * CELL_W + (CELL_W - im.width) // 2
            y = r * CELL_H + (CELL_H - im.height) - 4
            sheet.paste(im, (x, y), im)
            col += 1

out = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\洪佳karen\AppData\Local\Temp\contact.png"
sheet.save(out)
print("saved", out, sheet.size)
