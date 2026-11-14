# -*- coding: utf-8 -*-
"""
第 8 周实验 · 防御式编程终稿：mud_engine_defensive.py

由 mud_loop_v2.py（循环 + for 遍历）与 mud_chaos_buggy.py（混沌靶场）合入修复而来：
1. 状态前置：world / player 定义在 while True 外部，位置跨回合持久；
2. for 循环渲染地面物品、出口中文导航与带序号的行囊；
3. 方案 B 防御式寻路护栏：广场 east 恢复为 "chaguan"，保留测试出口
   north -> "market_unbuilt"；/go 分支在读取 world[target_id] 前先做
   `if target_id in world:`，未开放区域给友好提示并留在原地，绝不 KeyError 闪退；
4. /buy_tea 修复算术错误：在茶馆且铜钱 >= 15 时用减法扣 15 文（50 -> 35），
   已清除全部临时 [DEBUG] 探针。
"""

world = {
    "guangchang": {
        "name": "扬州中心广场",
        "description": "宽阔的青石板广场，中央立着千年古槐。",
        # east 已恢复正常；north 指向尚未开放的区域，用于验证防御式护栏
        "exits": {"east": "chaguan", "west": "wuguan", "north": "market_unbuilt"},
        "items": ["生锈的铁剑", "神秘的卷轴"]
    },
    "chaguan": {
        "name": "春来茶馆",
        "description": "茶香四溢，说书先生正拍案惊堂。",
        "exits": {"west": "guangchang"},
        "items": ["粗瓷茶碗", "碧螺春茶叶"]
    },
    "wuguan": {
        "name": "振远武馆",
        "description": "院内刀枪整齐排列，弟子们正挥汗操练。",
        "exits": {"east": "guangchang"},
        "items": ["木制练功桩"]
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


def render_current_room(world, room_id):
    """用 for 循环渲染房间：场景 + 地面物品 + 带中文目标名的出口导航。"""
    room = world[room_id]
    lines = [f"📍 【{room['name']}】{room['description']}"]
    for item in room["items"]:
        lines.append(f"  📦 [地面物品] 你发现地上有：【{item}】")
    for d, tid in room["exits"].items():
        # 出口可能指向未开放房间，显示时同样设防，避免 /look 崩溃
        target_name = world[tid]["name"] if tid in world else f"未开放迷雾区({tid})"
        lines.append(f"  🧭 [此地出口] {d} -> 通往【{target_name}】")
    return "\n".join(lines)


def process_command(raw_input, world=world, player=player):
    """处理单轮指令，返回 (response_text, should_quit)。

    默认参数在定义时绑定模块级 world/player；回归测试可注入深拷贝字典而不污染全局状态。
    """
    command = raw_input.strip().lower()

    if not command:
        return "⚠️ 请输入有效指令（如 /look, /bag, /buy_tea, /go east, /quit）。", False

    if command == "/quit":
        return "👋 少侠收剑入鞘，江湖路远，后会有期！（主引擎已安全退出）", True

    if command == "/look":
        return render_current_room(world, player["location"]), False

    if command == "/bag":
        lines = [f"🎒 【{player['name']}的行囊】（铜钱：{player['gold']} 文）："]
        for idx, item in enumerate(player["inventory"], 1):
            lines.append(f"  [{idx}] {item}")
        return "\n".join(lines), False

    if command == "/buy_tea":
        tea_price = 15
        if player["location"] != "chaguan":
            return "⚠️ 只有【春来茶馆】才售卖碧螺春茶！", False
        if player["gold"] >= 15:
            # 修复静默算术漏洞：双重负号已改为正常减法
            player["gold"] = player["gold"] - 15
            player["inventory"].append("碧螺春新茶")
            return f"🍵 购买成功！扣除 {tea_price} 文，剩余铜钱：{player['gold']} 文。", False
        return "⚠️ 囊中羞涩，铜钱不足 15 文！", False

    if command == "/status":
        items = "、".join(player["inventory"])
        return (
            f"【角色状态】{player['name']} | 生命: {player['health']}/{player['max_health']} "
            f"| 铜钱: {player['gold']} 文 | 声望: {player['reputation']} | 背包: [{items}]"
        ), False

    if command == "/heal":
        if "金创药" not in player["inventory"]:
            return "⚠️ 你的行囊中已经没有【金创药】了！", False
        if player["health"] >= player["max_health"]:
            return "💡 你当前气血充沛，无需服用金创药。", False
        player["inventory"].remove("金创药")
        player["health"] = min(player["max_health"], player["health"] + 20)
        return f"💊 气血恢复至 {player['health']}/{player['max_health']}。", False

    if command == "/help_scholar":
        if player["location"] != "chaguan":
            return "💡 当前地点没有需要救助的落魄书生。", False
        if player["gold"] < 10:
            return "⚠️ 你囊中羞涩（铜钱不足 10 文），只能向书生拱手致歉。", False
        player["gold"] -= 10
        player["reputation"] += 15
        return f"🤝 解囊相助 10 文，江湖声望提升至 {player['reputation']}。", False

    if command.startswith("/go"):
        parts = command.split()  # 不带参数，合并连续空格
        if len(parts) < 2:
            return "⚠️ 少侠欲往何方？请在 /go 后指明方向（如 /go east）！", False

        direction = parts[1]
        exits = world[player["location"]]["exits"]
        if direction not in exits:
            return f"🧱 那是一堵高耸的青砖石墙，无法向 [{direction}] 前行！", False

        target_id = exits[direction]
        # 🛡️ 防御式护栏：读取 world[target_id] 之前先核验键是否存在
        if target_id in world:
            new_room = world[target_id]
            player["location"] = target_id
            return (
                f"🏃 你施展轻功向 [{direction}] 迈步，抵达了【{new_room['name']}】！\n"
                + render_current_room(world, target_id)
            ), False
        # 目标房间未开放：不改写 player["location"]，留在原地且主循环继续
        return f"🛡 [系统提示] 前方区域尚未开放，请留步！（系统防御拦截：{target_id}）", False

    return "❓ 此言未解。可用指令：/look、/bag、/buy_tea、/status、/heal、/help_scholar、/go <方向>、/quit", False


if __name__ == "__main__":
    # 【循环外】冷启动开场白：整个程序只打印一次
    print("=== 欢迎踏入《侠客行》防御加固版引擎（输入 /quit 退出）===")
    print(render_current_room(world, player["location"]))

    while True:
        try:
            # 去掉终端/管道输入可能附带的 BOM，保证首条指令也能被识别
            raw = input("\n少侠请下令 > ").lstrip("\ufeff")
        except (EOFError, KeyboardInterrupt):
            print("👋 少侠收剑入鞘，江湖路远，后会有期！（主引擎已安全退出）")
            break

        reply, should_quit = process_command(raw)
        print(reply)
        # 【安全退出分支】打印告别语后立即终止循环
        if should_quit:
            break
