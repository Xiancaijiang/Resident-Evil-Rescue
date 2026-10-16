"""
sprites.py —— 精灵素材运行时加载与动画
从 assets/sprites/ 加载透明帧 PNG，统一缩放到固定渲染高度，
按动作（idle/walk/run/shoot）循环播放；素材缺失时回退为 None（由调用方画矢量图形）。
"""
import os
import pygame
from constants import ASSET_DIR, SPRITE_HEIGHT

ACTIONS = ("idle", "walk", "run", "shoot")
FRAME_COUNT = 3

_cache = {}


def _asset_root():
    """assets 目录的绝对路径（基于本文件所在目录，保证任意 cwd 可运行）。"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), ASSET_DIR)


def load_sprite_set(char):
    """加载某角色的全部动作帧，返回 {action: [Surface, ...]}；无任何帧则返回 None。"""
    if char in _cache:
        return _cache[char]

    spr_dir = os.path.join(_asset_root(), "sprites")
    frames = {}
    for action in ACTIONS:
        action_frames = []
        for i in range(FRAME_COUNT):
            path = os.path.join(spr_dir, f"{char}_{action}_{i}.png")
            if not os.path.exists(path):
                continue
            try:
                img = pygame.image.load(path).convert_alpha()
            except pygame.error:
                continue
            # 等比缩放到统一渲染高度
            w = max(1, int(img.get_width() * SPRITE_HEIGHT / img.get_height()))
            img = pygame.transform.smoothscale(img, (w, SPRITE_HEIGHT))
            action_frames.append(img)
        if action_frames:
            frames[action] = action_frames

    result = frames if frames else None
    _cache[char] = result
    return result


def load_portrait(char):
    """加载菜单/HUD 立绘，失败返回 None。"""
    key = f"portrait_{char}"
    if key in _cache:
        return _cache[key]
    path = os.path.join(_asset_root(), "portraits", f"{char}.png")
    surf = None
    if os.path.exists(path):
        try:
            surf = pygame.image.load(path).convert_alpha()
        except pygame.error:
            surf = None
    _cache[key] = surf
    return surf


def pick_frame(sprite_set, action, frame_idx):
    """取某动作的第 frame_idx 帧；动作缺失时依次回退 walk->idle->任意。"""
    if sprite_set is None:
        return None
    seq = sprite_set.get(action)
    if not seq:
        seq = sprite_set.get("walk") or sprite_set.get("idle")
    if not seq:
        seq = next(iter(sprite_set.values()))
    return seq[frame_idx % len(seq)]


def draw_sprite(surf, sprite_set, action, frame_idx, x, y, facing_left):
    """以 (x, y) 为脚底中心绘制精灵；facing_left 时水平翻转。返回是否绘制成功。"""
    img = pick_frame(sprite_set, action, frame_idx)
    if img is None:
        return False
    if facing_left:
        img = pygame.transform.flip(img, True, False)
    rect = img.get_rect(midbottom=(int(x), int(y)))
    surf.blit(img, rect)
    return True
