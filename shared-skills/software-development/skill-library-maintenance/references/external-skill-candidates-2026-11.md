# 外部技能候选池：AI 短剧 / 分镜类（2026-11-18 实地查证）

> 用法：下次凡哥说"找个好用的分镜 skill / 短剧 skill"时，**先看本文件，再去查更新**。
> 所有星数/推送时间是 2026-11-18 用 `api.github.com/repos/<owner>/<repo>` 实测，会变，引用前重查。

---

## 一、入口：合集索引（先查这里，别逐个搜）

| 索引 | 星 | 内容 |
|---|---|---|
| **`UnderleveledBuilder/awesome-short-drama-skills`**（CC0） | ★2,529 | **收录 115 个短剧 skill + 16 个开源平台**，按"全流程 / 编剧 / 分镜·视觉资产·视频提示词 / 上游 / 编剧基本功"分类，元数据每周更新；官网 `shortdramaskills.com` |
| GitHub topics | — | `claude-code-skills`（2,780 仓）、`comic-drama`（12 仓）、`ai-video`（3,402 仓） |

**这个清单做过三轮盲测**（2026-10-18 / 10-20 / 10-31），15-20 个 skill 各写 3 次同一道题、Opus + GPT 双评审盲比：

- 第一轮（写剧本）：**`zenstory-ai/drama-skills`、`Shanyin-ai/shanyin-screenwriting-master`、`jtydhr88/screenwriting-skills`、`adoria111/emma-screenwriting-skills`** 四个"三次全赢对照组"。
- 第二轮（定选题）：`Tomsawyerhu/Chinese-WebNovel-Skill`、`lingfengQAQ/webnovel-writer`、`Hao0321/ai-short-drama` 前三。
- 第三轮（全剧骨架）：`zhu5859243-free/hongguo-shortdrama-screenwriting`、`adoria111/emma-screenwriting-skills`、`Tomsawyerhu/Chinese-WebNovel-Skill`、`lixiaoxiao9888-create/short-drama-factory` 两位评审都进前五。

**局限（清单自己写的，转述时必须带上）**：只测 `claude-opus-5-5` 一个模型；198 对比较里有 63 对两位评审结论不同；每个 skill 的稿子都夹编号和自检表，投喂前要删。

---

## 二、已实测结构的四个"分镜"候选

### ① `forest-laoli-h3`（漫剧老李 · H3 专版）★84 · MIT · pushed 2026-11-02
**只做 MiniMax H3**，v2.1.1。这是四个里**机检最完整**的：

```
forest-laoli-h3/
├── SKILL.md                        23K
├── references/  (18 本)
│   ├── camera-movement.md          36K   运镜
│   ├── h3-shot-grammar.md          20K   H3 镜头语法
│   ├── h3-format.md                15K   H3 格式
│   ├── h3-lexicon-cleanup.md       13K   H3 词汇清洗
│   ├── spatial-anchor-and-hold.md  13K   空间锚定
│   ├── asset-layer.md              13K   资产层
│   ├── diagnose.md                 16K   诊断
│   ├── dialogue-density.md          9K   台词密度
│   ├── acting-facs.md               7K   FACS 表情
│   ├── acting-listen.md             5K   倾听表演
│   ├── acting-recipes.md            8K   表演配方
│   ├── atmosphere-and-light.md     10K
│   ├── camera-four-axis-h3.md       8K
│   ├── checklist.md                11K
│   ├── delivery.md                  6K
│   ├── examples.md                 10K
│   ├── gates.md                     8K
│   ├── h3-constraints-qc.md         9K
│   ├── pipeline.md                 12K
│   └── script-layer.md              6K
└── scripts/
    ├── h3_lint.py                  62K   ← 机检脚本
    └── tests/                     29 个用例（case01–case29，含 ok/bad 对照）
```

卖点原文：剧本→资产→H3分镜→**三字段/六段式投喂稿**→机检→交付包；**六项锁 + 铁律 + H1~H36 机检 + 29 用例零放水**；"通用型不绑定渲染端"；9:16 推荐 / 16:9 可用。
**风险**：星数低（84），可能未经大规模验证；同为 `lixiaoxiao9888-create` 出品。

### ② `short-drama-storyboard` + `short-drama-video-prompts`（zenstory-ai/drama-skills）★4,434 · MIT · pushed 2026-11-16
**结构最标准（大梁式）**：13 个技能，每个 SKILL.md 只有 4–10K，细节全在 references。

```
skills/short-drama-storyboard/        SKILL.md 10K
  references/ blocking-playbooks 5K · fight-craft 4K · keyframe-craft 7K
              screenplay-to-keyframe-example 7K · shot-craft 9K · stage-contract 9K
skills/short-drama-video-prompts/     SKILL.md 9.4K
  references/ minimax-h3 10.5K ← H3 专属 · seedance-2.0 4K · seedance-2.5 5K
              wan-3.0 5K · video-prompt-guide 9K · camera-audio-continuity 5K
              performance-action-timing 5K · model-and-delivery-profiles 7.5K
              stage-contract 8.8K
```

