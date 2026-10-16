"""
constants.py
《生化危机爆发夜·救援》 —— 全局可调参数集中区
所有数值/颜色/尺寸均在此统一配置，便于平衡调整与后期迁移。
"""

# ===== 窗口 =====
SCREEN_W = 960
SCREEN_H = 640
FPS = 60
TITLE = "生化危机爆发夜·救援"

# ===== 颜色 =====
COLOR_BG = (20, 22, 28)            # 背景深色
COLOR_FLOOR = (28, 32, 40)         # 地板
COLOR_GRID = (38, 42, 52)          # 网格线
COLOR_WALL = (70, 74, 86)          # 墙体
COLOR_WALL_BORDER = (110, 114, 128)
COLOR_PLAYER_FUJI = (70, 130, 220)    # 藤：蓝
COLOR_PLAYER_KAREN = (225, 100, 160)  # 凯伦：粉
COLOR_ZOMBIE = (90, 170, 90)       # 丧尸：绿
COLOR_ZOMBIE_EYE = (200, 40, 40)
COLOR_BULLET = (255, 220, 90)
COLOR_HEALTH = (210, 50, 60)
COLOR_AMMO = (230, 200, 70)
COLOR_HOSTAGE = (240, 210, 70)     # 男主：黄
COLOR_EXIT = (60, 200, 90)
COLOR_TEXT = (235, 235, 235)
COLOR_TEXT_DIM = (150, 155, 165)

# ===== 玩家属性 =====
PLAYER_RADIUS = 14
CHARACTERS = {
    "hero": {
        "name": "男主 Hero",
        "color": COLOR_HOSTAGE,
        "max_hp": 100,
        "speed": 2.6,
        "mag_size": 10,
        "reload_ms": 1100,
        "fire_interval_ms": 280,
        "bullet_damage": 30,
        "bullet_speed": 9.5,
    },
    "fuji": {
        "name": "藤 Fuji",
        "color": COLOR_PLAYER_FUJI,
        "max_hp": 120,
        "speed": 2.2,
        "mag_size": 12,
        "reload_ms": 1300,
        "fire_interval_ms": 360,
        "bullet_damage": 34,
        "bullet_speed": 9.0,
    },
    "karen": {
        "name": "凯伦 Karen",
        "color": COLOR_PLAYER_KAREN,
        "max_hp": 80,
        "speed": 3.0,
        "mag_size": 8,
        "reload_ms": 900,
        "fire_interval_ms": 220,
        "bullet_damage": 28,
        "bullet_speed": 10.0,
    },
}

# ===== 游戏模式 =====
MODE_SOLO = "solo"        # 男主单打独斗：操控男主从关押点杀到出口
MODE_RESCUE = "rescue"    # 救援模式：操控 fuji/karen 找到男主并护送出出口

# ===== 精灵素材 =====
ASSET_DIR = "assets"          # 素材根目录（相对 main.py）
SPRITE_HEIGHT = 56            # 游戏内精灵渲染高度（像素）
ANIM_INTERVAL_MS = 160        # 行走动画每帧时长
IDLE_INTERVAL_MS = 500        # 待机呼吸动画每帧时长
SHOOT_ANIM_MS = 180           # 开枪后射击姿态保持时长

# ===== 丧尸 =====
ZOMBIE_RADIUS = 13
ZOMBIE_SPEED = 1.1
ZOMBIE_HP = 60
ZOMBIE_AGGRO_RANGE = 230      # 进入此范围开始追击
ZOMBIE_ATTACK_RANGE = 22      # 接触攻击距离
ZOMBIE_ATTACK_DMG = 8
ZOMBIE_ATTACK_INTERVAL_MS = 700

# ===== 子弹 =====
BULLET_RADIUS = 4

# ===== 道具 =====
ITEM_RADIUS = 12
HEAL_PACK_AMOUNT = 40
AMMO_PACK_AMOUNT = 12         # 一次补满弹匣

# ===== 被救男主 =====
HOSTAGE_RADIUS = 14
HOSTAGE_SPEED = 1.6
HOSTAGE_FOLLOW_DIST = 40      # 与玩家保持的距离

# ===== 关卡（见 level.py） =====
WALL_THICKNESS = 16
