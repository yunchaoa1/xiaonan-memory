# H3 提示词 · OPC 节点契约（原 minimax-h3-shot-prompt 的职责/边界部分，完整保留）

> 只有在走 OPC 流水线（闭包包 → 编译 → 交付执行）时才需要读本文件。日常写提示词不用看。

## Purpose（用途）

把一个已批准的 OPC 镜头编译成一条 MiniMax H3 逐镜提示词 + 资产绑定包。本节点只编译已批准的决策：不写故事、不改剧本、不设计镜头、不做资产、不跑模型、不判片。有项目锁定风格时用锁定风格；给了多视图角色/场景主体表就用主体表。

## Input Boundary（输入边界）

只读一个闭合、带版本的镜头包 + 其已批准的来源记录 + 锁定的资产引用 + 选定的方言规则。不读聊天补充、不读历史、不读网页、不读未登记文件、不读其他项目、不读密钥。

必填输入：
- 镜头 ID、schema/版本、来源 ID 与哈希
- 已批准的动作、运镜意图、时长与模式
- 首/中/尾状态与连续性
- 台词与音频事件
- 有序资产引用（ID、版本/状态、角色、URI/路径、哈希、批准/锁定状态）
- 恰好一个方言与适配器版本

输入以这一份闭合包为唯一来源；不修补相邻镜头、不发明事实。

## Responsibility Boundary（职责边界）

上游拥有故事事实、剧本、资产提取、镜头时长、镜头方案、声音意图、状态转移；本节点只保留并编译。
执行方拥有凭证、排队、模型调用、重试、下载、任务状态、成本。QC 方检查真实媒体。**提交成功 ≠ 视频成功。**

## Four Dialects（四种方言）

### MiniMax Cloud API
编译已批准的请求形态：镜头 ID、提示词版本、模式、时长、有序条件、显式参数。鉴权/提交/轮询/下载归执行方。

### ComfyUI Partner Nodes
为锁定的 Partner 模板编译 API 格式图输入。OPC 资产 ID、版本、哈希、血缘保留在 URI/槽位映射旁。槽位顺序只是传输层，永远不是身份。

### ComfyUI Native Nodes
为锁定的本地 H3 T2V / I2V / FLF2V / R2V 图编译输入。绑定带类型的图像/视频/音频条件，不猜模型路径、采样器、分辨率、fps 或音频行为。

### AIMixer Director
编译外部分组、分段、素材顺序、共享提示词字段。OPC 镜头与资产身份保留在 Director 编号之外。Director 报告是执行遥测，不是 OPC 真相。

## Output Contract（输出契约）

一份完整编译包（本节点只产出编译结果）：

- status `SUCCESS`
- 包与提示词 schema 版本
- 镜头/来源 ID 与哈希
- 选定方言与适配器版本
- 编译后的提示词、语言、模式、时长
- 首/中/尾状态时间线
- 有序资产绑定（ID、版本/状态、角色、哈希、传输映射）
- 未改动的台词/音频结构
- 执行方交接单
- `execution_status: NOT_RUN`

不声称已渲染视频、已做运行时 QC 或已获人工验收——执行与验收属节点外环节。

## 编译前提（输入事实，只读、只编译、不判定不阻断）

1. 镜头与来源的版本、批准、哈希、闭合边界
2. 时长、模式、动作、运镜意图、状态时间线、台词、音频、连续性
3. 每个可见主体/场景/道具/群组/能力的已批准锁定绑定
4. 资产 ID、版本/状态、哈希、角色、顺序、血缘
5. prompt 不新增未批准事实、不遗漏必需事实
6. 恰好一个受支持的方言与适配器版本
7. URI/槽位映射保留 OPC 身份，不依赖槽位次序
8. 输出完整、`execution_status: NOT_RUN`、不声称媒体验收

## 参考样例（历史三镜包，写法对照，非门禁）

- `D:\Hermes\xiaonan-memory\opc-mvp\05_h3_prompt_package\h3_prompt_package.json`
- `D:\Hermes\xiaonan-memory\opc-mvp\03_storyboard_timeline\opc_shots.json`
- `D:\Hermes\xiaonan-memory\references\reuse-scout\video-pipeline-reuse-scout-v0.1.md`

该样例含三镜、四个方言声明、`selected_dialect: aimixer_director`。
