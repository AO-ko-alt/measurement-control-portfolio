# -*- coding: utf-8 -*-
"""
第 7 周实验 · 进阶挑战：5 类非常规输入自动测试脚本 (test_boundary_audit.py)
运行方式：python3 test_boundary_audit.py
"""

from mud_engine_robust import dispatch_command_robust, player


def run_boundary_audit():
    test_cases = [
        ("类别 1：前后带空格与大写字母", "   /LOOK   ", "扬州中心广场"),
        ("类别 1：大小写混合带方向移动", "  /Go East ", "春来茶馆"),
        ("类别 2：中间多敲了好几个空格", "/go     west", "扬州中心广场"),
        ("类别 3：只敲 /go 忘写方向", "/go", "请在 /go 后指明方向"),
        ("类别 3：/go 后面只敲了空格", "/go    ", "请在 /go 后指明方向"),
        ("类别 4：输入地图上没有的方向", "/go up", "无法向 [up] 前行"),
        ("类别 5：直接按回车或纯空格", "     ", "尚未输入任何指令"),
        ("类别 5：输入未知的乱码指令", "/fly_to_moon", "无法识别该指令"),
        ("进阶验证：扩建第 4 房间（只改字典不改分支）", "/go north", "白鹿洞书院"),
    ]

    print("=" * 68)
    print("🛡️  Week 07 MUD 指令分支程序 · 5 类边界输入自动测试")
    print("=" * 68)

    player["location"] = "guangchang"
    passed = 0

    for idx, (category, raw_cmd, expected_keyword) in enumerate(test_cases, 1):
        try:
            response = dispatch_command_robust(raw_cmd)
            ok = expected_keyword in response
            status = "✅ PASS" if ok else "❌ FAIL"
            if ok:
                passed += 1
            print(f"[{idx:02d}] {status} | {category}")
            print(f"     输入: {repr(raw_cmd)} -> 输出: {response}")
        except Exception as e:
            print(f"[{idx:02d}] 💥 CRASH | {category} | 抛出未捕获异常: {type(e).__name__}: {e}")

    print("-" * 68)
    print(f"📊 审计汇总：共执行 {len(test_cases)} 项边界用例，通过 {passed}/{len(test_cases)} 项（零未捕获异常崩溃）。")
    print("=" * 68)


if __name__ == "__main__":
    run_boundary_audit()