套装还有 `short-drama`（总入口 7.8K）、`-write`、`-breakdown`、`-assets`、`-image-prompts`、`-produce`、`-edit`、`-review`、`-develop`、`-novel-analyze`、`-knowhow`。全仓 553 个文件。
**优势**：三套盲测里都是赢家；四个视频模型各一本手册，换模型只换那本。

### ③ `sd-storyboard-engine`（lixiaoxiao9888-create/manju-laoli-skill）★2,145 · MIT · v7.5
通用短剧套装（1 总控 + 12 子技能），分镜引擎单独拆出：

```
sd-storyboard-engine/  SKILL.md 37K
  references/ short-drama-camera-system 56K · shot-economy-and-acting 42K
              storyboard-sheet-template 22K · p45-previs-storyboard 11K
              plot-deduction-grid 10K · scene-space-adaptation 7K · segment-linkage 870B
  scripts/    check_p45.py 16K
```

卖点：**三条硬契约** —— 台词不许私自删（要精简必须出清单征询）、不许越权决定切镜、3D 禁「特写×平视正面」；机位有配额（荷兰角≤1 / 大仰角≤3 / 常规镜头压到 30%）。
**短板**：主文件 37K 偏大；不写时长（交下游）；套装契约依赖未随装的 `short-drama-director/references/model-adapters.md`。

### ④ `h3-storyboard`（phileiny/h3-storyboard-skill）· MIT · 35 commits
```
SKILL.md 105K + SOURCES.md 34K
```
**内容最"讲原理"**：每条规则标明是"有对照实验"还是"仍是推断"。核心实证：一颗 7 秒特写塞 9 个表情节拍 → PSNR 37–42 dB（冻帧）；拆成三颗 2–3 秒各一个主节拍 → 22–23 dB（表情到位）；加 `<d>` 对白 → 19 dB。
另有：帧数 `17n+5` 格点、**尾巴留 1.3–1.5 秒**（H3 在片尾前 1.2–1.7 秒崩解成噪讯）、"先问要不要生成"（能复用就 trim，省 40 分钟）、禁用字对照表。
**致命短板**：**105K 单文件，加载即被 `[SKILL_PRUNED]` 剪掉，实际读不进来**（实测 12–18K 就会剪）。

---

## 三、其他相关（未细看）

| 仓库 | 星 | 一句话 |
|---|---|---|
| `zhanghao123vip/ai-manju-skills` | ★847 | 21 个题材的漫剧模板（企划案→资产→分集剧本→分镜→视频提示词） |
| `10291124jcjc-dotcom/ai-anime-series` | ★392 | 固定原创角色，主题→无台词动作喜剧 |
| `Work-Fisher/fisher-storylens` | ★43 | 剧本→定角色→定场景→按确认图写 H3 提示词，15 秒一段 |
| `doublesq97-ui/su-ai-short-drama` | ★70 | 女频/男频两版，按"总导演/编剧/选角/分镜导演"岗位协作 |
| `JuneYaooo/rea-toon` | ★219 | 逆向：拆解别人短剧为什么火 |
| `liangdabiao/Seedance2-Storyboard-Generator` | — | Seedance 分镜生成器 |

---

## 四、从中提炼的三条通用判断

1. **专用版 > 通用版**（任务锁定单一模型时）。`forest-laoli-h3` 只做 H3，机检细到 29 个用例；通用版要照顾三四个模型，规则必然被摊薄。
2. **主文件大小是第一道筛子**。>20K 的要警惕、>50K 的基本读不进来 —— 结构再漂亮也用不上。
3. **星数 ≠ 好用**。★4,434 的 zenstory 和 ★84 的 forest-laoli-h3 各有优势；**盲测排名 + 结构 + 能不能读进来，三个一起看**。

---

## 五、⭐ 格式家族：选型时必须先查（2026-11-18 补充，差点漏掉）

**判断"能不能直接喂目标模型"的关键，不是技能好坏，是它吐出来的提示词格式是不是目标模型的官方格式。**

### H3 官方格式 = 六段式

我们自己的 `h3-video-prompt` 里白纸黑字（原文）：

> **「六段格式（官方 Ref2VA，顺序与字段名固定，不可乱）」**
> **「六段全英文，仅 `<d>` 内中文」**

字段名：`subject_definitions` / `summary` / `retention_analysis` / `detailed_description` / `overall_soundscape` / `non_diegetic_music`
（简版三字段：`integrated_multimodal_description` / `overall_soundscape` / `non_diegetic_music`）

### 四个候选分两派

