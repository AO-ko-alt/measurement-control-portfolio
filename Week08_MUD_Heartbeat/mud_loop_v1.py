# -*- coding: utf-8 -*-
"""
第 8 周实验 · 多轮持续交互主循环脚本 (mud_loop_v1.py)

由第 7 周「单回合」引擎改造而来，四条关键约束：
1. world 地图字典与 player 玩家字典（初始位置 "guangchang"）定义在 while True 外部上方，
   循环内只更新 player["location"]，绝不重建字典，因此位置不会在下一轮被重置；
2. 进入 while True 之前只打印一次初始房间开场白，循环开头不重复打印场景；
3. 循环内仅 /look 与 /go <方向> 成功移动时才打印房间描述，且每次只打印一遍；
4. /quit 分支打印告别语并立即 break，防止死循环。
"""

world = {
    "guangchang": {
        "name": "扬州中心广场",
        "description": "脚下是宽阔的青石板路，正中央立着一棵千年古槐。东面茶香袅袅，西面喝彩阵阵，北面通往白鹿洞书院。",
        "exits": {"east": "chaguan", "west": "wuguan", "north": "shuyuan"}
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
    },
    "shuyuan": {
        "name": "白鹿洞书院",
        "description": "翠竹掩映着古朴的藏书阁，案头摆放着先贤手稿，令人心神宁静。",
        "exits": {"south": "guangchang"}
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
    """按 player 当前位置生成房间描述（含房间名、场景、可用出口）。"""
    room = world[player["location"]]
    exits_str = "、".join(room["exits"].keys())
    return f"【{room['name']}】{room['description']}（可用出口：{exits_str}）"


def dispatch_command(raw_input):
    """执行一条指令，返回本轮要打印的文字；只有 /look 和 /go 成功时带房间描述。"""
    command = raw_input.strip().lower()

    if not command:
        return "少侠尚未输入任何指令。请输入 /look 查看四周，或输入 /go <方向> 移动。"

    # 每轮都从 player 重新取当前位置，查表得到当前房间
    room = world[player["location"]]

    if command == "/look":
        return describe_room()

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
            return f"你向 [{direction}] 前行，抵达了新房间。\n{describe_room()}"
        exits_str = "、".join(room["exits"].keys())
        return f"[{direction}] 方向没有路，暂时无法通行。（当前可用出口：{exits_str}）"

    return f"无法识别的指令：{raw_input.strip()}。可用指令：/look、/status、/heal、/help_scholar、/go <方向>、/quit。"


if __name__ == "__main__":
    # 【循环外】初始开场白：整个程序只在此处打印一次
    print("=== 欢迎来到《侠客行》MUD（输入 /quit 退出）===")
    print(f"初始位置：{describe_room()}")

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

        print(dispatch_command(raw))
