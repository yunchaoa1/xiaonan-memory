# 一张卡怎么分给两个人用：MIG 与显存切分（2026-10-21 核）

> 起因：小李提出「显存隔离，把一张卡分给两个人用，真正做到一卡 2 并发」，凡哥判断「**这个很重要**」。
> 本文回答三件事：**技术上能不能做 / 做了产能涨不涨 / 现场怎么测**。

## 一、先分清「一卡多用」的四条路，别混着说

「显存隔离」这个词对应四种完全不同的技术，能力和代价差很远：

| 路线 | 隔离程度 | 需要什么 | 产能能翻倍吗 |
|---|---|---|---|
| **MIG**（多实例 GPU） | **硬件级真隔离**：独立显存、缓存、计算核心、独立 QoS | 卡必须支持 + **Linux** 驱动 + root 配置 | **不能**（带宽被切，见第三节） |
| **时间分片**（time-slicing） | 无隔离，任务轮流占用整卡 | 驱动默认支持 | 不能，只是排队更细 |
| **多实例共存**（同卡跑多个模型进程） | 显存不隔离，靠 `CUDA_VISIBLE_DEVICES` + 显存够 | 显存装得下就行 | **有可能**，取决于单实例是否吃满硬件 |
| **vGPU**（虚拟化） | 虚拟机级隔离 | NVIDIA vGPU license + 数据中心卡 | 不能 |

⚠️ **小李说的「显存隔离」如果指的是「把一张卡分成两块、谁也看不见谁」，那只有 MIG 或 vGPU 能做到。** 只是「两个进程共用一张卡、显存够就行」不算隔离——一个进程 OOM 会连累另一个。

## 二、MIG 官方支持情况（原文摘录）

**NVIDIA 官网 · RTX PRO 6000 Blackwell Max-Q Workstation Edition**：

> Multi-Instance GPU (MIG) expands the performance and value of RTX PRO 6000 Max-Q by enabling the creation of **up to four fully isolated instances**. Each MIG instance has its **own high-bandwidth memory, cache, and compute cores** as well as **guaranteed quality of service (QoS)**, extending the reach of accelerated computing resources to every user.

**丽台（Leadtek，NVIDIA 官方代理）产品页**：

> RTX PRO 6000 Blackwell Max-Q GPUs includes multi-instance GPU (MIG) virtualization and GPU partitioning capability. When configured for MIG operation, RTX PRO 6000 delivers **up to 4 GPU instances**. Robust fault isolation allows partitioning RTX PRO 6000 GPUs safely and securely.

**NVIDIA MIG 技术总页**：

> NVIDIA Blackwell and Hopper GPUs support MIG with multi-tenant, multi-user configurations in virtualized environments across **up to seven GPU instances**.

→ **Hopper 数据中心卡（H100/H200）最多 7 片；RTX PRO 6000 最多 4 片。**

### 三个未确认的点（采购前必须问供应商或现场验）

1. **6000D 特供版是否保留 MIG** —— 官方文档只提 Max-Q / Workstation；特供版（84G）是另一条产品线，**功能可能被裁剪，没有任何公开资料敢确认**
   - ⚠️ **但新出的 RTX PRO 5500（2026-09 上线）官方明确写了「MIG: 1×84GB or 2×42GB」**——同样 84G 显存，同样只能切两片各 42G，**跑 H3 一样装不下**。这条把「84G 能不能切」变成确定答案，但答案对 H3 不利。
2. **Windows 下能不能配 MIG** —— MIG 配置工具（`nvidia-smi mig`）主要在 Linux；Windows 支持有限甚至没有。**ComfyUI 我们跑在 Windows 上，这条不通则方案作废**
3. **Max-Q 的功率限制** —— Max-Q 是 300W 版本，切 4 片后每片算力很低；Workstation 600W 版切分余量更大

## 三、为什么切了产能也不翻倍（核心原理）

MIG 切的是**整套资源**，不只是显存地址空间：

- 显存容量 → 按片分（96G ÷ 2 = 48G/片）
- **显存带宽 → 按片分（1.79 TB/s ÷ 2 ≈ 896 GB/s/片）**
- **计算核心（SM）→ 按片分**
- 每片有独立 QoS 保证，不互相抢

视频生成（H3 这类扩散模型）是**显存带宽密集型**任务。带宽砍半 → 出片时间接近翻倍。

