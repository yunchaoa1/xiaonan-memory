# 利用率体检 · 2026-10-15 基线证据

> 本文是 `knowledge-base-utilization` 的取证记录。**基线数字留着，下次复测用来对比。**

## 一、基线（改动前，2026-10-15）

```
合计 30 个库：写入活跃 11 / 半死 19  →  写入活跃率 37%
```

**14 个库精确停在同一天 `2026-06-30`**（另 2 个停在 07-01/07-07）——
即这批目录是**建立当天写进去的，之后再没人动过** = "建完那天就是最后一天"。

对照组（真活的）：`memory`（每日日志）、`opc-sim/research`、`集团`、`形象档案`（10-15 当天）、`DASHBOARD.md`。
→ 共同点：**都跟"正在做的事"绑定，我干活时必须读它们。**

## 二、atime 对照实验（决定性，别重复踩）

```
① touch -a -d "2026-06-30 10:00" <file>   → 一分钟后再看：已被刷成今天 18:05:07
② 跑体检脚本后                            → 又跳到 18:05:10   ← 测量工具自己擦了数据
③ git status 后                           → 18:05:10（不变）
④ cat 读取后                              → 18:05:10（不变）
```

另：抽样三个**从未读过**的文件，atime 全是"脚本运行那一刻"（18:04:11，同一秒）。
→ **结论：atime 不可用于统计读取；观测行为本身改变观测对象。** 改测 `mtime`（写入）+ 显式「使用日志」（读取）。

脚本：`D:\Hermes\scripts\kb_utilization_check.py`（`--baseline` / `--diff`；**只 stat、绝不 open 内容**）。

## 三、决定性反证：`director-kb`

该库 `2026-06-29` 建立，**自带**：

- 一张带「触发条件」列的路由表：
  `| [[01_故事结构/15节拍表]] | 拿到小说→需要搭剧本骨架时 | 15个故事节拍 |`
- 「入库铁律」：`找不到归属层 → 不急入库，可能是用不上的知识`
- 完整管线图（小说→剧本→分镜→提示词→视频）

**→ 依然 107 天无人碰。**

> **局部索引 ≠ 全局入口。** 索引建在库**里面**，干活时想不起来翻；做得再好也照样烂掉。

同类：`open-source-ai-kb` / `psychology-kb` / `visual-template-library` **都各自有内部索引** —— 全都在半死名单里。

## 四、落地物（2026-10-15）

| 东西 | 路径 |
|---|---|
| 知识库总入口（场景→库 + 30 库清单 + 使用日志） | `D:\Hermes\xiaonan-memory\知识库路由.md` |
| 启动同步挂载（与 DASHBOARD 并列） | `D:\Hermes\SOUL.md` 启动同步段 |
| 活跃度体检脚本 | `D:\Hermes\scripts\kb_utilization_check.py` |
| 总控台记录 | `D:\Hermes\xiaonan-memory\DASHBOARD.md` §十二 |

## 五、社区权威实践（原文摘录）

- **Microsoft Copilot Studio（官方）**：`Always prioritize information from uploaded knowledge sources. Search the knowledge base first before using general knowledge. Cite sources.` / `Add trigger phrases matching your knowledge content` / `Monitor Analytics → knowledge source usage`
- **Agent.ai（官方 best practices）**：`Write for AI, Not Humans` / `Tell the AI exactly when and how to use each tool` / 维护节奏"季度审计、月度查准确性、知识须在 3 个月内更新"
- **InfoWorld「Anatomy of an AI agent knowledge base」**：`maintaining a knowledge base is a lot harder than creating one. To solve this, agents themselves should capture new information and keep the knowledge base up-to-date.`

## 六、这条线上凡哥问过的原话（下次顺着接）

- 「那你觉得我们现在知识库能真正发挥作用吗？」
- 「我现在没搞懂，哪些应该是技能，哪些应该是知识库，然后他们的利用率如何能提高」
- 「可以，吃灰检查我觉得有必要，另外，你觉得这两本书要不要配上那种说话公式？」
- 「小南，你以后回复我的内容都要按照说人话的方式和我交流，太专业的东西我理解起来很困难」