| 候选 | 输出格式 | 能不能直接喂 H3 |
|---|---|---|
| `forest-laoli-h3` | **六段式**（官方，扫描命中 4 处字段名） | ✅ 能，且自带机检闭环 |
| `short-drama-video-prompts` | **六段式**（扫描命中 6 处） | ✅ 能 |
| `h3-storyboard` | **六段式**（扫描命中 4 处） | ✅ 能（但单文件 105K 读不全） |
| **`sd-storyboard-engine`** | ⚠️ **七段式**（自创，扫描命中 10 处方括号栏位） | ❌ **不能，要先转义** |

**七段式长这样**：`【画幅风格】→【场景资产】→【核心人物】→【站位声明】→【时间轴分镜】→【音效】→【强制禁止项】`

**它不是错误，是取舍**：sd 要同时喂 Seedance 2.5 / 2.0 / H3 三个模型，自创一套中文七段式统一格式。**但它自己没说是 H3 实测**，所以"H3 认不认这个格式"至今未验证。

**一条命令查格式家族**（装完立刻跑，别等测试才发现对不上）：
```bash
grep -c "subject_definitions\|detailed_description" <技能>/SKILL.md <技能>/references/*.md   # 六段派
grep -c "【画幅风格】\|【时间轴分镜】"               <技能>/references/*.md                  # 七段派
```

### 推论：分镜技能必须有"配套下游"才能端到端比

**分镜技能只出"分镜稿"，不出"模型提示词"** —— 所以：
- `sd-storyboard-engine` 的下游是它总控的 `model-adapters.md`（七段式封装，85K，要随装）
- `zenstory` 的下游是同一套装的 `short-drama-video-prompts`（六段式）
- `forest-laoli-h3` / `h3-storyboard` 是**一体式**（自带到提示词）

**⚠️ "用它的配套下游" ≠ "混着用"。** 凡哥的规矩是"不混着用"，指的是**别把 A 的分镜规则和 B 的提示词规则搅在一起**；用 A 自己设计的下游是**它的组成部件**，不算混。

**公平对比必须以"端到端方案"为单位**，四组：
1. forest-laoli-h3（一体）
2. h3-storyboard（一体）
3. zenstory storyboard + video-prompts（配套）
4. sd-storyboard-engine + model-adapters.md（配套）

前三个天然是官方六段式，可以直接用同一套机检横比；**第 4 个要先证明七段式喂 H3 有效**，否则它只能当"分镜稿生成器"。

---

## 六、机检能测什么、不能测什么（别夸大）

**`h3_lint.py`（forest，62K，H1~H36）实测输出示例**：
```
[ OK ] H16  无禁用运镜
[WARN] H20  台词填充率仅 8%（1句/4字≈1.2s 占 15s 段）——观众会体感「对话太少」
[WARN] H24  关键镜行缺维持句（站位/家具会漂移）：['Shot 1','Shot 2','Shot 4']
[WARN] H27  末镜 Shot 4 无定格句（段缝截不出尾帧会跳）
[WARN] H35  氛围层缺 2/3：空气介质、前景遮挡/景深（不写就是平光片）
—— FAIL 0 ｜ WARN 5 ——
```
退出码：0 = 无 FAIL，1 = 有 FAIL，2 = 用法/读取错误（**可编程判断，能进流水线**）。

**它验的三类**：
1. **格式**（H1 六段/三字段齐不齐、H4 中文残留、H8 禁 @锚点/ASCII框图/坐标表、H14 画幅、H23 镜行 ≤75 词）
2. **H3 的已知行为陷阱**（**最值钱**）：H2 首镜不能带时间戳／**写"镜头切至"→ H3 做成叠化融脸**／写 cross-dissolve 也错／**写"升格/慢动作"→ H3 渲染成静止**；H19 位移与变焦不能叠加；H21 台词镜必须换嘴切镜（回合制）；H28 空间描述禁复数扩建词；H29 禁"穿过门洞"消除式动作；H33 禁高危卡死/冻帧动作
3. **输出质量的客观指标**：H20 台词填充率、H24 维持句、H27 末镜定格句、H35 氛围层（光/空气/前景）

**它测不出的**（凡哥问过"能测出 H3 的遵循程度吗"，答案是**不能**）：
- 脸到底演不演
- 画面质感
- 尾巴到底崩不崩（只能靠"有定格句"降概率）

**一句话定性**：机检是**上车前的安检**，不是**车开得好不好**。类比作文的"错别字 + 字数检查"——查完不等于文章好，但错字连篇肯定不行。

**它的真正价值**：每条规则都是**别人真跑崩了才写进去的学费**（中文切镜动词、升格、段缝无定格、氛围层缺失），我们照抄就不用再交一遍。

**所以正确流程**：
```
按技能规则产出提示词 → 过机检（筛掉 80% 低级错误，免费秒出）→ 真跑 H3 → 看片子
                                                     ↑ 这一步机检替代不了
```