| 场景 | 单实例 | 双实例（MIG） |
|---|---|---|
| 每实例分到带宽 | 1792 GB/s | ≈896 GB/s |
| 一集耗时 | 20 分钟 | **40 分钟** |
| 同时能接 | 1 单 | **2 单** |
| **1 小时总产量** | **3 集** | **3 集** |
| 客户感受 | 不用等 | **要等一倍时间** |

→ **本质：把「排队」换成了「各自慢一倍」。总产量不变。**

### 唯一可能真赚的条件

如果单实例跑 H3 时**吃不满硬件**（模型加载、IO 等待、CPU 预处理、VAE 解码等阶段 GPU 空转），那么第二个实例能填进这些空隙，**总产量可能接近翻倍**。

这种情况在真实生产里并不罕见——尤其是：
- 全自动流水线里前后处理占比高
- 分辨率/时长较短的镜头（前面 5090 实测：6 秒段效率是 15 秒段的 2.7 倍，说明短任务的空闲占比可能更高）

**但这个只能实测，任何纸面推算都不作数。**

## 四、四种卡的显存切分余量（H3 = 40G 量化权重）

| 卡 | 总显存 | 切 2 片 | 每片余量 | 判定 |
|---|---|---|---|---|
| **RTX PRO 6000（96G）** | 96G | 48G | +8G | ✅ 能跑，余量偏紧 |
| **RTX 6000D（84G）** | 84G | 42G | **+2G** | ⚠️ **大概率装不下**（运行时 + KV + 激活就要几 G） |
| **RTX PRO 5500（84G，新）** | 84G | 42G（官方口径） | **+2G** | ⚠️ **同样装不下**，跟 6000D 一个坑 |
| **H100（80G）** | 80G | 40G | 0 | ❌ 正好卡死 |
| **H200（141G）** | 141G | 70G | +30G | ✅ 宽松，还能切 3 片（47G/片） |

**结论**：想靠 MIG 一卡双跑 H3，**至少得是 96G 起步**；84G 特供版基本没戏，除非模型量化更激进或能压到 35G 以下。

## 五、现场实测四步（拿到这三个数就能定性）

**准备**：同一台机器、同一份 H3 模型、同一组提示词、同一时长（建议 6 秒段，效率最高）、关掉抽卡。

**第一步 · 单实例基准**
- 一张卡，跑 1 个实例，连续出片 **1 小时**（不要只跑一个就停，要看持续吞吐）
- 记录：总出片集数 → **A**；单集平均耗时；显存峰值占用

**第二步 · 双实例**
- 同一张卡配 MIG 切 2 片（若配不了，改用两个进程共卡）
- 每片跑 1 个实例，**同时**连续跑 1 小时
- 记录：两片总出片集数 → **B**；每片单集耗时；每片显存峰值

**第三步 · 判读**

| 结果 | 含义 | 决策 |
|---|---|---|
| **B ≈ 2A** | 单实例确实吃不满硬件 | **赚大了**，卡数可省近一半 |
| **B ≈ A** | 带宽是硬瓶颈 | 不赚，只是不用排队；**按原计划买卡** |
| **B < A** | 切分开销吃掉性能 | 亏，别用 |

**第四步 · 单独验 6000D**
- 6000D 那 42G 到底装不装得下 40G 模型 + 运行时
- 装不下就到此为止，不用再测后面的

**附加记录（写进测试表，以后议价用）**：显存峰值、GPU 利用率曲线、是否出现 OOM、切分后重启/重配是否要清空任务。

## 六、报价话术（给领导）

> 「一张卡分两个人用，技术上英伟达官方支持。但**分开的是整张卡的能力，不只是内存**——好比一条八车道公路划成两条四车道，能同时跑两辆车，可每条路都变窄，车全慢一半。**一小时总共运的货还是一样多。**
>
> 所以它解决的是『客户要不要排队』，不是『机器够不够用』。**要想机器少买一半，必须现场测出『两个人一起跑，产量真能接近翻倍』这个结果——测不出来，就得按原计划买。**」

## 出处

- NVIDIA 官网 · RTX PRO 6000 Blackwell Max-Q Workstation Edition（MIG 段落，2026-10 查）
- Leadtek 丽台 · RTX PRO 6000 Blackwell Max-Q 产品页（MIG virtualization，2026-10 查）
- NVIDIA · Multi-Instance GPU 技术页（Blackwell/Hopper 最多 7 实例）
- H3 量化权重体量：见 `语言与视频模型部署门槛.md`
- 5090 实测出片时间（6 秒段 vs 15 秒段）：见主 SKILL.md「出片时间不能按秒数线性叠加」
