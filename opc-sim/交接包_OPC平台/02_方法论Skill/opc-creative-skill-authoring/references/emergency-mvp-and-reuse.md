# OPC 紧急 MVP 与成熟底座复用经验

## 适用场景

用户要求在一个工作日内拿到可测试版本，同时完整生产链仍有媒体API、权限或全量回归未闭合。

## 最小可测结构

1. 固定两条链：写作首次可用交付；固定小说进入生产链。
2. 每个节点只交一个小而完整样本：一个完整场景或三镜，不先扩全批次。
3. 产物必须机器可读并可验证：JSON解析、Fountain解析、OTIO写入回读、状态枚举互斥。
4. 媒体模型未执行时必须写 `NOT_RUN`；缺key/额度/权限时写 `MODEL_BLOCKED`，同时保留完整request manifest。
5. 独立verifier在总包前核对文件矩阵、关键字段、执行记录和越权声明。

## 已验证复用方向

- Fountain 1.1＋screenplay-tools：中文使用强制标记；实际解析后再归一化为OPC AST。
- OpenTimelineIO：负责帧率、时长和镜头时间线；OPC字段放在版本化metadata中。
- Kitsu式实体关系可借鉴，但OPC自己持有状态真源。
- GPT Image：官方API适配层＋内容寻址资产库＋OPC provenance/QC/lock。
- MiniMax H3：官方/Comfy模板作为图结构，AIMixer Director仅作执行适配器；OPC持有素材UUID、prompt版本、任务状态和QC。

## Provider隔离

媒体API与聊天Provider分开：独立密钥作用域、endpoint、模型ID和输出目录。第三方OpenAI兼容聊天endpoint未通过图像endpoint烟测时，不得默认兼容GPT Image。首次只做一张最低成本、低质量烟测，成功后再批量。

## 截断恢复

代理批次超时或返回503/524时：

1. 建目标文件矩阵；
2. 逐项查存在性；
3. 回读完整项及真实测试证据；
4. 仅重派缺失项；
5. 把任务收缩到单文件/单场/三镜；
6. 不让`completed`摘要替代产物。
