# -*- coding: utf-8 -*-
"""
第 7 周实验 · 阶段一：静态世界数据 (world_data.py)

本文件只负责存放"数据"，不写游戏逻辑：
- world  ：地图字典，三层结构 = 房间代号 -> 房间信息 -> 出口字典
- player ：玩家档案字典，记录角色当前状态
引擎文件通过 `from world_data import world, player` 读取这两个字典。
"""

# ---------------------------------------------------------------------------
# 一、世界地图 world
#     结构：{ 房间代号: { "name": 中文名称,
#                        "description": 环境描述,
#                        "exits": { 方向: 目标房间代号 } } }
#     出口的键用小写英文（与引擎指令 /go east、/go west 保持一致），
#     值是另一个房间的代号，必须能在 world 中找到。
# ---------------------------------------------------------------------------
world = {
    "guangchang": {
        "name": "扬州中心广场",
        "description": "脚下是宽阔的青石板路，正中央立着一棵千年古槐。东面传来阵阵茶香，西面隐约有练武的喝彩声。",
        # 东连茶馆，西连武馆
        "exits": {"east": "chaguan", "west": "wuguan"}
    },
    "chaguan": {
        "name": "春来茶馆",
        "description": "八仙桌上摆着粗瓷盖碗茶，说书先生正拍着醒木讲述江湖轶事。门口有一位饥寒交迫的落魄书生。",
        # 西连广场：与广场的 east 互为反向出口，保证能走回来
        "exits": {"west": "guangchang"}
    },
    "wuguan": {
        "name": "振远武馆",
        "description": "青砖演武场上整齐排列着十八般兵器架，几名弟子正在练习木人桩法。",
        # 东连广场：与广场的 west 互为反向出口，保证能走回来
        "exits": {"east": "guangchang"}
    }
}

# ---------------------------------------------------------------------------
# 二、玩家档案 player
#     注意：health、max_health、gold、reputation 都要写成不带引号的整数 int，
#     这样后续才能做加减法（如 health + 20）和大小比较（如 gold >= 10）。
#     若误写成 "80"，加血会变成字符串拼接 "80" + "20" = "8020"。
# ---------------------------------------------------------------------------
player = {
    "name": "少侠郭靖",              # 姓名：字符串
    "location": "guangchang",       # 当前所在房间代号：必须是 world 中的键
    "health": 80,                   # 当前生命值：整数 int
    "max_health": 100,              # 生命上限：整数 int
    "gold": 50,                     # 铜钱：整数 int
    "reputation": 10,               # 江湖声望：整数 int
    "inventory": ["金创药", "粗布行囊"]  # 背包：列表 list
}


# ---------------------------------------------------------------------------
# 三、自测（直接运行本文件时才会执行，被 import 时不会执行）
#     对应验收清单：① 出口双向走通；② 数值为纯数字 int
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    loc = player["location"]
    print(f"📍 当前位置：【{world[loc]['name']}】")
    print(f"📜 场景描述：{world[loc]['description']}")
    print(f"🧭 可用出口：{list(world[loc]['exits'].keys())}")
    print(f"👤 角色状态：{player['name']} | 生命: {player['health']}/{player['max_health']} "
          f"| 铜钱: {player['gold']} | 声望: {player['reputation']} | 背包: {player['inventory']}")

    print("\n--- 验收①：出口双向连通 ---")
    # 相反方向对照表
    opposite = {"east": "west", "west": "east", "north": "south", "south": "north"}
    for room_id, room in world.items():
        for direction, target in room["exits"].items():
            back = world[target]["exits"].get(opposite[direction])
            ok = back == room_id
            print(f"{room_id} --{direction}--> {target} --{opposite[direction]}--> {back} : {'✅ 通' if ok else '❌ 不通'}")

    print("\n--- 验收②：数值类型检查 ---")
    for key in ("health", "max_health", "gold", "reputation"):
        value = player[key]
        print(f"player['{key}'] = {value}，类型 = {type(value).__name__}")
    print(f"服药模拟：health + 20 = {player['health'] + 20}")
