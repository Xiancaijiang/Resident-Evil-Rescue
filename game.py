"""
game.py —— 主游戏循环与状态机
状态：MENU（选择模式与角色） -> PLAYING -> WIN / LOSE
模式：
  - solo   男主单打独斗：操控男主从关押点杀到出口
  - rescue 救援模式：操控 fuji/karen 找到男主并护送他到出口
两种模式共用同一关卡（墙体/丧尸/道具一致）。
"""
import sys
import math
import pygame

from constants import (
    SCREEN_W, SCREEN_H, FPS, TITLE,
    COLOR_BG, COLOR_FLOOR, COLOR_GRID, COLOR_WALL, COLOR_WALL_BORDER,
    COLOR_EXIT, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_BULLET,
    CHARACTERS, HEAL_PACK_AMOUNT, MODE_SOLO, MODE_RESCUE,
)
from player import Player
from zombie import Zombie
from items import Item
from hostage import Hostage
from level import build_level
from hud import draw_hud, draw_center_text
import sprites

# ===== 菜单选项（顺序即按键 1/2/3） =====
MENU_OPTIONS = [
    {"char": "hero", "mode": MODE_SOLO, "tag": "单打独斗",
     "desc": "操控男主，独自杀出重围"},
    {"char": "fuji", "mode": MODE_RESCUE, "tag": "救援模式",
     "desc": "扮演藤，找到男主并护送撤离"},
    {"char": "karen", "mode": MODE_RESCUE, "tag": "救援模式",
     "desc": "扮演凯伦，找到男主并护送撤离"},
]


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.SysFont("microsoftyahei,simhei,arial", 18)
        self.font_big = pygame.font.SysFont("microsoftyahei,simhei,arial", 28)
        self.font_title = pygame.font.SysFont("microsoftyahei,simhei,arial", 44, bold=True)

        self.state = "MENU"  # MENU / PLAYING / WIN / LOSE
        self.mode = None
        self.selected_char = None
        self.portraits = {c: sprites.load_portrait(c) for c in ("hero", "fuji", "karen")}
        self._reset_level(None, None)

    # ---------- 关卡初始化 ----------
    def _reset_level(self, char_key, mode):
        level = build_level()
        self.walls = level["walls"]
        self.exit_rect = level["exit_rect"]
        self.zombies = [Zombie(x, y) for (x, y) in level["zombie_spawns"]]
        self.items = [Item(x, y, kind) for (x, y, kind) in level["item_spawns"]]
        self.bullets = []
        self.hostage = None
        self.player = None
        if not char_key:
            return
        if mode == MODE_SOLO:
            # 男主从关押点出发
            self.player = Player(char_key, *level["hostage_pos"])
        else:
            self.player = Player(char_key, *level["player_spawn"])
            self.hostage = Hostage(*level["hostage_pos"])

    # ---------- 主循环 ----------
    def run(self):
        while True:
            self._handle_events()
            self._update()
            self._draw()
            pygame.display.flip()
            self.clock.tick(FPS)

    # ---------- 事件 ----------
    def _handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if self.state == "MENU":
                    if e.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        opt = MENU_OPTIONS[e.key - pygame.K_1]
                        self._start_game(opt)
                elif self.state in ("WIN", "LOSE"):
                    if e.key == pygame.K_r:
                        self.state = "MENU"
                        self.selected_char = None
                        self._reset_level(None, None)
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.state == "MENU":
                    self._menu_click(e.pos)

    def _menu_cards(self):
        """三张选项卡的位置。"""
        return [pygame.Rect(70 + i * 280, 180, 260, 320) for i in range(3)]

    def _menu_click(self, pos):
        for opt, rect in zip(MENU_OPTIONS, self._menu_cards()):
            if rect.collidepoint(pos):
                self._start_game(opt)

    def _start_game(self, opt):
        self.selected_char = opt["char"]
        self.mode = opt["mode"]
        self._reset_level(opt["char"], opt["mode"])
        self.state = "PLAYING"

    # ---------- 更新 ----------
    def _update(self):
        if self.state != "PLAYING":
            return

        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        # —— 移动 ——
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1
        self.player.moving = bool(dx or dy)
        if dx or dy:
            length = math.hypot(dx, dy)
            self.player.move(dx / length * self.player.speed,
                             dy / length * self.player.speed, self.walls)

        # —— 瞄准 ——
        self.player.update_aim(mouse)

        # —— 射击（按住左键或空格）——
        if mouse_pressed or keys[pygame.K_SPACE]:
            self.player.try_shoot(now, self.bullets)

        # —— 换弹 ——
        if keys[pygame.K_r]:
            self.player.try_reload(now)
        self.player.update_reload(now)

        # —— 子弹 ——
        for b in self.bullets:
            b.update(self.walls)
        self.bullets = [b for b in self.bullets if b.alive]

        # —— 子弹 vs 丧尸 ——
        for b in self.bullets:
            for z in self.zombies:
                if not z.alive:
                    continue
                if math.hypot(b.x - z.x, b.y - z.y) < z.radius + b.radius:
                    z.take_damage(b.damage)
                    b.alive = False
                    break
        self.bullets = [b for b in self.bullets if b.alive]

        # —— 丧尸 ——
        for z in self.zombies:
            z.update(self.player, self.walls, now)

        # —— 道具拾取 ——
        for it in self.items:
            if it.collected:
                continue
            if math.hypot(it.x - self.player.x, it.y - self.player.y) < it.radius + self.player.radius:
                it.collected = True
                if it.kind == "health":
                    self.player.hp = min(self.player.max_hp, self.player.hp + HEAL_PACK_AMOUNT)
                else:
                    self.player.ammo = self.player.mag_size

        # —— 男主 NPC（仅救援模式）——
        if self.hostage:
            self.hostage.update(self.player, self.zombies, self.walls, now)

        # —— 胜负判定 ——
        if self.player.is_dead:
            self.state = "LOSE"
            return
        if self.mode == MODE_SOLO:
            if self.exit_rect.collidepoint(self.player.x, self.player.y):
                self.state = "WIN"
        else:
            if not self.hostage.alive:
                self.state = "LOSE"
                return
            if self.hostage.rescued:
                if (self.exit_rect.collidepoint(self.player.x, self.player.y) and
                        self.exit_rect.collidepoint(self.hostage.x, self.hostage.y)):
                    self.state = "WIN"

    # ---------- 绘制 ----------
    def _draw(self):
        self.screen.fill(COLOR_BG)

        if self.state == "MENU":
            self._draw_menu()
            return

        # 地板 + 网格
        self.screen.fill(COLOR_FLOOR)
        for x in range(0, SCREEN_W, 40):
            pygame.draw.line(self.screen, COLOR_GRID, (x, 0), (x, SCREEN_H))
        for y in range(0, SCREEN_H, 40):
            pygame.draw.line(self.screen, COLOR_GRID, (0, y), (SCREEN_W, y))

        # 出口
        pygame.draw.rect(self.screen, COLOR_EXIT, self.exit_rect, border_radius=6)
        pygame.draw.rect(self.screen, (20, 80, 40), self.exit_rect, 3, border_radius=6)
        ex = self.font_small.render("EXIT", True, (20, 60, 30))
        self.screen.blit(ex, (self.exit_rect.centerx - ex.get_width() / 2,
                              self.exit_rect.centery - ex.get_height() / 2))

        # 墙体
        for w in self.walls:
            pygame.draw.rect(self.screen, COLOR_WALL, w)
            pygame.draw.rect(self.screen, COLOR_WALL_BORDER, w, 2)

        # 道具
        for it in self.items:
            it.draw(self.screen)

        # 丧尸
        for z in self.zombies:
            z.draw(self.screen)

        # 男主 NPC（仅救援模式）
        if self.hostage:
            self.hostage.draw(self.screen, self.font_small)

        # 玩家
        now = pygame.time.get_ticks()
        if self.player:
            self.player.draw(self.screen, now)

        # 子弹
        for b in self.bullets:
            b.draw(self.screen, COLOR_BULLET)

        # HUD
        if self.player:
            draw_hud(self.screen, self.player, self.hostage, self.mode,
                     self.font_small, self.font_big,
                     self.portraits.get(self.selected_char))

        # 结算覆盖
        if self.state == "WIN":
            text = "成功突围！" if self.mode == MODE_SOLO else "救援成功！"
            self._draw_overlay(text, (90, 220, 120))
        elif self.state == "LOSE":
            if self.mode == MODE_RESCUE and self.hostage and not self.hostage.alive:
                reason = "男主已阵亡"
            else:
                reason = "你已阵亡"
            self._draw_overlay(f"任务失败：{reason}", (230, 80, 80))

    def _draw_menu(self):
        self.screen.fill(COLOR_BG)
        title = self.font_title.render("生化危机爆发夜 · 救援", True, (230, 70, 70))
        self.screen.blit(title, (SCREEN_W / 2 - title.get_width() / 2, 48))
        sub = self.font_small.render("选择游戏方式：男主单打独斗，或扮演 Fuji / Karen 帮助男主通关（关卡一致）",
                                     True, COLOR_TEXT_DIM)
        self.screen.blit(sub, (SCREEN_W / 2 - sub.get_width() / 2, 112))

        for i, (opt, rect) in enumerate(zip(MENU_OPTIONS, self._menu_cards())):
            char = opt["char"]
            cfg = CHARACTERS[char]
            pygame.draw.rect(self.screen, (35, 38, 48), rect, border_radius=10)
            pygame.draw.rect(self.screen, cfg["color"], rect, 3, border_radius=10)

            # —— 立绘（高度 150，等比缩放居中）——
            portrait = self.portraits.get(char)
            img_y = rect.top + 14
            if portrait:
                ph = 150
                pw = max(1, int(portrait.get_width() * ph / portrait.get_height()))
                p = pygame.transform.smoothscale(portrait, (pw, ph))
                # 裁掉超出卡片宽度的部分
                clip = pygame.Rect(0, 0, min(pw, rect.width - 20), ph)
                self.screen.blit(p, (rect.centerx - clip.width / 2, img_y), clip)
            else:
                pygame.draw.circle(self.screen, cfg["color"],
                                   (rect.centerx, img_y + 75), 50)
                pygame.draw.circle(self.screen, (255, 255, 255),
                                   (rect.centerx, img_y + 75), 50, 2)

            # —— 名称与模式标签 ——
            name = self.font_big.render(cfg["name"], True, COLOR_TEXT)
            self.screen.blit(name, (rect.centerx - name.get_width() / 2, rect.top + 172))
            tag = self.font_small.render(f"【{opt['tag']}】", True, (255, 210, 90))
            self.screen.blit(tag, (rect.centerx - tag.get_width() / 2, rect.top + 206))
            desc = self.font_small.render(opt["desc"], True, COLOR_TEXT_DIM)
            self.screen.blit(desc, (rect.centerx - desc.get_width() / 2, rect.top + 230))

            # —— 属性 ——
            stats = f"HP {cfg['max_hp']}  弹匣 {cfg['mag_size']}  伤害 {cfg['bullet_damage']}  移速 {cfg['speed']}"
            st = self.font_small.render(stats, True, COLOR_TEXT_DIM)
            self.screen.blit(st, (rect.centerx - st.get_width() / 2, rect.top + 256))

            # —— 按键提示 ——
            tip = self.font_small.render(f"按 {i + 1}", True, (255, 220, 100))
            self.screen.blit(tip, (rect.centerx - tip.get_width() / 2, rect.bottom - 34))

        foot = self.font_small.render("点击卡片或按 1 / 2 / 3 开始   |   ESC 退出", True, COLOR_TEXT_DIM)
        self.screen.blit(foot, (SCREEN_W / 2 - foot.get_width() / 2, 540))

    def _draw_overlay(self, text, color):
        s = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 160))
        self.screen.blit(s, (0, 0))
        draw_center_text(self.screen, text, self.font_title, color, -30)
        tip = self.font_small.render("按 R 返回菜单   |   ESC 退出", True, COLOR_TEXT)
        self.screen.blit(tip, (SCREEN_W / 2 - tip.get_width() / 2, SCREEN_H / 2 + 30))
