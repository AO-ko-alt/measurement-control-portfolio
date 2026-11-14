# mre_keyerror.py —— 最小复现案例 (Minimal Reproducible Example, MRE)
world = {
    "guangchang": {"name": "扬州中心广场", "exits": {"east": "market"}},
    "chaguan": {"name": "春来茶馆", "exits": {"west": "guangchang"}}
}
player_location = "guangchang"
direction = "east"
target_id = world[player_location]["exits"][direction]
new_room = world[target_id]  # 运行此脚本可稳定复现 KeyError: 'market'
print(f"抵达：{new_room['name']}")