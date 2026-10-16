"""
analyze_assets.py —— 素材布局分析工具（一次性）
用纯像素统计推断 P1/P2 图片结构：
- 估计背景色（取四角众数）
- 找出前景连通区域的行/列投影，推断精灵网格
输出文本报告，不依赖人工看图。
"""
import sys
from collections import Counter
from PIL import Image


def load(path):
    return Image.open(path).convert("RGB")


def estimate_bg(im):
    w, h = im.size
    pts = []
    for x in (2, w - 3):
        for y in (2, h - 3):
            pts.append(im.getpixel((x, y)))
    # 也采样边缘一圈
    for x in range(0, w, max(1, w // 50)):
        pts.append(im.getpixel((x, 0)))
        pts.append(im.getpixel((x, h - 1)))
    for y in range(0, h, max(1, h // 50)):
        pts.append(im.getpixel((0, y)))
        pts.append(im.getpixel((w - 1, y)))
    return Counter(pts).most_common(5)


def projections(im, bg, tol=40):
    """返回每行/每列的前景像素计数（与背景色差异 > tol 视为前景）。"""
    w, h = im.size
    px = im.load()
    row_fg = [0] * h
    col_fg = [0] * w
    for y in range(h):
        for x in range(w):
            p = px[x, y]
            d = abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2])
            if d > tol:
                row_fg[y] += 1
                col_fg[x] += 1
    return row_fg, col_fg


def runs(counts, min_val):
    """把计数数组中 >= min_val 的连续区间列出来。"""
    out = []
    start = None
    for i, c in enumerate(counts):
        if c >= min_val and start is None:
            start = i
        elif c < min_val and start is not None:
            out.append((start, i - 1))
            start = None
    if start is not None:
        out.append((start, len(counts) - 1))
    return out


def report(path, name):
    im = load(path)
    w, h = im.size
    print(f"=== {name}: {w}x{h} ===")
    bg_candidates = estimate_bg(im)
    print("背景候选色(色值,次数):", bg_candidates)
    bg = bg_candidates[0][0]
    row_fg, col_fg = projections(im, bg)
    max_row = max(row_fg)
    max_col = max(col_fg)
    print(f"最大行前景数={max_row} 最大列前景数={max_col}")

    # 用 5% 最大值为阈值找大行带
    row_bands = runs(row_fg, max(6, max_row * 0.05))
    print(f"行带({len(row_bands)}):", [(a, b, b - a + 1) for a, b in row_bands])

    # 对每个行带，再看列带
    for (a, b) in row_bands:
        band_h = b - a + 1
        if band_h < 20:
            continue
        sub = im.crop((0, a, w, b + 1))
        _, col_fg2 = projections(sub, bg)
        mc = max(col_fg2) if col_fg2 else 0
        col_bands = runs(col_fg2, max(4, mc * 0.05))
        print(f"  行带 y={a}-{b} (h={band_h}) 列带({len(col_bands)}):",
              [(s, e, e - s + 1) for s, e in col_bands])
    print()


if __name__ == "__main__":
    p1 = r"C:\Users\洪佳karen\AppData\Local\Temp\p1_hero.png"
    p2 = r"c:\Users\洪佳karen\.trae-cn\attachments\ada8d718-8ed4-4968-8854-ee13154edaa0_a3f3113f-e7d3-49c3-95e7-337614c3c568_image.png"
    report(p1, "P1 男主")
    report(p2, "P2 Fuji&Karen")
