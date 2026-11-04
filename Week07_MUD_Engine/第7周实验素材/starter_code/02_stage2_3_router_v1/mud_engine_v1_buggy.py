# -*- coding: utf-8 -*-
"""
第 7 周实验 · 阶段二/三靶场：初版玩家指令判断程序 (mud_engine_v1_buggy.py)
【阶段测试目标】：
1. 跑通 /look、/status、/heal、/help_scholar、/go east 等常规指令；
2. 仅输入单个词 "/go"（忘写方向）复现 IndexError: list index out of range 越界报错；
3. 输入 "/go     west"（中间多敲几个空格）观察 split(" ", 1) 提取出的方向偏差。
"""

from world_data import world, player


# 用 def 把指令判断分支包装起来，方便传入玩家输入的文字并返回结果
def dispatch_command_v1(raw_input):
    """初版指令判断函数（尚未增加移动方向词数检查）"""
    command = raw_input.strip().lower()
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
        # 多条件判断：先检查背包里有没有金创药、当前血量是否已满，再执行服药加血
        if "金创药" not in player["inventory"]:
            return "⚠️ 你的行囊中已经没有【金创药】了！"
        elif player["health"] >= player["max_health"]:
            return "💡 你当前气血充沛，无需服用金创药。"
        else:
            player["inventory"].remove("金创药")
            player["health"] = min(player["max_health"], player["health"] + 20)
            return f"💊 你服下一瓶金创药，气血恢复至 {player['health']}/{player['max_health']}！"

    elif command == "/help_scholar":
        # 价值规则分支：先检查是否在春来茶馆且铜钱足够，再执行赠金助人
        if loc != "chaguan":
            return "💡 当前地点没有需要救助的落魄书生。"
        elif player["gold"] >= 10:
            player["gold"] -= 10
            player["reputation"] += 15
            return f"🤝 你解囊相助落魄书生 10 文铜钱（剩余铜钱: {player['gold']}，江湖声望提升至 {player['reputation']}）！"
        else:
            return "⚠️ 你囊中羞涩（铜钱不足 10 文），只能向书生拱手致歉。"

    elif command.startswith("/go"):
        # 💥 隐患点：默认玩家在 "/go" 后一定输入了空格和方向，直接读取索引 [1]
        direction = command.split(" ", 1)[1]
        if direction in room["exits"]:
            player["location"] = room["exits"][direction]
            new_room = world[player["location"]]
            return f"🏃 你疾步向 [{direction}] 前行，抵达了【{new_room['name']}】。"
        else:
            return f"🧱 那是一堵高耸的青砖石墙，无法向 [{direction}] 前行！"

    else:
        return f"❓ 未知指令：{raw_input}。可用指令：/look, /status, /heal, /help_scholar, /go <方向>"


if __name__ == "__main__":
    loc = player["location"]
    print(f"=== 欢迎来到《侠客行》MUD 初版引擎 (当前位置: 【{world[loc]['name']}】) ===")
    user_cmd = input("请输入指令 (/look, /status, /heal, /go <方向>): ")
    print(dispatch_command_v1(user_cmd))
