# 「分镜技能只留一个」实战记录（2026-11-22）

凡哥原话：**「拿我们的分镜 skill 是不是还有其他的？会不会打架？我们只留一个就好」**
随后又纠正一次：**「我们不是只找到一个是我们需要的skill吗？」**

---

## 一、当时到底有几个在做「剧本 → 分镜」

`python D:\Hermes\scripts\find_skill.py 分镜` 命中 22 条，其中**真做分镜稿（启用）5 个**：

| 技能 | 体量 | 干什么 | 处置 |
|---|---|---|---|
| `forest-laoli-h3` | 12,592 字 | H3 专用全流程（G0→①剧本→②资产→③分镜→④编译→⑤机检→⑥交付） | **留，唯一入口** |
| `h3-storyboard` | 47,861 字 | 同为 H3 分镜（六段派、外部装的那套） | **归档** |
| `sd-storyboard-engine` | 16,689 字 | 套装内部，自创七段式，H3 认不认未验证 | 待凡哥定（OPC 套装在用） |
| `short-drama-storyboard` | 4,536 字 | 通用短剧分镜 + 首帧提示词 | 待凡哥定（与 video-prompts 成对） |
| `screenplay-to-15s-storyboard-opc-test` | 23,246 字 | OPC 流水线节点（剧本→15 秒分镜） | 待凡哥定（OPC 出包要用） |

**非分镜、别误算**：`storyboard-keyframe-opc-test`（宫格关键帧＝生图工序）、`short-drama-video-prompts`（分镜下游＝提示词）、`yingju-workshop-pipeline`（六节点总控）、`character-vlog-pipeline`（已禁用）。

**汇报口径的错**：我第一次把「`forest-laoli-h3` ＋ 它的施工手册 `h3-segment-filmmaking` ＋ 手册里的 `check_dialogue_coverage.py`」报成「三件技能」，凡哥立刻纠正 —— **手册和脚本是技能的一部分，不是并列的技能**。以后报数只数 `SKILL.md` 目录。

---

## 二、打架的确切证据（这是本次真正的病灶）

`skill-router/SKILL.md` **同一个文件里两段相反的话**：

- 第 22 行（路由结论）：`唯一入口：forest-laoli-h3（H3 专用全流程，六阶段一条链）`
- 第 144 行（自查清单）：`- [ ] 凡哥需求是"做成视频/出片/分镜"吗？→ 三步链走完了吗？（① sd-storyboard-engine 出分镜稿 → ② h3-storyboard 查节拍密度 → ③ h3-video-prompt 写提示词）跳一步就是违规`

**第 26 行已经写明这条三步链是 2026-10-14《偏心》整版作废的原因**（台词全抽成 mp3、提示词里一句台词不写、白跑 6 颗镜头 + 17 张资产图作废），但 144 行没跟着改 → 实际执行时照的是 144 行。

> **判据：`health_check.py` 报「疑似重复：无、悬空引用：无」也可能照样打架。**
> 它查的是**跨技能**（description 撞车、引用悬空），查不出**单文件内部自相矛盾**。
> 查法：`grep -n "<技能名>" <路由技能>/SKILL.md`，同一文件里同时出现「唯一入口」和「必走／必经／必须」＝矛盾。

---

## 三、动作与验证

1. 归档：`cp -r skills/creative/h3-storyboard skills-archive/creative/` → `sleep 3` → `rm -rf skills/creative/h3-storyboard`
   （第一次 `rm -rf` 报 `Device or resource busy` —— Hermes 常驻监控 skills 目录，`sleep` 后重试即成功）
2. 改路由**两处都改**：第 40 行（降级说明加"h3-storyboard 已于 2026-11-22 归档 + 恢复命令"）、第 144 行（改成走 `forest-laoli-h3` 那条链，并写明废弃的三步链）
3. 扫残留引用 7 处，分三类处理：
   - `skill-router` ×2 → **活路由，必改**
   - `av-generation-troubleshooting` ×4 → 其中 1 处是"步骤②"直接改指 `forest-laoli-h3`；另 3 处是**引用 h3-storyboard 的原话/结论**，改成「（原 `h3-storyboard` 的原话…；该技能已于 2026-11-22 归档，原文在 `D:\Hermes\skills-archive\creative\h3-storyboard`）」—— **保留出处，不删知识**
   - `sd-storyboard-engine/ORIGIN.md`、`_候选池_分镜技能来源登记.md` → **历史快照，不改**
4. 验证：`health_check.py` → `启用技能: 70 ｜ 悬空引用: 无 ｜ 重复: 无 ｜ 结论: ✅ 健康`；`find_skill.py 分镜` 已不再出现 h3-storyboard
5. 同步：`sync_skills.py push` ＋ DASHBOARD 记一节（含恢复命令 `restore_skills.py h3-storyboard`）

---

## 四、给凡哥的回复结构（他验收的就是这个）

1. **清单表**：技能 / 干什么 / 状态（留 / 已归档 / 待定）
2. **打架的证据**：引原文（哪个文件、哪一行、两句相反的话），不用"感觉重复"这种词
3. **已处置**：归档了什么、改了哪几处、体检结果
4. **剩下的为什么不能一刀切**：属于别的流水线的节点，删了会断 OPC 出包 / 影剧工坊六节点 → **一条问句让他定**

> 凡哥要的是"只留一个"，但**执行上"一个"指的是同类入口只留一个**，不是把 OPC 流水线的工序节点一起删。说不清依赖就删，等于拿别人的产线换整洁。
