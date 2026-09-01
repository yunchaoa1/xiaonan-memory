# 小说改剧本节点交付说明

## 状态

本节点已完成，唯一输出状态为 `SUCCESS`。

- 剧本包：[screenplay.md](D:\Hermes\xiaonan-memory\opc-sim\02_screenplay\screenplay.md)
- 结果记录：[adaptation_result.json](D:\Hermes\xiaonan-memory\opc-sim\02_screenplay\adaptation_result.json)
- 目标时长：约 180 秒
- 场景单元：6
- 严格主要人物：2 名（周野、母亲）
- 台词人物：2 名（周野、母亲）

## 输入冻结

只读取并使用以下上游文件：

1. `D:\Hermes\xiaonan-memory\opc-sim\01_writing\novel.md`
2. `D:\Hermes\xiaonan-memory\opc-sim\01_writing\writing_result.json`

未使用聊天补充、历史、网络、其他项目或候选草稿。未决定下游视频模型。

## 内容覆盖

`screenplay.md` 包含：

- 六个连续场景的时间、地点、人物状态、道具状态与时长
- 可拍摄动作、对白、声音、场景结果和退出状态
- 周野与母亲的连续状态表
- 帆布包、围裙、面粉、旧搪瓷碗、饺子和锅碗等道具流
- 小说行段到场景的双向来源映射、压缩/合并/删除及信息补偿
- 信息持有与揭示顺序、因果链、产能和拍摄约束

## 下游交接

交给 `screenplay-asset-extraction`：从已锁定剧本提取角色、场地、道具、声音和连续性资产。下游必须保留严格两名主要人物、道具状态连续、约三分钟线性结构，不新增事故或反转。
