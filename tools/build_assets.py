"""
build_assets.py —— 素材切分管线（一次性运行）
从原始素材 P1(男主立绘) / P2(动作素材总表) 中：
  1. 按网格裁剪角色动作帧（hero/fuji/karen × idle/walk/run/shoot × 3帧）
  2. 用"边缘洪水填充"抠掉深蓝背景，生成透明 PNG
  3. 裁剪三张菜单立绘（hero 用 P1，fuji/karen 用 P2 顶部头像）
输出到 assets/ 目录，供游戏运行时直接加载。
"""
import os
import shutil
from collections import deque
from PIL import Image

# ===== 路径 =====
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P1_SRC = r"c:\Users\洪佳karen\.trae-cn\attachments\9d49d5ae-a196-4493-8cd5-8bccb5fe0c9f_70187b20-8fec-4b95-8362-7677172f5c8f_image.png"
P2_SRC = r"c:\Users\洪佳karen\.trae-cn\attachments\ada8d718-8ed4-4968-8854-ee13154edaa0_a3f3113f-e7d3-49c3-95e7-337614c3c568_image.png"
ASSETS = os.path.join(BASE, "assets")

# ===== P2 精灵表网格（原图 537x458 像素坐标） =====
BG_COLOR = (5, 12, 20)          # 深蓝背景
KEY_TOL = 34                    # 背景色判定欧氏距离阈值
ROW_BANDS = [(261, 328), (328, 390), (390, 444)]   # 3 个帧行 (y0, y1)

# 列单元: (x0, x1)，动作顺序见 actions
COL_CELLS = {
    "hero":  [(6, 52), (52, 99), (99, 146)],                     # 男主: walk/run/shoot（无 idle 列）
    "fuji":  [(161, 207), (207, 253), (253, 299), (299, 345)],   # 待机/行走/跑步/射击
    "karen": [(360, 401), (401, 442), (442, 483), (483, 524)],
}
COL_ACTIONS = {
    "hero":  ["walk", "run", "shoot"],
    "fuji":  ["idle", "walk", "run", "shoot"],
    "karen": ["idle", "walk", "run", "shoot"],
}

# ===== P2 顶部立绘区（菜单卡片用） =====
PORTRAIT_CROPS_P2 = {
    "fuji": (0, 0, 105, 204),
    "karen": (260, 0, 370, 204),
}
PORTRAIT_W = 200   # 输出立绘宽度


def flood_key(im, bg, tol):
    """边缘洪水填充抠背景：只把与边缘相连、颜色接近 bg 的像素置透明。"""
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()
    tol2 = tol * tol

    def is_bg(p):
        dr = p[0] - bg[0]
        dg = p[1] - bg[1]
        db = p[2] - bg[2]
        return dr * dr + dg * dg + db * db < tol2

    visited = [[False] * w for _ in range(h)]
    q = deque()
    # 从四边所有背景色像素出发
    for x in range(w):
        for y in (0, h - 1):
            if is_bg(px[x, y]) and not visited[y][x]:
                visited[y][x] = True
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if is_bg(px[x, y]) and not visited[y][x]:
                visited[y][x] = True
                q.append((x, y))
    while q:
        x, y = q.popleft()
        p = px[x, y]
        px[x, y] = (p[0], p[1], p[2], 0)
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx]:
                visited[ny][nx] = True
                if is_bg(px[nx, ny]):
                    q.append((nx, ny))
                else:
                    # 非背景像素：保持不透明（不误伤深色衣物/头发）
                    pass
    return im


def trim_alpha(im, pad=2):
    """按 alpha 通道裁剪透明边距，保留 pad 像素余量。"""
    bbox = im.getchannel("A").getbbox()
    if not bbox:
        return im
    x0, y0, x1, y1 = bbox
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(im.width, x1 + pad)
    y1 = min(im.height, y1 + pad)
    return im.crop((x0, y0, x1, y1))


def build_sprites():
    sheet = Image.open(P2_SRC).convert("RGB")
    outdir = os.path.join(ASSETS, "sprites")
    os.makedirs(outdir, exist_ok=True)
    count = 0
    for char, cells in COL_CELLS.items():
        actions = COL_ACTIONS[char]
        for col_idx, (x0, x1) in enumerate(cells):
            action = actions[col_idx]
            for row_idx, (y0, y1) in enumerate(ROW_BANDS):
                cell = sheet.crop((x0, y0, x1, y1))
                keyed = flood_key(cell, BG_COLOR, KEY_TOL)
                frame = trim_alpha(keyed)
                # 过滤无效帧（抠完几乎为空）
                if frame.width < 6 or frame.height < 10:
                    print(f"  [跳过] {char}/{action}_{row_idx}: 内容过少 {frame.size}")
                    continue
                name = f"{char}_{action}_{row_idx}.png"
                frame.save(os.path.join(outdir, name))
                count += 1
        # hero 没有 idle 列：用 walk 帧复制一份作为 idle
        if char == "hero":
            for row_idx in range(len(ROW_BANDS)):
                src = os.path.join(outdir, f"hero_walk_{row_idx}.png")
                dst = os.path.join(outdir, f"hero_idle_{row_idx}.png")
                if os.path.exists(src):
                    shutil.copyfile(src, dst)
    print(f"精灵帧输出完成: {count} 张 -> {outdir}")


def build_portraits():
    outdir = os.path.join(ASSETS, "portraits")
    os.makedirs(outdir, exist_ok=True)
    # fuji / karen 来自 P2 顶部
    p2 = Image.open(P2_SRC).convert("RGB")
    for name, box in PORTRAIT_CROPS_P2.items():
        crop = p2.crop(box)
        h = int(crop.height * PORTRAIT_W / crop.width)
        crop = crop.resize((PORTRAIT_W, h), Image.LANCZOS)
        crop.save(os.path.join(outdir, f"{name}.png"))
    # hero 来自 P1（立绘原图，等比缩放到 200px 宽）
    p1 = Image.open(P1_SRC).convert("RGB")
    h = int(p1.height * PORTRAIT_W / p1.width)
    p1.resize((PORTRAIT_W, h), Image.LANCZOS).save(os.path.join(outdir, "hero.png"))
    print(f"立绘输出完成 -> {outdir}")


def copy_sources():
    """原始素材归档到 assets/source/，随仓库分发。"""
    outdir = os.path.join(ASSETS, "source")
    os.makedirs(outdir, exist_ok=True)
    shutil.copyfile(P1_SRC, os.path.join(outdir, "p1_hero.png"))
    shutil.copyfile(P2_SRC, os.path.join(outdir, "p2_fuji_karen.png"))
    print(f"原始素材归档 -> {outdir}")


if __name__ == "__main__":
    build_sprites()
    build_portraits()
    copy_sources()
    print("素材管线完成。")
