"""
zombie.py —— 丧尸敌人
AI：玩家进入仇恨范围则追击，否则原地缓慢游走；接触玩家造成周期性伤害。
"""
import math
import random
import pygame
from constants import (
    ZOMBIE_RADIUS, ZOMBIE_SPEED, ZOMBIE_HP,
    ZOMBIE_AGGRO_RANGE, ZOMBIE_ATTACK_RANGE,
    ZOMBIE_ATTACK_DMG, ZOMBIE_ATTACK_INTERVAL_MS,
    COLOR_ZOMBIE, COLOR_ZOMBIE_EYE,
)
from player import circle_rect_collide


class Zombie:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.radius = ZOMBIE_RADIUS
        self.speed = ZOMBIE_SPEED
        self.hp = ZOMBIE_HP
        self.max_hp = ZOMBIE_HP
        self.alive = True

        # 游走方向（随机角度），定期改变
        self.wander_angle = random.uniform(0, math.tau)
        self.wander_timer = 0
        self.last_attack_ms = 0

    def update(self, player, walls, now_ms):
        if not self.alive:
            return

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist < ZOMBIE_AGGRO_RANGE:
            # 追击：朝玩家移动
            if dist > 0.001:
                nx = self.x + (dx / dist) * self.speed
                ny = self.y + (dy / dist) * self.speed
                self._move_with_collision(nx, ny, walls)
        else:
            # 游走：缓慢按随机方向移动，定期换方向
            self.wander_timer -= 1
            if self.wander_timer <= 0:
                self.wander_angle = random.uniform(0, math.tau)
                self.wander_timer = random.randint(60, 180)
            nx = self.x + math.cos(self.wander_angle) * self.speed * 0.4
            ny = self.y + math.sin(self.wander_angle) * self.speed * 0.4
            self._move_with_collision(nx, ny, walls)

        # 接触攻击
        if dist < ZOMBIE_ATTACK_RANGE + player.radius:
            if now_ms - self.last_attack_ms >= ZOMBIE_ATTACK_INTERVAL_MS:
                player.take_damage(ZOMBIE_ATTACK_DMG)
                self.last_attack_ms = now_ms

    def _move_with_collision(self, nx, ny, walls):
        if not any(circle_rect_collide(nx, self.y, self.radius, w) for w in walls):
            self.x = nx
        if not any(circle_rect_collide(self.x, ny, self.radius, w) for w in walls):
            self.y = ny

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False

    def draw(self, surf):
        if not self.alive:
            return
        pygame.draw.circle(surf, COLOR_ZOMBIE, (int(self.x), int(self.y)), self.radius)
        # 红眼
        pygame.draw.circle(surf, COLOR_ZOMBIE_EYE, (int(self.x - 4), int(self.y - 2)), 2)
        pygame.draw.circle(surf, COLOR_ZOMBIE_EYE, (int(self.x + 4), int(self.y - 2)), 2)
        # 血条
        if self.hp < self.max_hp:
            bw = self.radius * 2
            pygame.draw.rect(surf, (60, 20, 20), (self.x - self.radius, self.y - self.radius - 8, bw, 4))
            pygame.draw.rect(surf, (200, 50, 50),
                             (self.x - self.radius, self.y - self.radius - 8,
                              bw * self.hp / self.max_hp, 4))
