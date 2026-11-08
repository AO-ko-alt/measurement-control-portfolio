# -*- coding: utf-8 -*-
"""
第 7 周实验 · 阶段二/三：玩家指令判断脚本 (mud_engine_v1.py)

职责分工：
- world_data.py 只存放数据（world 地图 + player 档案）
- 本文件只负责"指令判断 + 状态更新"，所有房间信息都从字典里查，不写死具体房间名
"""

from world_data import world, player


def dispatch_command(raw_input):
    """接收玩家原始输入，返回本次指令的执行结果文字。"""
    # ① 清理输入格式：去掉首尾多余空格，并统一转为小写
    command = raw_input.strip().lower()

    if not command:
        return "少侠尚未输入指令。可用指令：/look、/status、/go <方向>。"

    # ② 每次都从 player 重新取当前位置，再到 world 里查对应房间
    room = world[player["location"]]

    # ③ 用 if-elif-else 做多路分支判断
    if command == "/look":
        exits_str = "、".join(room["exits"].keys())
        return (f"【{room['name']}】\n"
                f"{room['description']}\n"
                f"可用出口：{exits_str}")

    elif command == "/status":
        items = "、".join(player["inventory"]) if player["inventory"] else "（空）"
        return (f"【角色状态】{player['name']} | 生命：{player['health']}/{player['max_health']} "
                f"| 铜钱：{player['gold']} | 声望：{player['reputation']} | 背包：{items}")

    elif command.startswith("/go"):
        # split() 不带参数：自动把中间连续多个空格合并切开
        parts = command.split()
        # 只输入 "/go" 时没有方向词，先给出提示，避免取 parts[1] 越界
        if len(parts) < 2:
            return "少侠欲往何方？请在 /go 后指明方向，例如：/go east。"

        direction = parts[1]

        # 先查当前房间的出口字典，确认这个方向有没有路
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
                f"可用指令：/look、/status、/go <方向>。")


if __name__ == "__main__":
    print("=== 欢迎来到《侠客行》MUD（输入 /quit 退出）===")
    print(dispatch_command("/look"))
    while True:
        raw = input("\n请输入指令：")
        if raw.strip().lower() == "/quit":
            print("后会有期！")
            break
        print(dispatch_command(raw))
