# -*- coding: utf-8 -*-
"""
第 7 周实验 · 阶段一靶场：存在类型安全隐患的静态世界蓝图 (world_data_buggy.py)
【人工代码审查任务】：请找出下方 player 字典与回血计算中的数据类型错误（"80" + "20" 陷阱）并修正。
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

# ⚠️ 缺陷靶场：注意检查 health 与 gold 的数据类型是否誤加了双引号！
player = {
    "name": "少侠郭靖",
    "location": "guangchang",
    "health": "80",          # [缺陷 1] 误用 str 字符串表示血量数值
    "max_health": 100,
    "gold": "50",            # [缺陷 2] 误用 str 字符串表示铜钱数值
    "inventory": ["金创药", "粗布行囊"]
}

if __name__ == "__main__":
    loc = player["location"]
    print(f"📍 当前位置：【{world[loc]['name']}】")
    print(f"📜 场景描述：{world[loc]['description']}")
    # 模拟服用金创药恢复 20 点生命值
    player["health"] = player["health"] + "20"
    print(f"💊 服用金创药后生命值：{player['health']} (类型: {type(player['health']).__name__})")
    if player["health"] == "8020":
        print("❌ [类型审查告警] 触发字符串拼接 Bug：80 点血 + 20 点药水变成了 \"8020\"！")
