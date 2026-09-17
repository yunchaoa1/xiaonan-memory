---
name: gpt-image-style-prompting
description: Use when writing style prompts for GPT Image 2. 生图画风控制防漂移。
version: 0.1.0
author: Xiaonan
license: MIT
metadata:
  hermes:
    category: creative
    tags: [gpt-image, style, art-direction, prompt, brushwork]
    related_skills: [image-prompt, image-asset-prompting]
---

# GPT Image 2 画风控制（Style Prompting）

## When to Use

凡哥用 GPT Image 2（gpt-image-2）生图、需要控制画风/风格/质感、或生成结果漂成写实/二次元要纠正时加载。

## Overview

写 GPT Image 2 画风/风格提示词的方法，防漂移（尤其防"漂成写实"）。核心结论来自凡哥多轮实测验证，不是通用教程照搬。

## 三条铁律

1. **结构化风格声明 > 关键词堆栈**：GPT Image 2 有推理层（Thinking Mode），官方明说 "Precise style control with minimal prompting"。堆 15 个逗号关键词（Midjourney 式）会过度执行甚至反向；正确是「风格名 + 2~3 关键特征 + 1 个明确排除」，风格声明放提示词靠前。
2. **笔触是命门**：写"怎么画的"（brushwork / line work / flat fills）比写"什么风格"（cel-shaded）更能锁画风。两条路径：平涂（cel shading）vs painterly（渐变写实），选错拉不回来。
3. **负向词精简但必须**：明确写 `not photorealistic` / `not flat 2D`，不用堆一串 no（堆多了模型混乱，反而更写实）。

## 笔触维度对照

| 路径 | 笔触词 | 结果 |
|------|--------|------|
| 平涂 cel shading | flat color fills, hard shadow edges, no gradient brushwork | 动漫/二次元 |
| painterly | layered brushstrokes, soft transitions, visible brush texture | 写实 |

## 3D 动漫电影风（验证锁定的正确表达）

踩坑顺序（都验证过）：
- ❌ `3D animated film style` → 漂写实 Pixar（"3D"+"animated film" 默认关联写实 CGI）
- ❌ 三渲二平涂（`cel-animation brushwork + flat fills + 重描边`）→ 太二次元，没出二次元范围
- ❌ `real 3D volume + soft cinematic lighting + film-quality depth` → 偏写实（cinematic/film-quality/real 是写实信号）
- ❌ 堆 anime 词（`anime lighting/anime materials/anime palette`）→ 反而更写实（堆词混乱）
- ✅ 正确 = **真实 3D 渲染 + 动漫角色设计**（《原神》/国产 3D 国漫质感）：有体积、有光影、有材质，但角色是动漫审美，既非平涂也非写实真人

**关键心法**：往动漫靠是做"减法"（删 cinematic/film-quality/real 等写实信号），不是做"加法"（堆 anime 词）。

### 最终锁定声明（母亲 + 周野均验证通过）

```
Stylized 3D rendered anime character, next-gen 3D CG quality — 3D volume, highly detailed, rim light with warm-cool contrast, detailed skin and hair strands and fabric texture, anime facial proportions with large expressive eyes, clean bright colors; not photorealistic, not realistic skin texture, not flat 2D cel-shading.
```

### 精致度三件套（"够精致"的关键，对标主流 3D 动漫短剧）

1. 次世代 CG 质感：`next-gen 3D CG quality`
2. 材质细节：`detailed skin / hair strands / fabric texture`（不能是泛泛的 smooth materials）
3. 光影强化：`rim light with warm-cool contrast`（轮廓光 + 冷暖对比）

## 其他画风方向（未逐张验证）

- 日式动漫（2D 赛璐璐）：`2D anime, clean hand-drawn line art, flat cel-painted color, hard shadow edges; not 3D render, not photorealistic`
- 韩式彩漫：`Korean webtoon, clean digital line work, soft digital brush shading, detailed iris; not manga, not photorealistic`
- 国风水墨/工笔：`Chinese ink wash, expressive loose brushwork, wet-on-wet washes, dry brush texture, rice-paper texture; not photorealistic, not glossy`
- 写实电影概念：`cinematic concept art, painterly brushwork, layered brushstrokes, cinematic three-point lighting`

