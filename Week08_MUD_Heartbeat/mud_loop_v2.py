# -*- coding: utf-8 -*-
"""
第 8 周实验 · 多轮持续交互主循环脚本 v2 (mud_loop_v2.py)

在 mud_loop_v1.py 基础上的增量升级：保留 while True 主循环结构、循环外 world/player
状态初始化、/go 参数长度检查、/quit 安全退出机制，以及原有全部指令行为；
仅新增房间地面物品数据和三处 for 遍历打印。

新增内容：
1. world 每个房间都带 "items" 列表（地面物品）；
2. print_room() 用 `for item in room["items"]:` 逐行打印地面物品，
   用 `for d, tid in room["exits"].items():` 遍历出口字典并通过 world[tid]["name"]
   打印目标房间中文名称；/look 与 /go 成功移动时都会调用它；
3. 新增 /bag 指令，用 `for idx, item in enumerate(player["inventory"], 1):`
   打印从 [1] 开始编号的背包清单。
"""

world = {
    "guangchang": {
        "name": "扬州中心广场",
        "description": "脚下是宽阔的青石板路，正中央立着一棵千年古槐。东面茶香袅袅，西面喝彩阵阵，北面通往白鹿洞书院。",
        "exits": {"east": "chaguan", "west": "wuguan", "north": "shuyuan"},
        "items": ["一枚磨损的铜钱", "半张残破的江湖地图"]
    },
    "chaguan": {
        "name": "春来茶馆",
        "description": "八仙桌上摆着粗瓷盖碗茶，说书先生正拍着醒木讲述江湖轶事。门口有一位饥寒交迫的落魄书生。",
        "exits": {"west": "guangchang"},
        "items": ["一盏温热的盖碗茶", "落魄书生遗落的书卷"]
    },
    "wuguan": {
        "name": "振远武馆",
        "description": "青砖演武场上整齐排列着十八般兵器架，几名弟子正在练习木人桩法。",
        "exits": {"east": "guangchang"},
        "items": ["一柄练功用的木刀", "一卷泛黄的拳谱抄本"]
    },
    "shuyuan": {
        "name": "白鹿洞书院",
        "description": "翠竹掩映着古朴的藏书阁，案头摆放着先贤手稿，令人心神宁静。",
        "exits": {"south": "guangchang"},
        "items": ["一支狼毫笔", "一方旧砚台"]
    }
}

player = {
    "name": "少侠郭靖",
    "location": "guangchang",
    "health": 80,
    "max_health": 100,
    "gold": 50,
    "reputation": 10,
    "inventory": ["金创药", "粗布行囊"]
}


def describe_room():
    """按 player 当前位置生成房间名与场景描述。"""
    room = world[player["location"]]
    return f"【{room['name']}】{room['description']}"


def print_room():
    """打印房间完整信息：场景 + 地面物品 + 带中文目标名的可用出口。"""
    room = world[player["location"]]
    print(describe_room())

    print("地面物品：")
    if not room["items"]:
        print("  （空）")
    for item in room["items"]:
        print(f"  · {item}")

    print("可用出口：")
    for d, tid in room["exits"].items():
        print(f"  - {d} → 【{world[tid]['name']}】")


def print_bag():
    """带序号打印背包清单，编号从 [1] 开始。"""
    print("【背包清单】")
    if not player["inventory"]:
        print("  （空）")
    for idx, item in enumerate(player["inventory"], 1):
        print(f"  [{idx}] {item}")


def dispatch_command(raw_input):
    """执行一条指令；房间信息与背包由本函数逐行打印，其余指令返回文字交主循环打印。"""
    command = raw_input.strip().lower()

    if not command:
        return "少侠尚未输入任何指令。请输入 /look 查看四周，或输入 /go <方向> 移动。"

    # 每轮都从 player 重新取当前位置，查表得到当前房间
    room = world[player["location"]]

    if command == "/look":
        print_room()
        return None

    if command == "/bag":
        print_bag()
        return None

    if command == "/status":
        items = "、".join(player["inventory"])
        return (
            f"【角色状态】{player['name']} | 生命: {player['health']}/{player['max_health']} "
            f"| 铜钱: {player['gold']} | 声望: {player['reputation']} | 背包: [{items}]"
        )

    if command == "/heal":
        if "金创药" not in player["inventory"]:
            return "你的行囊中已经没有【金创药】了。"
        if player["health"] >= player["max_health"]:
            return "你当前气血充沛，无需服用金创药。"
        player["inventory"].remove("金创药")
        player["health"] = min(player["max_health"], player["health"] + 20)
        return f"你服下一瓶金创药，气血恢复至 {player['health']}/{player['max_health']}。"

    if command == "/help_scholar":
        if player["location"] != "chaguan":
            return "当前地点没有需要救助的落魄书生。"
        if player["gold"] < 10:
            return "你囊中羞涩（铜钱不足 10 文），只能向书生拱手致歉。"
        player["gold"] -= 10
        player["reputation"] += 15
        return f"你解囊相助落魄书生 10 文铜钱（剩余铜钱: {player['gold']}，江湖声望提升至 {player['reputation']}）。"

    if command.startswith("/go"):
        parts = command.split()  # 不带参数，合并连续空格
        if len(parts) < 2:
            return "少侠欲往何方？请在 /go 后指明方向（例如：/go east）。"

        direction = parts[1]
        if direction in room["exits"]:
            # 只更新局外字典里的位置字段，不重建 player，故下一轮仍在茶馆
            player["location"] = room["exits"][direction]
            print(f"你向 [{direction}] 前行，抵达了新房间。")
            print_room()
            return None
        exits_str = "、".join(room["exits"].keys())
        return f"[{direction}] 方向没有路，暂时无法通行。（当前可用出口：{exits_str}）"

    return f"无法识别的指令：{raw_input.strip()}。可用指令：/look、/bag、/status、/heal、/help_scholar、/go <方向>、/quit。"


if __name__ == "__main__":
    # 【循环外】初始开场白：整个程序只在此处打印一次
    print("=== 欢迎来到《侠客行》MUD v2（输入 /quit 退出）===")
    print("初始位置：")
    print_room()

    while True:
        try:
            # 去掉终端/管道输入可能附带的 BOM，保证首条指令也能被识别
            raw = input("\n请输入指令：").lstrip("\ufeff")
        except (EOFError, KeyboardInterrupt):
            print("后会有期！")
            break

        # 【安全退出分支】打印告别语后立即终止循环
        if raw.strip().lower() == "/quit":
            print("后会有期！")
            break

        result = dispatch_command(raw)
        if result is not None:
            print(result)
