# 第 5 周实验：意图造物与 ReAct 闭环编程实验报告

- **学生姓名**：[你的姓名]
- **学号**：[你的学号]
- **所属专业**：[你的学院与专业]
- **实验日期**：2026-09-XX
- **GitHub 作品集主仓库链接**： `https://github.com/[你的 GitHub 用户名]/NCU-Human-AI-Programming`

---

## 一、 实验完成成果概览

* [X] **任务一** ：GitHub 课程主仓库与第 5 周无菌子模块创建
* [X] **任务二** ：单摆物理模拟器 MVP（单文件 Canvas 简谐振动）
* [X] **任务三** ：参数滑块实时交互面板（摆长 / 重力 / 阻尼）
* [X] **任务四** ：控制台报错捕获与 ReAct 自愈修复（ReferenceError 纠偏）
* [ ] **进阶挑战 (选做)** ：双摆混沌模拟器 / 天体场景与 LocalStorage 持久化

---

## 二、 核心灵魂：人机协同三反思

### 1. 意图定义与边界约束反思 (Prompt Engineering)

> **【思考手记 1】** ：在编写初始四段式 Prompt 时，我特意限制了“单文件 index.html 且不依赖任何外部第三方库”。
> **【设计考量】** ：这样设计的核心目的是消除跨域 CDN 加载失败的不可靠因素，确保代码在任何离线电脑上双击即可秒级运行，极大提升了首轮 MVP 的交付确定性。

---

### 2. 报错自愈与证据驱动排错反思 (ReAct Debugging)

> **【思考手记 2】** ：在增加交互控制时，点击重置按钮单摆未能复位初始状态（功能失效），F12 控制台报出 `Uncaught ReferenceError: resetAnimation is not defined` 。
> **【排错心得】**：我没有对 AI 发出盲目的情绪化催促（如“怎么坏了，重写”），而是将控制台具体的函数名与报错行号原样复制给 AI。AI 拿到这一行客观证据后，在数秒内便精准定位了作用域未导出的根因并完成局部修复。这让我深刻体会到“ **证据说话**”在人机协同中的核心力量。

---

### 3. 人机协同哲学与主体性反思 (Human Agency)

> **【思考手记 3】** ：在本次实验中，AI 在 5 秒内帮我完成了上百行 Canvas 绘制与数学物理计算，承担了底层“代码砖瓦工”的角色；
> **【主体性沉淀】**：但我作为人类主导了物理模型的选择、交互界面的视觉标准判定、以及最终控制台是否报错的验收把关。在人机协同时代，人类不可替代的核心价值不在于死记语法细节，而在于 **清晰的意图定义能力、严谨的证据意识与深刻的系统验收能力**。

---

## 三、 Git 敏捷演进提交历史记录 (至少 3 次 Commit)

```bash
* feat: complete pendulum MVP with simple harmonic motion
* feat: add interactive parameter sliders for length, gravity and damping
* fix: resolve reset button runtime error via ReAct loop
```
