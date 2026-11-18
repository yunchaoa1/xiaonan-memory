# 模型换代后的技能改造 · 2026-11-18 实战存档

> 场景：凡哥说「现在出图是用的 seedream」。库里的 `gpt-image-*`、`qwen-image-*` 全是换模型留下的旧衣裳，体检报成"两道鱼香肉丝"。
> 结论：**它们不是重复，是"旧版 vs 升级版"+"被依赖的编译模板"**。按"删"处理会砸掉正在用的能力。

## 一、体检基线（2026-11-18 跑 `skill_audit.py`）

| 项 | 数字 |
|---|---|
| 技能文件总数 | 182（`hermes skills list` 里 enabled 约 120，其余 builtin/平台不符已禁） |
| 缺"怎么算做完"（验证章节） | 22 / 182（12%） |
| 缺触发词 | 49 / 182（27%） |
| 缺边界/坑 | 60 / 182（33%） |
| description 雷同组 | 6 组 |
| 体积 >1.2 万字 | 7 个（最长 `research-paper-writing` 70,719 字） |
| >30 天没动 | 137 个（75%） |

⚠️ **口径教训**：同一天自写脚本报"缺验证 59 个"，官方脚本报 22 个 —— 因为 `VERIFY_RE` 的匹配词表不同。**报数只认官方脚本**，否则要跟凡哥解释两轮为什么数字打架。

## 二、6 组雷同（体检输出原文）

```
[3 个] claude-code | codex | opencode            （均已 disabled，builtin）
[2 个] gpt-image-storyboard-keyframe-opc-test | qwen-image-storyboard-keyframe-opc-test
[2 个] gpt-image-style-prompting | short-drama-story-engine
[3 个] gpt-image-subject-assets | qwen-image-subject-assets | screenplay-asset-extraction
[2 个] novel-to-screenplay | screenplay-to-15s-storyboard
[3 个] docx | powerpoint | xlsx
```

**不是每组都该并**：`novel-to-screenplay`/`screenplay-to-15s-storyboard` 是链条上下游；`docx/powerpoint/xlsx` 是三种真实格式；`gpt-image-style-prompting` 与 `short-drama-story-engine` 用途不同，只是描述开头撞了。**只有"同一件事、只差模型名"的才是真双胞胎。**

## 三、两对真双胞胎的真相

| 技能 | 体积 | version | 真相 |
|---|---|---|---|
| `gpt-image-storyboard-keyframe-opc-test` | 10,467 | 0.1.0-rc | 旧版 |
| `qwen-image-storyboard-keyframe-opc-test` | 11,804 | **0.2.0-rc** | **升级版**，开头明写"旧 GPT Image 2 / Nano Banana 通道已退役" |
| `gpt-image-subject-assets-opc-test` | 17,795 | — | 旧版 |
| `qwen-image-subject-assets-opc-test` | 24,844 | **0.4.0-rc** | **升级版**，且是**模型无关的编译模板** |

**`diff` 出来的实质差异（storyboard 对）**：qwen 版多了三条硬规则 ——
- 「占框写死」治"大小比例忽大忽小"（每格写死主体占框百分比 + 头顶留白，全片逐字相同措辞）
- 「尺度对比镜」小人/巨物同框必带尺度锚，巨物虚焦
- 分辨率改成该模型原生上限

→ **这些规则跟模型无关，是资产，必须保留。**

## 四、差点删错的那一条（最重要）

```
skills/creative/image-prompt/SKILL.md:50
四视图提示词的完整编译（宫格细线约束 / 锁风全句 / 四格一致性 INVARIANTS / EXCLUSIONS）
**必须走 `qwen-image-subject-assets` 的编译模板逐块填写**，不许手拼
```

`image-prompt` 就是**豆包 Seedream 那套正在用的技能**。也就是说：**名字带 Qwen 的那个技能，是 Seedream 出图流程的必需依赖。** 删掉 = 四视图没人编。

→ **硬规则：任何"疑似重复"先 `grep -rn <技能名>`。命中活文档 = 依赖，改名不删。**

## 五、实际执行（2 对 → 2 个干净技能 + 2 个归档）

1. 归档旧版：
   `mv gpt-image-storyboard-keyframe-opc-test D:/Hermes/skills-archive/creative/`
   `mv gpt-image-subject-assets-opc-test D:/Hermes/skills-archive/creative/`
2. 改名去模型前缀：
   `qwen-image-storyboard-keyframe-opc-test` → **`storyboard-keyframe-opc-test`**
   `qwen-image-subject-assets-opc-test` → **`subject-assets-opc-test`**
3. 改四类内容：`name:`（与目录一致）/ `description:`（去模型绑定、写"出图走豆包 Seedream 5.5"）/ `tags:` / 顶部"出图工具（换轨日期）"一行
4. 参数换成 Seedream：**横屏 16:9 = 2816x1584，竖屏 9:16 = 1584x2816（最高 2K，无 4K）**；云电脑 Qwen（ComfyUI 三件套，2752x1536）标为**备用通道，工作流不拆**
5. 修引用：`image-prompt`、`image-asset-prompting` 里的 `qwen-image-subject-assets` → `subject-assets-opc-test`
6. 验证：两个都 `enabled`；技能文件 182 → 181（改名不减，归档才减）
7. 同步：`sync_skills.py push`（新增 2、更新 4）→ git commit

## 六、遗留可接受项

改名后正文里仍保留 7 处 `Qwen-Image 2.1` 字样，全部出现在"备用通道 / 技术规格"语境（如 ComfyUI 三件套 UNET/CLIP/VAE 名、备用画幅）。**这些是有用的历史信息，不是矛盾**，不追求清零 —— 只改"跟新说法直接冲突"的那几处（本次改了竖屏分辨率与正文尾部"出图走 Qwen 工作流"）。

## 七、下次遇到同类（换视频模型也会来一遍）

Seedance / LTX / H3 各自的 `*-prompt`、`*-opc-test` 技能是同一模式。**判据始终是同一条：名字里带模型名 = 迟早变成旧衣裳；先 grep 依赖，再决定归档还是改名。**
