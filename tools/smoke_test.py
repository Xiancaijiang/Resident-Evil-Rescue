"""
smoke_test.py —— 无头冒烟测试
用 SDL dummy 视频驱动，不弹窗验证：
  1. 素材加载（三角色精灵帧 + 三张立绘）
  2. 两种模式的游戏初始化与若干帧更新不抛异常
  3. 胜负判定路径可达（solo 到出口、rescue 接触+到出口）
"""
import os
import sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from game import Game, MENU_OPTIONS
from constants import MODE_SOLO, MODE_RESCUE

failures = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        failures.append(name)


game = Game()

# —— 素材加载 ——
import sprites
for c in ("hero", "fuji", "karen"):
    ss = sprites.load_sprite_set(c)
    check(f"精灵集 {c}", ss is not None and len(ss) >= 3)
    check(f"立绘 {c}", sprites.load_portrait(c) is not None)

# —— SOLO 模式 ——
game._start_game(MENU_OPTIONS[0])
check("solo 模式", game.mode == MODE_SOLO and game.state == "PLAYING")
check("solo 无 hostage", game.hostage is None)
check("solo 玩家为 hero", game.player.char_key == "hero")
for _ in range(120):
    game._update()
check("solo 120 帧更新无异常", game.state == "PLAYING")
# 直接把玩家放到出口 => WIN
game.player.x, game.player.y = game.exit_rect.centerx, game.exit_rect.centery
game._update()
check("solo 抵达出口获胜", game.state == "WIN")

# —— RESCUE 模式（fuji）——
game.state = "MENU"
game._start_game(MENU_OPTIONS[1])
check("rescue 模式", game.mode == MODE_RESCUE and game.state == "PLAYING")
check("rescue 有 hostage", game.hostage is not None)
check("rescue 玩家为 fuji", game.player.char_key == "fuji")
for _ in range(120):
    game._update()
check("rescue 120 帧更新无异常", game.state == "PLAYING")
check("hostage 初始未获救", not game.hostage.rescued)
# 玩家瞬移到男主身边 => 触发获救
game.player.x, game.player.y = game.hostage.x, game.hostage.y
game._update()
check("接触后 hostage 获救", game.hostage.rescued)
# 双方瞬移到出口 => WIN
game.player.x, game.player.y = game.exit_rect.centerx, game.exit_rect.centery
game.hostage.x, game.hostage.y = game.exit_rect.centerx, game.exit_rect.centery
game._update()
check("rescue 护送成功", game.state == "WIN")

# —— RESCUE 模式（karen）失败路径 ——
game.state = "MENU"
game._start_game(MENU_OPTIONS[2])
game.player.hp = 0
game._update()
check("玩家死亡判负", game.state == "LOSE")

# —— 菜单绘制不抛异常 ——
game.state = "MENU"
game._draw()
check("菜单绘制无异常", True)

pygame.quit()
print()
if failures:
    print(f"共 {len(failures)} 项失败")
    raise SystemExit(1)
print("全部冒烟测试通过")
