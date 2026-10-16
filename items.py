"""
items.py —— 可拾取道具
医疗包（回血）、弹药包（补满弹匣）。
"""
import pygame
from constants import ITEM_RADIUS, COLOR_HEALTH, COLOR_AMMO


class Item:
    def __init__(self, x, y, kind):
        self.x = float(x)
        self.y = float(y)
        self.radius = ITEM_RADIUS
        self.kind = kind  # "health" or "ammo"
        self.collected = False

    def draw(self, surf):
        if self.collected:
            return
        if self.kind == "health":
            pygame.draw.circle(surf, COLOR_HEALTH, (int(self.x), int(self.y)), self.radius)
            # 白色十字
            pygame.draw.rect(surf, (255, 255, 255),
                             (self.x - 2, self.y - 7, 4, 14))
            pygame.draw.rect(surf, (255, 255, 255),
                             (self.x - 7, self.y - 2, 14, 4))
        else:  # ammo
            pygame.draw.rect(surf, COLOR_AMMO,
                             (self.x - self.radius, self.y - self.radius,
                              self.radius * 2, self.radius * 2))
            pygame.draw.rect(surf, (80, 60, 20),
                             (self.x - self.radius, self.y - self.radius,
                              self.radius * 2, self.radius * 2), 2)