## 品牌标记（LOGO / 图标）产线 —— 支持文件

给品牌/平台出**标记（mark）**时，本技能带两份实测支持文件（原生归属 `logo-generator`，该技能当前为用户所有、后台不可写，故暂存于此）：

- `references/ai-generated-logo-marks.md` —— 用生图出标记稿的完整方法：prompt 模板（单色/无字/无渐变/瑞士风格那串固定后缀）、一次批量 4–6 张、白底稿转**精确目标色 + 真透明**的公式 `alpha = 255 - min(R,G,B)`、以及必须的质检步骤。
- `references/svg-mark-render-qc.md` —— SVG 稿 → 多尺寸透明 PNG + 白底/深底拼版 + 可点选对比页。含本机渲染事实（cairosvg 缺 DLL → 用 `resvg-py`；SVG 中文须写 `Microsoft YaHei`）、裸路径数据静默不渲染坑、光学居中算法、Chrome 无头截图裁切坑、GitHub API 取文件兜底，以及「产出后必须自己先看、坏稿不许交付」的纪律。
- `references/brand-style-directions-and-presentation.md` —— ⭐ **用户说「要高级感 / 没设计感 / 太土 / 像大牌那样」时先读这份**：高级感的真实来源（材质 / 光影 / 色彩层次 / 中文字标 / 发布会级呈现）、决策层级（**先气质方向 → 再图形 → 再应用系统**）、6 个气质方向的 prompt 词表、中文字标排版比例与缺字坑、**面向决策者（领导 / 甲方）的选型协议**（≥12 个具象母题、一概念一图、附星级与淘汰建议），以及 LogoLounge 2026 等调研依据（勿凭感觉断言）。

**⭐ 高级感铁律（最容易翻车的一条）**：用户判「土 / 没高级感 / 不像大牌」时，**先放开材质、光影、呈现这三样，不要在形状上再死磕一轮**。
同项目实测：在「单色扁平」框里死磕了三轮全被否；放开材质与呈现后一次通过。
**先定气质方向 → 再定图形 → 再定应用**，这个顺序能省掉整轮返工。

**核心纪律**：单色几何稿最容易撞**素材库脸**（翅膀/盾/靶心/维恩图/圆内平行线 + 严格对称 + 满构图）。
用户判「土 / 没有高级感」时 → **并行开生图线**（`ai-generated-logo-marks.md`）而不是在纯矢量里再赌一轮；
且**先定审美参照（对标品牌）再动手，没有参照先问用户，别盲画**。

### 偶像练习生妆造（改妆造，不是重画人）

凡哥说"把这张的穿搭和妆容润色成练习生/偶像派妆造"时用这套（实测有效）：

- **输入**：拿**上一稿已风格化的四视图**当唯一参考图（`image_url`），**不要再喂真人照片**（防写实回拉）。本版**不写**"不许瘦化"体型条款 —— 偶像派要精瘦。
- **妆容四件套**：`flawless glass skin + dewy highlight on cheekbones and nose bridge`（玻璃肌水光）／`refined thin straight eyebrows instead of thick natural brows`（细直眉换掉浓密眉）／`delicate eyeliner + aegyo-sal highlight + subtle lower-lash line`（眼线+卧蚕+下睫毛线）／`glossy rosy tinted lips + fresh natural flush`（水光润唇+血色）
- **★ 硬指标**：`completely clean-shaven — no stubble, no beard shadow, no facial hair of any kind` —— **不写就留胡茬，偶像妆直接失败**
- **发型**：保结构提质感 —— `keep the same swept-back hair with the small tied bun, but make it sleek, glossy and precisely styled with a clean product shine`
- **眼镜必留**（本人辨识锚点）：`identical thin round two-tone wire glasses`
- **两套穿搭**：①舞台打歌服 = 结构感立领夹克（金属扣+条纹边）+修身内搭+修身裤+皮靴；②练习室潮流 = 宽松短款夹克+白内搭T+工装裤+厚底潮鞋；两套都加 `thin silver chain necklace + small ear cuff`，并写 `no logos, no prints, no text`

