"""
player.py —— 玩家角色
负责移动、瞄准、射击、换弹、碰撞、受伤。
"""
import math
import pygame
from constants import (
    CHARACTERS, PLAYER_RADIUS, BULLET_RADIUS,
    ANIM_INTERVAL_MS, IDLE_INTERVAL_MS, SHOOT_ANIM_MS,
)
import sprites


def circle_rect_collide(cx, cy, r, rect):
    """圆与矩形碰撞检测，返回最近点距离平方 <= r^2。"""
    closest_x = max(rect.left, min(cx, rect.right))
    closest_y = max(rect.top, min(cy, rect.bottom))
    dx = cx - closest_x
    dy = cy - closest_y
    return dx * dx + dy * dy <= r * r


class Bullet:
    """玩家发射的子弹。"""
    def __init__(self, x, y, angle, speed, damage):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.damage = damage
        self.alive = True
        self.radius = BULLET_RADIUS

    def update(self, walls):
        self.x += self.vx
        self.y += self.vy
        # 出界或撞墙则消失
        if self.x < 0 or self.x > 960 or self.y < 0 or self.y > 640:
            self.alive = False
            return
        for w in walls:
            if circle_rect_collide(self.x, self.y, self.radius, w):
                self.alive = False
                return

    def draw(self, surf, color):
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), self.radius)


class Player:
    def __init__(self, char_key, x, y):
        cfg = CHARACTERS[char_key]
        self.char_key = char_key
        self.name = cfg["name"]
        self.color = cfg["color"]
        self.x = float(x)
        self.y = float(y)
        self.radius = PLAYER_RADIUS

        self.max_hp = cfg["max_hp"]
        self.hp = cfg["max_hp"]
        self.speed = cfg["speed"]

        self.mag_size = cfg["mag_size"]
        self.ammo = cfg["mag_size"]
        self.reload_ms = cfg["reload_ms"]
        self.fire_interval_ms = cfg["fire_interval_ms"]
        self.bullet_damage = cfg["bullet_damage"]
        self.bullet_speed = cfg["bullet_speed"]

        self.last_shot_ms = 0
        self.reloading = False
        self.reload_start_ms = 0
        self.angle = 0.0  # 瞄准角度

        # —— 精灵动画状态 ——
        self.sprite_set = sprites.load_sprite_set(char_key)
        self.moving = False          # 本帧是否在移动（game 循环每帧重置设置）
        self.walk_anim_ms = 0        # 行走动画计时
        self.idle_anim_ms = 0        # 待机动画计时

    @property
    def facing_left(self):
        return math.cos(self.angle) < 0

    def current_action(self, now_ms):
        """根据状态选择动作：开枪后短时间保持 shoot，移动时 walk，否则 idle。"""
        if now_ms - self.last_shot_ms < SHOOT_ANIM_MS and self.ammo >= 0:
            return "shoot"
        if self.moving:
            return "walk"
        return "idle"

    def current_frame(self, now_ms, action):
        if action == "walk":
            return (now_ms // ANIM_INTERVAL_MS) % 3
        if action == "idle":
            return (now_ms // IDLE_INTERVAL_MS) % 3
        return (now_ms // 90) % 3  # shoot 快速循环

    # ---- 移动（带墙体碰撞，分轴检测避免卡墙） ----
    def move(self, dx, dy, walls):
        nx = self.x + dx
        if not any(circle_rect_collide(nx, self.y, self.radius, w) for w in walls):
            self.x = nx
        ny = self.y + dy
        if not any(circle_rect_collide(self.x, ny, self.radius, w) for w in walls):
            self.y = ny

    def update_aim(self, mouse_pos):
        self.angle = math.atan2(mouse_pos[1] - self.y, mouse_pos[0] - self.x)

    def try_shoot(self, now_ms, bullets):
        if self.reloading:
            return
        if self.ammo <= 0:
            return
        if now_ms - self.last_shot_ms < self.fire_interval_ms:
            return
        self.last_shot_ms = now_ms
        self.ammo -= 1
        # 子弹从枪口（角色前方）生成
        bx = self.x + math.cos(self.angle) * (self.radius + 4)
        by = self.y + math.sin(self.angle) * (self.radius + 4)
        bullets.append(Bullet(bx, by, self.angle, self.bullet_speed, self.bullet_damage))

    def try_reload(self, now_ms):
        if self.reloading or self.ammo == self.mag_size:
            return
        self.reloading = True
        self.reload_start_ms = now_ms

    def update_reload(self, now_ms):
        if self.reloading and now_ms - self.reload_start_ms >= self.reload_ms:
            self.ammo = self.mag_size
            self.reloading = False

    def take_damage(self, dmg):
        self.hp = max(0, self.hp - dmg)

    @property
    def is_dead(self):
        return self.hp <= 0

    def draw(self, surf, now_ms=0):
        # 优先用精灵帧绘制（脚底对齐角色中心下方）
        action = self.current_action(now_ms)
        frame = self.current_frame(now_ms, action)
        foot_y = self.y + self.radius + 2
        if sprites.draw_sprite(surf, self.sprite_set, action, frame,
                               self.x, foot_y, self.facing_left):
            # 枪口朝向辅助线（淡化，避免遮挡素材）
            gx = self.x + math.cos(self.angle) * (self.radius + 10)
            gy = self.y + math.sin(self.angle) * (self.radius + 10)
            pygame.draw.line(surf, (200, 200, 200), (int(self.x), int(self.y)),
                             (int(gx), int(gy)), 2)
            return
        # —— 素材缺失时的矢量回退绘制 ——
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surf, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 2)
        gx = self.x + math.cos(self.angle) * (self.radius + 10)
        gy = self.y + math.sin(self.angle) * (self.radius + 10)
        pygame.draw.line(surf, (240, 240, 240), (int(self.x), int(self.y)), (int(gx), int(gy)), 3)
