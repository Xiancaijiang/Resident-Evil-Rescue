"""
level.py —— 关卡数据
用墙体矩形构建一个含多个房间的建筑，定义出生点、出口、
丧尸与道具的初始位置。
"""
import pygame
from constants import WALL_THICKNESS


def build_level():
    """返回关卡数据字典。"""
    walls = []
    T = WALL_THICKNESS

    # —— 外围边框 ——
    walls.append(pygame.Rect(0, 0, 960, T))          # 上
    walls.append(pygame.Rect(0, 640 - T, 960, T))    # 下
    walls.append(pygame.Rect(0, 0, T, 640))          # 左
    walls.append(pygame.Rect(960 - T, 0, T, 640))    # 右

    # —— 中部横墙，分隔上下层，中间留门 ——
    walls.append(pygame.Rect(T, 312, 400, T))        # 左段
    walls.append(pygame.Rect(544, 312, 960 - 544 - T, T))  # 右段（门在 416~544）

    # —— 上层右侧小房间（男主关押点），竖墙带缺口 ——
    walls.append(pygame.Rect(700, T, T, 124))        # 上半段
    walls.append(pygame.Rect(700, 200, T, 112))      # 下半段（缺口在 y 140~200）

    # —— 出生点 / 出口 / 目标 ——
    player_spawn = (80, 560)
    hostage_pos = (820, 160)
    exit_rect = pygame.Rect(840, 520, 88, 88)

    # —— 丧尸出生点 ——
    zombie_spawns = [
        (300, 200), (600, 200), (820, 260),
        (200, 500), (500, 540), (760, 520),
    ]

    # —— 道具 ——
    item_spawns = [
        (150, 150, "health"),
        (500, 100, "ammo"),
        (300, 560, "ammo"),
        (820, 420, "health"),
    ]

    return {
        "walls": walls,
        "player_spawn": player_spawn,
        "hostage_pos": hostage_pos,
        "exit_rect": exit_rect,
        "zombie_spawns": zombie_spawns,
        "item_spawns": item_spawns,
    }
