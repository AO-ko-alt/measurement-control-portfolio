# -*- coding: utf-8 -*-
"""
第 7 周实验 · 阶段五终稿：完成防呆检查修复的指令判断程序 (mud_engine_robust.py)
【核心修复要点】：
1. 空输入检查：玩家直接按回车时给出提示；
2. 不带参数的 split()：自动把 "/go    east" 中间多敲的连续空格合并切开；
3. 先检查词数 (len(parts) < 2)：防止只输入 "/go" 忘写方向引发 IndexError 崩溃；
4. 检查出口字典 (direction in room["exits"])：防止输入不存在的方向引发 KeyError；
5. 只改字典扩建第 4 房间：在 world 字典新增 "shuyuan"（白鹿洞书院），下方 if-elif 分支无需改动一行。
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


# 用 def 把指令判断分支包装起来，方便终端交互和自动测试脚本调用
def dispatch_command_robust(raw_input):
    """加上防呆检查后的指令判断函数（通过全部 5 类边界输入测试）"""
    command = raw_input.strip().lower()

    # [检查 1] 如果玩家直接按回车或只敲了空格，直接给出提示
    if not command:
        return "💡 少侠尚未输入任何指令。请输入 /look 查看四周，或输入 /go <方向> 移动。"

    loc = player["location"]
    room = world[loc]

    if command == "/look":
        exits_str = "、".join(room["exits"].keys())
        return f"【{room['name']}】{room['description']} (可用出口: {exits_str})"

    elif command == "/status":
        items = "、".join(player["inventory"])
        return (
            f"【角色状态】{player['name']} | 生命: {player['health']}/{player['max_health']} "
            f"| 铜钱: {player['gold']} | 声望: {player['reputation']} | 背包: [{items}]"
        )

    elif command == "/heal":
        if "金创药" not in player["inventory"]:
            return "⚠️ 你的行囊中已经没有【金创药】了！"
        elif player["health"] >= player["max_health"]:
            return "💡 你当前气血充沛，无需服用金创药。"
        else:
            player["inventory"].remove("金创药")
            player["health"] = min(player["max_health"], player["health"] + 20)
            return f"💊 你服下一瓶金创药，气血恢复至 {player['health']}/{player['max_health']}！"

    elif command == "/help_scholar":
        if loc != "chaguan":
            return "💡 当前地点没有需要救助的落魄书生。"
        elif player["gold"] >= 10:
            player["gold"] -= 10
            player["reputation"] += 15
            return f"🤝 你解囊相助落魄书生 10 文铜钱（剩余铜钱: {player['gold']}，江湖声望提升至 {player['reputation']}）！"
        else:
            return "⚠️ 你囊中羞涩（铜钱不足 10 文），只能向书生拱手致歉。"

    elif command.startswith("/go"):
        # [检查 2] 不带参数的 split()，自动把中间多敲的连续空格合并切开
        parts = command.split()
        # [检查 3] 先检查词数够不够 2 个，防止只输 "/go" 时取 parts[1] 触发 IndexError
        if len(parts) < 2:
            return "⚠️ 少侠欲往何方？请在 /go 后指明方向（例如：/go east）！"

        direction = parts[1]
        # [检查 4] 检查当前房间有没有这个方向的出口，防止 KeyError
        if direction in room["exits"]:
            player["location"] = room["exits"][direction]
            new_room = world[player["location"]]
            return f"🏃 你疾步向 [{direction}] 前行，抵达了【{new_room['name']}】。"
        else:
            exits_str = "、".join(room["exits"].keys())
            return f"🧱 那是一堵高耸的青砖石墙，无法向 [{direction}] 前行！(当前可用出口: {exits_str})"

    else:
        return f"❓ 无法识别该指令：\"{raw_input.strip()}\"。可用指令：/look, /status, /heal, /help_scholar, /go <方向>"


if __name__ == "__main__":
    loc = player["location"]
    print(f"=== 欢迎来到《侠客行》MUD 防御加固版引擎 (当前位置: 【{world[loc]['name']}】) ===")
    user_cmd = input("请输入指令 (/look, /status, /heal, /help_scholar, /go <方向>): ")
    print(dispatch_command_robust(user_cmd))
