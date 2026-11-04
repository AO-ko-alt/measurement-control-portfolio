# -*- coding: utf-8 -*-
"""
第 7 周实验 · 阶段一基准：通过类型安全审查的静态世界与角色数据蓝图 (world_data.py)
"""

world = {
    "guangchang": {
        "name": "扬州中心广场",
        "description": "脚下是宽阔的青石板路，正中央立着一棵千年古槐。东面传来阵阵茶香，西面隐约有练武的喝彩声。",
        "exits": {"east": "chaguan", "west": "wuguan"}
    },
    "chaguan": {
        "name": "春来茶馆",
        "description": "八仙桌上摆着粗瓷盖碗茶，说书先生正拍着醒木讲述江湖轶事。门口有一位饥寒交迫的落魄书生。",
        "exits": {"west": "guangchang"}
    },
    "wuguan": {
        "name": "振远武馆",
        "description": "青砖演武场上整齐排列着十八般兵器架，几名弟子正在练习木人桩法。",
        "exits": {"east": "guangchang"}
    }
}

player = {
    "name": "少侠郭靖",
    "location": "guangchang",
    "health": 80,            # [已修正] 整数 int 类型，支持算术加减与大小比较
    "max_health": 100,
    "gold": 50,              # [已修正] 整数 int 类型
    "reputation": 10,        # 江湖声望值（用于价值抉择分支记录）
    "inventory": ["金创药", "粗布行囊"]
}

if __name__ == "__main__":
    loc = player["location"]
    print(f"📍 当前位置：【{world[loc]['name']}】")
    print(f"📜 场景描述：{world[loc]['description']}")
    print(f"🧭 可用出口：{list(world[loc]['exits'].keys())}")
    print(f"👤 角色状态：{player['name']} | HP: {player['health']}/{player['max_health']} | 铜钱: {player['gold']} | 背包: {player['inventory']}")
