"""
cluster_preview.py —— 颜色聚类 ASCII 图 + 分区主色统计
用于推断图片结构（不需要直接看图）。
"""
import sys
from PIL import Image


def main(path, cols=100):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    print(f"尺寸: {w}x{h}")

    # 量化到 10 色
    q = im.quantize(colors=10, method=Image.MEDIANCUT)
    pal = q.getpalette()[:30]
    colors = [(pal[i * 3], pal[i * 3 + 1], pal[i * 3 + 2]) for i in range(10)]
    counts = sorted(q.getcolors(), reverse=True)
    print("主色(索引: RGB, 像素数):")
    for cnt, idx in counts:
        print(f"  {idx}: {colors[idx]}  {cnt} ({cnt * 100 // (w * h)}%)")

    # 按索引排序映射字符：数量最多的背景用空格
    order = [idx for _, idx in counts]
    symbols = " .:-=+*#%@"
    sym_of = {idx: symbols[i] for i, idx in enumerate(order)}

    rows = int(cols * h / w * 0.5)
    small = q.resize((cols, rows), Image.NEAREST)
    px = small.load()
    print("\n聚类分布图(空格=最大簇=背景):")
    for y in range(rows):
        print("".join(sym_of[px[x, y]] for x in range(cols)))

    # 四象限主色
    print("\n象限主色:")
    for name, box in [("左上", (0, 0, w // 2, h // 2)), ("右上", (w // 2, 0, w, h // 2)),
                      ("左下", (0, h // 2, w // 2, h)), ("右下", (w // 2, h // 2, w, h))]:
        sub = im.crop(box).quantize(colors=3, method=Image.MEDIANCUT)
        sp = sub.getpalette()[:9]
        sc = sorted(sub.getcolors(), reverse=True)
        desc = [f"{(sp[i*3], sp[i*3+1], sp[i*3+2])}({c*100//(box[2]-box[0])*(box[3]-box[1])}%)" for c, i in sc]
        # 修正百分比
        total = (box[2] - box[0]) * (box[3] - box[1])
        desc = [f"{(sp[i*3], sp[i*3+1], sp[i*3+2])}({c * 100 // total}%)" for c, i in sc]
        print(f"  {name}: {desc}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 100)
