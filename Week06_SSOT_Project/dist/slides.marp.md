---
marp: true
theme: default
size: 16:9
paginate: true
math: katex
---

<style>
section {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  padding: 44px 64px;
  background: #ffffff;
  color: #1e293b;
  font-size: 20.5px;
  line-height: 1.72;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  box-sizing: border-box;
}

/* 封面页高阶视觉设计 (Dignified Hero Canvas) */
section.lead {
  background: radial-gradient(circle at 90% 10%, #e0f2fe 0%, #f8fafc 50%, #ffffff 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: stretch;
  gap: 20px;
  padding: 44px 68px;
  box-sizing: border-box;
}

.hero-tag {
  display: inline-block;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 15.5px;
  font-weight: 800;
  padding: 6px 18px;
  border-radius: 20px;
  border: 1.5px solid #bae6fd;
  margin-bottom: 8px;
}

.hero-title {
  font-size: 40px;
  font-weight: 900;
  color: #0f172a;
  line-height: 1.25;
  margin: 0 0 12px 0;
  letter-spacing: -0.02em;
}

.hero-meta {
  display: flex;
  gap: 28px;
  font-size: 18.5px;
  color: #0284c7;
  font-weight: 700;
  margin: 0;
}

.hero-abstract-card {
  background: #ffffff;
  border: 1.5px solid #cbd5e1;
  border-left: 6px solid #0284c7;
  border-radius: 14px;
  padding: 22px 28px;
  box-shadow: 0 8px 24px rgba(15,23,42,0.06);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.hero-abstract-title {
  font-size: 20px;
  font-weight: 800;
  color: #0369a1;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.hero-abstract-card p {
  font-size: 18.5px;
  line-height: 1.75;
  color: #334155;
  margin: 0;
}

.hero-disclaimer-pill {
  background: #fffbeb;
  border: 1.5px solid #fde68a;
  border-left: 6px solid #f59e0b;
  border-radius: 10px;
  padding: 12px 22px;
  font-size: 15.5px;
  color: #92400e;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* 章节标题与徽章 */
h2 {
  font-size: 31px;
  font-weight: 900;
  color: #0f172a;
  border-bottom: 2.5px solid #e2e8f0;
  padding-bottom: 12px;
  margin-top: 0;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.badge {
  display: inline-block;
  background: linear-gradient(135deg, #0284c7, #0369a1);
  color: #ffffff;
  font-size: 15.5px;
  font-weight: 800;
  padding: 5px 14px;
  border-radius: 6px;
  vertical-align: middle;
  margin-right: 14px;
  box-shadow: 0 2px 8px rgba(2, 132, 199, 0.28);
}

/* 通用双栏栅格系统 */
.columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 22px;
  margin-bottom: 14px;
}

/* 通用语义卡片体系 */
.card, .card-blue, .card-green, .card-amber {
  border-radius: 14px;
  padding: 20px 26px;
  box-shadow: 0 6px 18px rgba(15,23,42,0.04);
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 10px;
  height: auto;
  box-sizing: border-box;
  font-size: 20px;
  line-height: 1.72;
  margin-bottom: 18px;
}

.card p, .card-blue p, .card-green p, .card-amber p {
  margin: 0;
}

.card-subtitle {
  font-size: 20.5px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 4px;
}

.card {
  background: #ffffff;
  border: 1.5px solid #e2e8f0;
  border-left: 6px solid #64748b;
}

.card-blue {
  background: #f0f9ff;
  border: 1.5px solid #bae6fd;
  border-left: 6px solid #0284c7;
  box-shadow: 0 6px 18px rgba(2,132,199,0.05);
}

.card-green {
  background: #f0fdf4;
  border: 1.5px solid #bbf7d0;
  border-left: 6px solid #10b981;
  box-shadow: 0 6px 18px rgba(16,185,129,0.05);
}

.card-amber {
  background: #fffbeb;
  border: 1.5px solid #fde68a;
  border-left: 6px solid #f59e0b;
  box-shadow: 0 6px 18px rgba(245,158,11,0.05);
}

p {
  font-size: 20px;
  line-height: 1.75;
  color: #334155;
  margin: 0 0 14px 0;
}

strong {
  color: #0f172a;
  font-weight: 800;
}

ul {
  margin: 0;
  padding-left: 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

li {
  font-size: 19.5px;
  line-height: 1.7;
  color: #334155;
  margin: 0;
}

/* 底部洞察卡片 (Insight Box) */
.insight {
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-left: 6px solid #0284c7;
  border-radius: 12px;
  padding: 16px 24px;
  font-size: 19.5px;
  line-height: 1.65;
  color: #0f172a;
  box-shadow: 0 4px 12px rgba(15,23,42,0.04);
  margin-top: auto;
}

/* 学术三线表优化 */
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 18px;
  margin-top: 4px;
  margin-bottom: 16px;
}
th {
  background: #f8fafc;
  font-weight: 800;
  color: #0f172a;
  padding: 11px 16px;
  border-top: 2.5px solid #0f172a;
  border-bottom: 1.5px solid #0f172a;
  text-align: left;
  font-size: 18.5px;
}
td {
  padding: 10px 16px;
  border-bottom: 1px solid #e2e8f0;
  color: #334155;
}
tr:nth-child(even) td {
  background: #fafafa;
}
tr:last-child td {
  border-bottom: 2.5px solid #0f172a;
}
code {
  font-family: 'SFMono-Regular', Consolas, monospace;
  background: #eff6ff;
  color: #0369a1;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
}
</style>

<!-- _class: lead -->
<div>
  <div class="hero-tag">🌿 单一事实源 (SSOT) 自动化衍生演示</div>
  <h1 class="hero-title">“凌晨一点半综合征”：睡前短视频沉迷机制与大学生断网干预对照实验</h1>
  <div class="hero-meta">
    <span>🎙️ 汇报团队：<strong>NCU《人机协同程序设计》第 6 周实践课</strong></span>
    <span>🏛️ 数据基准：<strong>2026_Campus_Sleep_Intervention (N=80)</strong></span>
    <span>📅 <strong>2026 秋季学期</strong></span>
  </div>
</div>

<div class="hero-abstract-card">
  <div class="hero-abstract-title">🎯 核心导读与研究摘要</div>
  <p>针对高校大学生普遍面临的睡前短视频无意识刷屏、入睡潜伏期延长与次日早八困倦等“凌晨一点半综合征”痛点，本文提出基于 <strong>“灰阶屏幕视觉降噪 + 离床充电物理隔离”的双重行为干预机制</strong>。基于 <code>2026_Campus_Sleep_Intervention</code> 数据集（双组 <span class="math-inline">N=40</span>）的受控对照实验表明：干预组 30 分钟入睡达标率由 <strong>42.5%</strong> 跃升至 <strong>85.0%</strong>（净增 <strong>42.5</strong> 个百分点），平均入睡潜伏耗时由 <strong>46.0 分钟</strong> 压缩至 <strong>14.0 分钟</strong>（缩短 <strong>69.6%</strong>），次日早八困倦发生率由 <strong>72.5%</strong> 骤降至 <strong>7.5%</strong>。</p>
</div>

<div class="hero-disclaimer-pill">
  <span>💡 <strong>一源多端编译声明</strong>：本演示文稿与 A4 研报由 <code>ssot_compiler.py</code> 从同一份纯语义母稿 <code>report.md</code> 确定性衍生。</span>
  <span style="background: #f59e0b; color: #fff; padding: 2px 10px; border-radius: 4px; font-size: 12.5px; font-weight: 700; white-space: nowrap;">SSOT 确定性衍生</span>
</div>

---

## <span class="badge">01</span> 1. 引言：“凌晨一点半综合征”与睡前认知失控困局

<div class="card-blue">

**1.1 现象剖析：报复性熬夜与无限流推荐的多巴胺陷阱**

在智能手机高度渗透高校宿舍生活的当下，大量大学生陷入“明明身体极度疲惫，却在关灯后持续刷短视频至凌晨一点半以后”的睡眠拖延怪圈。行为心理学与神经科学观察表明，这种睡前失控并非单纯的意志力薄弱：高饱和度蓝光屏幕会直接抑制松果体褪黑素分泌，而短视频平台基于强化学习算法构建的“无限下滑（Infinite Scroll）+ 随机可变奖赏”机制，则会持续激活大脑奖赏回路，使学生在睡前陷入时间感知麻痹与认知停不下来的恶性循环。

</div>

<div class="card-green">

**1.2 问题界定：从“意志力自责”走向“环境摩擦力干预”**

要打破“越刷越清醒、越熬越焦虑”的睡眠困局，核心在于放弃低效的单纯口头自律说教，转而通过重构睡前物理与视觉环境来增加成瘾行为的启动阻力。本文聚焦“灰阶屏幕视觉降噪 + 离床两米充电物理隔离”双重干预策略在真实宿舍场景中的有效性，通过双组受控对照实验定量回答两个核心问题：双重环境干预能否显著缩短大学生入睡潜伏期？睡前刺激剥离能否同步降低次日早八课堂的日间困倦率？

</div>

---

## <span class="badge">02</span> 2. 干预机制设计：基于视觉多巴胺剥离与物理摩擦力的双重阻断

<div class="card-blue">

**2.1 灰阶显示模式：剥离高饱和视觉奖赏与蓝光唤醒刺激**

干预方案的第一道防线是在每晚 23:00 自动触发手机系统级“色彩滤镜（灰阶模式）”。从感官加工机理来看，去除高饱和度红黄视觉刺激能够瞬间瓦解短视频画面的多巴胺诱惑力，将原本高唤醒度的娱乐媒介降维为低吸引力的黑白信息流，从而在视觉输入端切断大脑奖赏回路的持续兴奋。

</div>

<div class="card-green">

**2.2 离床物理隔离：重构行为启动摩擦力与睡眠条件反射**

针对躺床后“肌肉记忆式盲摸解锁”的习惯回路，第二道防线强制要求受试者在入睡前将手机放置于距离床铺 2 米以外的书桌充电桩。该设计利用行为经济学中的“摩擦力效应（Friction Effect）”，将伸手即得的零成本微习惯转化为必须掀被下床的高阻力行为，从而重建“床铺仅用于睡眠”的巴甫洛夫条件反射。

</div>

---

## <span class="badge">03</span> 3.1 实验设置与核心睡眠指标基准对比

本研究基于 `2026_Campus_Sleep_Intervention` 校园睡眠干预数据集开展为期 14 天的双组对照实验，将 80 名存在睡前刷屏习惯的在校本科生随机均分为对照组 `G_Control`（维持 **睡前自由刷短视频** 模式，$N = 40$ 人）与干预组 `G_Exp`（执行 **灰阶屏幕+离床隔离** 模式，$N = 40$ 人），通过手环睡眠监测与晨间打卡记录三项核心指标如下表所示：

| 评测组别 | 睡前干预模式 | 样本量 ($N$) | 30分钟入睡达标人数 / 达标率 | 平均入睡潜伏耗时 | 次日早八困倦人数 / 发生率 |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **对照组 (G_Control)** | 睡前自由刷短视频 | 40 人 | 17 人 (**42.5%**) | **46.0 分钟** (2760 秒) | 29 人 (**72.5%**) |
| **干预组 (G_Exp)** | 灰阶屏幕+离床隔离 | 40 人 | 34 人 (**85.0%**) | **14.0 分钟** (840 秒) | 3 人 (**7.5%**) |
| **相对变化幅度** | 双重环境阻断干预 | 样本均衡 | **+42.5 个百分点** | **缩短 69.6%** (-32.0 分钟) | **-65.0 个百分点** |

<div class="insight">📊 <strong>数据洞察</strong>：实测对比数据表明，相对变化幅度在核心维度呈现显著改善：30分钟入睡达标人数 / 达标率 <strong>+42.5 个百分点</strong>，平均入睡潜伏耗时 <strong>缩短 69.6%</strong> (-32.0 分钟)，次日早八困倦人数 / 发生率 <strong>-65.0 个百分点</strong>。</div>

---

## <span class="badge">04</span> 3.2 干预效能对比与行为阻断机理

<div class="card-blue">

* 对比两组实测数据可以发现，干预组的 30 分钟入睡达标率从对照组的 **42.5%** 大幅跃升至 **85.0%**，净增 **42.5 个百分点**。
* 与此同时，干预组学生的平均入睡潜伏耗时从对照组的 **46.0 分钟**（2760 秒）大幅压缩至 **14.0 分钟**（840 秒），降幅高达 **69.6%**（每晚平均净省 **32.0 分钟** 入睡等待时间）。
* 这一显著成效并非源于虚无缥缈的“意志力提升”，而是得益于双重环境干预对睡前成瘾回路的精准物理阻断。

</div>

<div class="card-green">

具体而言，对照组学生在关灯躺床后极易受无限流算法推荐诱惑，陷入“无意识解锁—多巴胺兴奋—褪黑素受抑”的恶性循环；而干预组通过**灰阶显示模式**先行剥离高饱和视觉刺激以降低大脑皮层唤醒度，再配合**离床两米充电**显著抬高二次拿取手机的物理摩擦力，从而在行为启动端阻断了睡前刷屏冲动。这种“视觉降噪 + 物理隔离”的协同机制，在课业压力较大的期末复习周与早八课程前夕展现出了极高的干预稳健性。

</div>

---

## <span class="badge">05</span> 3.3 日间精力恢复效应与早八课堂出勤质量验证

<div class="card-blue">

在评估睡眠干预是否真正转化为日间学习效能的“次日早八困倦发生率”维度上，对照组在 40 名受试者中共有 **29 人**频繁出现晨间嗜睡、注意力涣散或早八迟到现象，困倦发生率高达 **72.5%**；而干预组仅出现 **3 人**轻微晨间疲惫，早八困倦发生率骤降至 **7.5%**，净下降 **65.0 个百分点**。

</div>

<div class="insight">💡 <strong>核心结论与机理验证</strong>：这证实睡前切断高多巴胺信息流不仅延长了总睡眠时长，更显著改善了慢波深睡眠结构与次日清晨的皮质醇唤醒节律。</div>

---

## <span class="badge">06</span> 4. 讨论与结论：校园睡眠干预的边界条件与推广建议

<div class="card-amber">

**4.1 适用边界：戒断初期的 FOMO 反弹与室友协同效应**

尽管双重环境干预展现出显著的促眠效果，但实验访谈也揭示了其现实边界：在干预前 3 天，约四分之一受试者会出现明显的“错失恐惧症（FOMO）”与睡前戒断焦躁，且若同寝室室友仍在公放刷视频，单人干预极易因环境声光干扰而破功。因此在高校推广中，建议以“寝室公约”为单位建立群体协同契约，并辅以白噪音或纸质阅读作为睡前平替过渡。

</div>

<div class="card-green">

**4.2 核心结论与健康数字化作息展望**

综上所述，本研究通过双组受控实验证实：**以“灰阶屏幕视觉降噪 + 离床充电物理隔离”为核心的环境摩擦力干预策略**，能够使大学生 30 分钟入睡达标率翻倍（**42.5% $\rightarrow$ 85.0%**）并将平均入睡潜伏耗时压缩近七成（**缩短 69.6%**）。将该纯语义实验报告接入一源多端编译管线（SSOT），更可一键生成宿舍健康宣讲幻灯片与学工调研简报。

</div>
