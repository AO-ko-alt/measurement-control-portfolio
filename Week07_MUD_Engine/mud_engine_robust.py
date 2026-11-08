# -*- coding: utf-8 -*-
"""
第 7 周实验 · 阶段五：防御加固版指令判断脚本 (mud_engine_robust.py)
在 v1 基础上修复两类边界崩溃：
1. 空输入检查：玩家直接按回车时给出提示，不往下执行；
2. 不带参数的 split()：自动把 "/go    east" 中间多敲的连续空格合并切开；
3. 先检查词数 (len(parts) < 2)：防止只输入 "/go" 忘写方向引发 IndexError 崩溃；
4. 检查出口字典 (direction in room["exits"])：防止输入不存在的方向引发 KeyError。
"""

from world_data import world, player


def dispatch_command_robust(raw_input):
    """接收玩家原始输入，返回本次指令的执行结果文字。"""
    # ① 清理输入格式：去掉首尾多余空格并统一小写
    command = raw_input.strip().lower()

    # ② 空输入检查：玩家直接按回车，给出提示后不再往下执行
    if not command:
        return "请输入指令。（可用：/look、/status、/heal、/help_scholar、/go <方向>）"

    # ③ 每次都从 player 重新取当前位置，再到 world 里查对应房间
    room = world[player["location"]]

    # ④ 用 if-elif-else 做多路分支判断
    if command == "/look":
        exits_str = "、".join(room["exits"].keys())
        return (f"【{room['name']}】\n"
                f"{room['description']}\n"
                f"可用出口：{exits_str}")

    elif command == "/status":
        items = "、".join(player["inventory"]) if player["inventory"] else "（空）"
        return (f"【角色状态】{player['name']} | 生命：{player['health']}/{player['max_health']} "
                f"| 铜钱：{player['gold']} | 声望：{player['reputation']} | 背包：{items}")

    elif command == "/heal":
        # 先检查最具体的限制条件：背包里有没有金创药
        if "金创药" not in player["inventory"]:
            return "你行囊中没有【金创药】，无法服药疗伤。"
        # 再检查当前血量是否已经满值
        if player["health"] >= player["max_health"]:
            return "你当前气血充沛，无需服用金创药。"
        # 两个条件都满足，才执行服药回血（最高不超过 max_health）
        player["inventory"].remove("金创药")
        player["health"] = min(player["max_health"], player["health"] + 20)
        return (f"你服下一瓶金创药，气血恢复至 {player['health']}/{player['max_health']}。"
                f"（剩余金创药：{player['inventory'].count('金创药')}）")

    elif command == "/help_scholar":
        # 先检查最具体的限制条件：玩家是否就在春来茶馆
        if player["location"] != "chaguan":
            return "当前地点没有需要救助的落魄书生。"
        # 再检查铜钱是否足够
        if player["gold"] < 10:
            return "你囊中羞涩（铜钱不足 10 文），只能向书生拱手致歉。"
        # 两个条件都满足，才扣钱加声望
        player["gold"] -= 10
        player["reputation"] += 15
        return (f"你解囊相助落魄书生 10 文铜钱（剩余铜钱：{player['gold']}，"
                f"江湖声望提升至 {player['reputation']}）。")

    elif command.startswith("/go"):
        # ⑤ 不带参数的 split()：自动把中间多敲的连续空格合并切开
        parts = command.split()
        # ⑥ 先检查词数够不够 2 个，防止只输 "/go" 时取 parts[1] 触发 IndexError
        if len(parts) < 2:
            return "请在 /go 后指明方向（例如：/go east）。"

        direction = parts[1]

        # ⑦ 检查当前房间有没有这个方向的出口，防止 KeyError
        if direction in room["exits"]:
            # 出口字典的值就是目标房间代号，取出来直接更新玩家位置
            player["location"] = room["exits"][direction]
            new_room = world[player["location"]]
            return f"你向 [{direction}] 前行，抵达【{new_room['name']}】。{new_room['description']}"
        else:
            exits_str = "、".join(room["exits"].keys())
            return (f"抱歉，[{direction}] 方向没有路，暂时无法通行。"
                    f"（当前可用出口：{exits_str}）")

    else:
        return (f"无法识别的指令：{raw_input.strip()}。"
                f"可用指令：/look、/status、/heal、/help_scholar、/go <方向>。")


if __name__ == "__main__":
    print("=== 欢迎来到《侠客行》MUD 防御加固版（输入 /quit 退出）===")
    while True:
        raw = input("\n请输入指令：")
        if raw.strip().lower() == "/quit":
            print("后会有期！")
            break
        print(dispatch_command_robust(raw))
