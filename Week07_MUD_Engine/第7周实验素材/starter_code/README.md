# 第 7 周上机实验脚手架指南 (`starter_code/`)

本目录提供《人机协同程序设计》**第 7 周实验课（实验 7：逻辑世界建模——文字冒险游戏 MUD 规则构建与分支审查实践）**的分阶段代码靶场与验证基准。

## 📁 目录结构说明

```text
starter_code/
├── 01_stage1_world_model/
│   ├── world_data_buggy.py      # [阶段一靶场] 含 "80" + "20" = "8020" 类型错误的代码审查靶场
│   └── world_data.py            # [阶段一基准] 修正类型后的三房间 world 字典与 player 角色字典
├── 02_stage2_3_router_v1/
│   ├── world_data.py            # 静态世界数据模块
│   └── mud_engine_v1_buggy.py   # [阶段二~四靶场] 支持正常指令但输入 "/go" 会触发 IndexError 崩溃
├── 03_stage4_5_robust_engine/
│   ├── mud_engine_robust.py     # [阶段五终稿] 完成 len(parts) < 2 防呆检查修复与第 4 房间扩建
│   └── test_boundary_audit.py   # [进阶挑战] 5 类非常规输入自动测试脚本
└── Week07_MUD_Engine/           # [学生提交模板] 标准工程工作区目录与 annotated_prompts.md 模板
```

## 🚀 快速验证命令

```bash
# 1. 运行阶段一类型缺陷靶场，观察 "80" + "20" 字符串拼接 Bug
python3 01_stage1_world_model/world_data_buggy.py

# 2. 运行阶段一修正后的世界模型基准
python3 01_stage1_world_model/world_data.py

# 3. 运行阶段五自动测试脚本（一键验证 5 类共 9 项非常规输入）
python3 03_stage4_5_robust_engine/test_boundary_audit.py
```
