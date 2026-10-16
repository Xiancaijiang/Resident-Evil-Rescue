"""
hud.py —— 抬头显示
角色立绘头像、血条、弹药、换弹提示、任务目标、结算画面。
"""
import pygame
from constants import COLOR_TEXT, COLOR_TEXT_DIM, COLOR_HEALTH, SCREEN_W, MODE_SOLO


def draw_hud(surf, player, hostage, mode, font_small, font_big, portrait=None):
    x0 = 20
    # —— 角色立绘头像 ——
    if portrait:
        ph = 44
        pw = max(1, int(portrait.get_width() * ph / portrait.get_height()))
        p = pygame.transform.smoothscale(portrait, (pw, ph))
        clip = pygame.Rect(0, 0, min(pw, 44), ph)
        # 圆形衬底
        pygame.draw.circle(surf, (35, 38, 48), (x0 + 22, 24 + 16), 24)
        surf.blit(p, (x0 + 22 - clip.width / 2, 26), clip)
        pygame.draw.circle(surf, (200, 200, 200), (x0 + 22, 24 + 16), 24, 2)
        x0 += 56

    # —— 血条 ——
    bar_x, bar_y, bar_w, bar_h = x0, 20, 200, 18
    pygame.draw.rect(surf, (40, 10, 10), (bar_x, bar_y, bar_w, bar_h))
    hp_w = bar_w * player.hp / player.max_hp
    pygame.draw.rect(surf, COLOR_HEALTH, (bar_x, bar_y, hp_w, bar_h))
    pygame.draw.rect(surf, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 2)
    hp_txt = font_small.render(f"HP {player.hp}/{player.max_hp}", True, COLOR_TEXT)
    surf.blit(hp_txt, (bar_x + 6, bar_y + 1))

    # —— 弹药 ——
    ammo_txt = font_big.render(f"{player.ammo} / {player.mag_size}", True, COLOR_TEXT)
    surf.blit(ammo_txt, (bar_x, 46))
    if player.reloading:
        r_txt = font_small.render("换弹中...", True, (255, 200, 80))
        surf.blit(r_txt, (bar_x + 110, 56))
    elif player.ammo == 0:
        r_txt = font_small.render("按 R 换弹", True, (255, 100, 100))
        surf.blit(r_txt, (bar_x + 110, 56))

    # —— 任务提示 ——
    if mode == MODE_SOLO:
        obj = font_small.render("目标：杀出重围，抵达绿色出口", True, (120, 230, 140))
    elif hostage and not hostage.rescued:
        obj = font_small.render("目标：找到被困男主（HELP 标记）", True, COLOR_TEXT_DIM)
    else:
        obj = font_small.render("目标：护送男主到达绿色出口", True, (120, 230, 140))
    surf.blit(obj, (SCREEN_W - obj.get_width() - 20, 20))

    # —— 操作提示 ——
    tip = font_small.render("WASD 移动  |  鼠标瞄准  |  左键/空格 射击  |  R 换弹", True, COLOR_TEXT_DIM)
    surf.blit(tip, (SCREEN_W / 2 - tip.get_width() / 2, 600))


def draw_center_text(surf, text, font, color, y_offset=0):
    t = font.render(text, True, color)
    surf.blit(t, (surf.get_width() / 2 - t.get_width() / 2,
                  surf.get_height() / 2 - t.get_height() / 2 + y_offset))
