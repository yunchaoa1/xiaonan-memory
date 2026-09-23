# LangGraph 官方要点摘录（子图 / 持久化）

> 核于 **2026-09-21**，来源为官方文档（Docs by LangChain）。引用结论时以本文件为准，不脑补 API 行为。
> 原文：
> - https://docs.langchain.com/oss/python/langgraph/use-subgraphs （使用子图）
> - https://docs.langchain.com/oss/python/langgraph/persistence （持久化）

## 1. 子图是什么

- 官方定义：**a subgraph is a graph that is used as a node in another graph**（子图＝被当成"一个节点"用的另一张图）。
- 官方列的用途三类：
  1. **构建多 agent 系统**（multi-agent systems）；
  2. 在多张图里**复用**同一组节点；
  3. **分团队并行开发**：各部分各自定义成子图，**只要遵守子图的输入/输出 schema 接口，父图不需要知道子图内部任何细节**。

## 2. 父子通信的两种模式（官方原表）

| 模式 | 何时用 | 状态结构 |
|---|---|---|
| **在节点里调用子图**（wrapper 函数） | 父子**不同**状态结构（**没有共享键**），或需要在中间做转换 | 自己写转换：父状态 → 子图输入；子图输出 → 父状态 |
| **子图直接 add_node** | 父子**共享状态键**（子图读写与父图同一批通道） | 直接把 compiled subgraph 传进去，不需要 wrapper |

- 官方注释（多层示例）：**"NOTE: child or parent keys will not be accessible here"** —— 各层之间的状态键**互不可见**（这正是"上下文隔离"的机制来源）。
- 支持**多层嵌套**：parent → child → grandchild。

## 3. 持久化 / 检查点（关键坑在这）

- **checkpointer**：把线程的图状态按步存成检查点（checkpoint）。用途：会话连续性、**human-in-the-loop**、time travel、**容错**。
- **Store**：在图状态**之外**存应用自定义数据，用于**跨线程长期记忆**（用户偏好、事实、共享知识）。
- **有状态子图会继承父图的 checkpointer**（`compile(checkpointer=True)` 或父图统一 compile 时管）；两种有状态模式：
  - **per-invocation（默认，官方推荐）** —— 适合多数应用，**包括"把子代理当工具调用"的多 agent 系统**：支持 interrupts / 持久化 / 并行调用，且每次调用相互隔离；
  - **persistent** —— 状态保留更久。
- ⚠ **坑（官方"Persistence"页明写）**：
  > "When a subgraph updates state, the parent graph may not see the changes immediately. This is because **each subgraph manages its own checkpoint namespace**. Fix: **Use shared state via Store** for data that needs to cross graph boundaries, **or configure your subgraph to write to the parent checkpoint**."
  - 编译：子图更新状态 → **父图可能看不到**（不是立即同步）→ 表现为"父图以为拿到了，其实是旧的/空的"。
  - 两个解法：① 用 **Store** 传跨图数据；② 配置**子图直接写父图检查点**。

## 4. 对我们（影剧工坊）的映射

- "上下文超出 → 情节崩塌 / 内容短缺" 的工程解法 = **子图隔离 + 结构化交接 + 投影落盘 + 交接校验边**（见 SKILL.md 第二节）。
- **优先验第一条**：父子**状态可见性**（上一条坑）——它最像"交接内容短缺"的直接成因。
- 排查动作建议：① 打开每步 state 的落盘/日志，核对"父图实际拿到什么"；② 交接处加校验（字段缺失/长度异常 → 重跑或告警）；③ 先用**一集剧本**跑通"剧本→分镜→生图"三段子图，再扩到全链。
