"""
ascii_preview.py —— 把图片转成 ASCII 亮度图，用于在无法直接看图时推断布局。
"""
import sys
from PIL import Image

CHARS = " .:-=+*#%@"


def ascii_art(path, cols=96):
    im = Image.open(path).convert("L")
    w, h = im.size
    rows = int(cols * h / w * 0.5)  # 字符高宽比约 2:1
    im = im.resize((cols, rows))
    px = im.load()
    lines = []
    for y in range(rows):
        line = "".join(CHARS[min(9, px[x, y] * 10 // 256)] for x in range(cols))
        lines.append(line)
    return "\n".join(lines)


if __name__ == "__main__":
    path = sys.argv[1]
    cols = int(sys.argv[2]) if len(sys.argv) > 2 else 96
    print(ascii_art(path, cols))
