"""
hostage.py —— 被解救的男主
未被接触时原地呼救；玩家靠近后自动跟随，保持一定距离。
丧尸会攻击他，死亡则任务失败。
"""
import math
import pygame
from constants import (
    HOSTAGE_RADIUS, HOSTAGE_SPEED, HOSTAGE_FOLLOW_DIST,
    COLOR_HOSTAGE, ZOMBIE_ATTACK_INTERVAL_MS,
    ANIM_INTERVAL_MS, IDLE_INTERVAL_MS,
)
from player import circle_rect_collide
import sprites


class Hostage:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.radius = HOSTAGE_RADIUS
        self.speed = HOSTAGE_SPEED
        self.max_hp = 100
        self.hp = 100
        self.rescued = False      # 是否已被玩家接触开始跟随
        self.alive = True
        self.last_attack_ms = 0
        self.sprite_set = sprites.load_sprite_set("hero")
        self.moving = False       # 本帧是否正在跟随移动

    def update(self, player, zombies, walls, now_ms):
        if not self.alive:
            return

        # 被接触后开始跟随
        if not self.rescued:
            dx = player.x - self.x
            dy = player.y - self.y
            if math.hypot(dx, dy) < self.radius + player.radius + 6:
                self.rescued = True
            return

        # 跟随玩家：若距离过远则靠近，过近则停下
        self.moving = False
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist > HOSTAGE_FOLLOW_DIST:
            self.moving = True
            nx = self.x + (dx / dist) * self.speed
            ny = self.y + (dy / dist) * self.speed
            if not any(circle_rect_collide(nx, self.y, self.radius, w) for w in walls):
                self.x = nx
            if not any(circle_rect_collide(self.x, ny, self.radius, w) for w in walls):
                self.y = ny

        # 丧尸攻击男主
        for z in zombies:
            if not z.alive:
                continue
            zd = math.hypot(z.x - self.x, z.y - self.y)
            if zd < z.radius + self.radius + 2:
                if now_ms - self.last_attack_ms >= ZOMBIE_ATTACK_INTERVAL_MS:
                    self.hp -= 6
                    self.last_attack_ms = now_ms
                    if self.hp <= 0:
                        self.alive = False

    def draw(self, surf, font):
        if not self.alive:
            return
        now = pygame.time.get_ticks()
        action = "walk" if self.moving else "idle"
        interval = ANIM_INTERVAL_MS if self.moving else IDLE_INTERVAL_MS
        frame = (now // interval) % 3
        foot_y = self.y + self.radius + 2
        drawn = sprites.draw_sprite(surf, self.sprite_set, action, frame,
                                    self.x, foot_y, facing_left=False)
        if not drawn:
            pygame.draw.circle(surf, COLOR_HOSTAGE, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surf, (120, 100, 30), (int(self.x), int(self.y)), self.radius, 2)
        if not self.rescued:
            t = font.render("HELP!", True, (255, 80, 80))
            surf.blit(t, (self.x - t.get_width() / 2, self.y - self.radius - 42))
        # 血条
        if self.hp < self.max_hp:
            bw = self.radius * 2
            pygame.draw.rect(surf, (60, 20, 20), (self.x - self.radius, self.y - self.radius - 8, bw, 4))
            pygame.draw.rect(surf, COLOR_HOSTAGE,
                             (self.x - self.radius, self.y - self.radius - 8,
                              bw * self.hp / self.max_hp, 4))