## 真人照片 → 3D 国漫角色（★实测修正：关键在形体夸张，不在表面）

**★ 2026-09-14 实测（7 稿）最重要一条**：风格化 = **改形体（intentional deformation）**，不只是改表面。只压皮肤表面（写"无毛孔/无纹理"）→ 输出就是"照片加滤镜"（凡哥原话：「看不出是 3D 国漫风，这就是原照片的感觉」）。**加上形体夸张声明后立刻质变。**

- **必写关键词**：`bold intentional deformation` / `cartoon-shaped geometry` / `simplified clean planes and clear geometric volumes` / `clean controlled surface finish` / `avoiding random texture or noise`
- **必须删的词**：锁风句里的 `highly detailed` ＋ `detailed skin and hair strands and fabric texture` —— 在真人照片输入下这两句会把结果拉回写实，是内在矛盾
- **照片会拉向写实**（行业实证 `photos pull toward realism`）。两条解法，都实测有效：① 形体夸张声明；② **二段式** —— 先出一张风格锚定图，再拿那张**已风格化**的图当参考出三/四视图，风格不退回写实
- **默认会漂向皮克斯欧美风**：必须显式写 `mature adult male oriental facial structure, defined angular facial planes, not cute, not chibi, not a rounded baby face, not Western cartoon style`，否则脸圆润可爱（凡哥明确否过皮克斯欧美风）
- **体型条款要单列一段**：不写 `do NOT slim him down, do NOT idealize him into an athletic figure`，模型会自动把人瘦化理想化（实测：国漫版身材被瘦掉，加体型条款后还原）

### 原记录（分维度单项参考 + 相似度优先 + 背面点名）

## 真人照片 → 3D 国漫角色（身份保真 + 分维度单项参考）

把写实照片转成 3D 国漫数字虚拟偶像时用这套。已验证/已实测的事实：

- **分维度单项参考法**（凡哥的规矩）：**不是整张照片一起参考**，而是每个维度单独一张参考图（面部+眼镜裁切 / 全身正面=体型+服装 / 侧面=侧轮廓+后脑发髻 / 背面=发髻+背视图），并在提示词里逐条声明 `reference N = 某某维度 only, never copied wholesale`，再加 `take no background, no camera perspective, no lighting and no colour grading from the photos`。这样照片的环境/光影/相机透视不会被带进 3D 角色。
- **相似度优先条款（必须写）**：`Keep his real facial proportions and real eye size instead of a generic enlarged-eye anime face` —— 不写这句，"动漫化"会把眼睛放大，人立刻不像本人。凡哥的第一验收标准是「**一眼认出是本人**」（原话「动漫人物无疑，但一眼就能看出是」）。
- **背面必须单独点名**：不点名，模型会给光后脑勺，看不到后脑发髻。
- **踩坑（实测 2 稿）**：参考图是**真人照片**时写实引力很强 —— 即使风格声明已写 `not photorealistic / not realistic skin texture / no pores / simplified facial planes`，输出仍偏「半写实 3D CG」（游戏角色感），够不到《凡人修仙传》那种国漫。**风格声明在插画输入上验证有效（母亲/周野），在真人照片输入上压不住。**
- **待验证解法（未实测，别当结论）**：二段式 —— 先把真人转出一张 3D 国漫图当「风格锚定图」，再拿那张风格化图作参考出四视图，用风格化输入替代照片输入来断掉写实引力。
- **本机环境事实**：`image_gen.model` 这个配置键**改完需重启 Hermes 才生效**（运行中进程启动时读配置，改完当次生成仍用旧模型）；且它不是 CLI 认得的键，`hermes config set` 会警告但能写入。

## 工作纪律

- 画风是节点外全局参数（style_id），节点只继承不选择、不改动；换画风只变渲染风格，不变人物可见事实（脸型/发型/服装）。
- 只用一个主画风，不混用；不用在世艺术家姓名或受保护品牌风格名。
- 验证画风靠凡哥人工审图，不用 vision 模型自我判断（视觉模型判画风常不可靠）。
