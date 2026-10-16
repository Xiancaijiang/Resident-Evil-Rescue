"""
make_screenshots.py —— 无头渲染菜单与游戏画面，输出 README 截图。
"""
import os
import sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from game import Game, MENU_OPTIONS

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(BASE, "docs")
os.makedirs(DOCS, exist_ok=True)

game = Game()

# —— 菜单 ——
game._draw()
pygame.image.save(game.screen, os.path.join(DOCS, "screenshot_menu.png"))
print("menu ok")

# —— 救援模式游戏画面（fuji 视角，模拟移动几步）——
game._start_game(MENU_OPTIONS[1])
import pygame as pg
for _ in range(90):
    # 模拟按键不可行（无头），直接改位置
    game.player.x += 2
    game.player.moving = True
    game._update()
game._draw()
pygame.image.save(game.screen, os.path.join(DOCS, "screenshot_rescue.png"))
print("rescue ok")

# —— solo 模式画面 ——
game.state = "MENU"
game._start_game(MENU_OPTIONS[0])
for _ in range(60):
    game.player.y += 1.5
    game.player.moving = True
    game._update()
game._draw()
pygame.image.save(game.screen, os.path.join(DOCS, "screenshot_solo.png"))
print("solo ok")

pygame.quit()
