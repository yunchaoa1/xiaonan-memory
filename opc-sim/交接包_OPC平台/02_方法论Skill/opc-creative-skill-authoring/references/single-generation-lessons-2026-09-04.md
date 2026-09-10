# 2026-09-04 单一生成形态实战教训（凡哥血泪）

## 实战背景

《饺子出锅前》OPC 链路从小说拆剧本起全链路重跑，凡哥当天对节点 Skill 形态提出三次架构纠正，全部沉淀为规则。

## 一、节点 Skill 单一生成形态

- 凡哥原话：「节点skill增加检查有什么意义？这个skill只是驱动大模型执行的规则，他们没有第二次机会，第二次修改机会只是留给客户的……节点里的skill的任务只是完成生成的使命。」
- 「OPC平台是没有另外一个skill去约束节点工作的，节点只是一个全新的，除了本节点的skill没有任何约束规则，所以把重点要放到opc的skill上……不要再形成新的skill去增加规则，没有任何意义。」
- 实战案例：主体资产节点在家场景图上自检后反复重试 8 次（28 次 API 调用、19 分钟）——根因是 Skill 边界段有 "does not interview/self-check/retry..." 的否定列举，模型读到检查概念就执行自检。
- 修复：清除全部检查形态词（Boundary/Prompt Rules/Output/回归段/One-Shot 五处），改写为纯生成描述。

## 二、改 Skill → 同回合重跑（原子动作）

- 凡哥三次连问「只要节点skill做出更新改变，下一步要干嘛？」——答案永远是用新 Skill 重跑验证。
- 执行纪律：patch 完成与派重跑必须在同一回合内完成，中间不插任何动作；修订前启动的运行不算数。
- 我当天至少两次改完 Skill 忘记立刻重跑，被凡哥抓包。

## 三、资产提取新标准（2026-09-04 定稿，已入 screenplay-asset-extraction 节点 Skill）

1. **Worn-Item Prop Standard**：穿戴物归类看源文动作——有摘/脱/换/转移=道具（holder 链+状态链）；始终穿戴=形象一部分（wardrobe）。例：周野帽子（摘下）=道具；母亲围裙（始终系着）=形象 NOT_A_PROP。
2. **State-Version Reference Standard + 配饰边界**：换装/受伤=独立完整人物版本图（禁部件拼贴）；**可摘脱配饰（帽/围巾/眼镜/手包）永远不触发人物版本图**——人物图始终无配饰基线，佩戴态=人物图+道具图在下游组合绑定。凡哥纠偏原话：「有了帽子道具，为什么还要周野戴帽的四格呢？skill驱使你这么干的吗？」
3. **Prop Three-Element Rule（道具三要素）**：凡哥观察规律——小说里的道具必有作用/出处/落幕三要素。提取时逐项核对：齐=全提取；缺=写「源文未交代」+裁定行（不脑补）；全缺=不算道具（降陈设）。
4. **Location Merging Rule（场景合并）**：连通性+叙事同一性判定——同一住宅连通空间（玄关/客厅/厨房/餐厅）=一个 location_master（一张图）；独立隔离空间（楼道）=单独。目的：少一个参考对象、少一道工序。
5. **Source-Clue Alignment（门禁 11）**：客户补充设定 vs 源文可见线索逐项对齐，每条线索必须有保留或显式裁定删除+理由；手工起草母版文件替代节点产物=明令禁止（帽就是这样悄悄丢的）。

## 四、画风锁定迭代链（写进 gpt-image-subject-assets + storyboard 节点 Skill）

凡哥四次指认画风漂移，每次根因不同：

| 版本 | 措辞 | 漂移 | 根因 |
|------|------|------|------|
| 裸标签 | "3D animated film" | 2 次元 | 无锁风措辞 |
| v1 | volumetric/subsurface skin/PBR | 写实 CG | 写实渲染词 |
| v2 | large expressive eyes/rounded | 皮克斯欧美风 | 欧美卡通词 |
| v3 定稿 | Chinese 3D donghua + 东方五官 + 7.5 头身 + 显式排除 | ✓ | 国漫三锚点 |

**国漫 3D 锁风三锚点**：东方五官（鹅蛋脸/丹凤眼/精致小鼻）+ 修长 7.5 头身 + 国漫渲染质感；显式排除 not Pixar/Disney/western cartoon/no rounded chubby proportions/no big circular western eyes。

## 五、宫格图边框稳定约束

- 现象：宫格分割线不稳定——有的达标（1-2px 细线）有的很粗。
- 根因：模型把「分割线」当装饰元素自由发挥。
- 规范（prompt 必写）：`uniform ultra-thin hairline dividers between panels, every divider exactly the same 1mm thickness` + 禁止项 `no thick borders, no black frame, no comic panel outlines, no double lines, no colored dividers` + 宫格外无边框。

## 六、One-Shot Generation Rule

每个 asset_id 只调一次生成，结果立即交付登记。禁止重新生成/筛选/择优/修图/「不满意再来一张」——节点没有第二次机会。实战：8 次重试浪费 7 张作废图。

## 七、清理三件套（环境级，节点外）

凡哥考核原话：「跑图之前要干嘛？」——①核对资产台账 asset_image_inventory.json（资产图一张不少）②删作废旧图/旧视频（换版即清）③视频前 POST /free 释放资源。属环境级纪律（working-with-fange），不进节点 Skill。
