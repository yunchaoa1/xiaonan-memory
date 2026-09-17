# 品牌气质方向 + 高级感呈现（用户说「要高级感 / 像大牌」时读这份）

> 2026-09-11 天使OPC数字社区项目后半程实测。用户连续三轮否决「单色扁平极简」
> （评语：「很土」「一点高级感也没有」「像素材库」）；**放开材质 / 光影 / 色彩 / 字标 / 呈现后一次通过**
> （评语：「完全不同了」）。原生归属 `logo-generator`（用户所有、后台不可写），故收录于此。

---

## 一、核心诊断：高级感不住在「形状简单」里

把标志压成 **单色 + 扁平剪影 + 无材质 + 无光影 + 无字标 + 无呈现** = 免费 logo 生成器的脸。
**高级感 = 材质 / 光影 / 色彩层次 / 字体气质 / 呈现方式 的合力。**

**⚠️ 推断规则（最重要的一条）**：用户说「太土 / 没设计感 / 没高级感 / 不像大牌」时 ——
**先放开材质、光影、呈现这三样，不要在形状上再死磕一轮。** 本项目在形状上死磕了三轮才想到这条，白费三轮。

## 二、决策层级：先气质 → 再图形 → 再应用

1. **气质方向**（一次给 6 个，气质要拉开，每个只出一张图）
2. **具体图形**（在选定气质下收敛 3–4 个图标，同气质横向比）
3. **应用系统**（App 图标 / 横竖版锁标 / 站标 / 头图 / 名片工牌 / 使用规范）

先定气质再定图形，可避免「图形定了才发现气质不对」的整轮返工。

## 三、6 个气质方向的 prompt 词表（实测出稿）

统一结构：
`Premium brand identity presentation: <图形> in the upper center of <底色/环境>, <材质/光/色彩关键词>, generous empty dark space across the bottom third for a wordmark. <气质锚点>, no text, no letters, no watermark, 8k detail`

| 方向 | 材质 / 色彩关键词 | 气质 |
|---|---|---|
| 玻璃质感·科技未来 | `glossy translucent glass`, gradient `deep royal blue → bright cyan`, `subtle inner light`, `rim lighting`, deep midnight navy backdrop, `radial blue glow` | 科技大牌发布会级，最"贵" |
| 金线徽章·高端商务 | `thin elegant champagne-gold lines`, matte + metallic gold, deep charcoal navy, understated emblem | 私行 / 奢侈酒店，最低调最贵气 |
| 流体渐变·潮流科技 | `fluid liquid ribbon`, gradient `electric blue → violet → cyan`, `soft ambient glow`, bloom, dark indigo | 一线大厂流体渐变 |
| 霓虹光效·潮酷 | `glowing neon outline`, bright cyan / electric blue light, pure black, reflections on `glossy floor` | 电竞 / 夜店，最抓眼 |
| 金属门户·稳重可信 | solid confident form, `brushed metal texture`, soft top-down lighting, deep ocean-blue gradient | 大公司稳重款 |
| 3D 浮雕·厚重质感 | `sculptural 3D`, `embossed polished chrome and enamel`, deep reflections, `dramatic rim light`, dark studio | 铭牌 / 奖杯 / 皮面烫印 |

**关键配方**
- **明写留出底部三分之一空白**（`generous empty dark space across the bottom third for a wordmark`）→ 自己再叠中文字标。
- **不要让模型写中文名**：CJK 会糊、会写错。模型只出「标记 + 环境」，中文标准字用 PIL 自己排（见第四节）。
- **一个方向一张图**；同一符号给多版本会淹没判断力，用户明确要求过「先一图标一图」。

## 四、中文字标排版（PIL，本机字体）

- 可用字体：`msyhbd.ttc`（微软雅黑粗）、`NotoSansSC-VF.ttf` / `Noto Sans SC Bold|Medium`（= 思源黑体）、
  `Source Han Serif SC Heavy`（思源宋体）。
- ⚠️ **`Source Han Serif SC Heavy` 缺 U+00B7（`·`）**：含 `·` 的小标签用它就渲染成**方框**。
  → 小标签 / 编号行一律用思源黑体，只有大标题用宋体。（本项目真实翻车一次）
- **字距**：PIL 没有 letter-spacing，逐字 `draw.text` 并累加 `draw.textlength(ch) + track`。
- **锁标比例（实测舒服的一组）**：符号高 = 1.0；主字号 ≈ 0.42×；副字号 ≈ 0.20×；
  两行行距 ≈ 0.06×；符号↔文字间距 ≈ 0.30×。横版 = 符号左 + 文字块竖向居中于符号光学中心。
- ⚠️ **别让字标压过符号**：首版主字号过大，符号沦为配角，被一眼看出不协调。
- **英文副标**：全大写 + 约 **0.22em 大字距**（`ANGEL OPC · DIGITAL COMMUNITY`）——
  廉价感 → 高级感的分水岭之一。

## 五、面向决策者（领导 / 甲方）的选型协议

- 决策者要 **能看懂 + 有含义 + 不花哨**；抽象几何在其眼中 = 「不知道画的啥」（用户原话：领导看了「感觉很抽象」）。
- 给 **≥12 个不同母题**（翼 / 门 / 星 / 手 / 山 / 鸟 / 阶梯 / 拼图 / 徽章 / 首字母 / 灯塔 / 自然），**优先具象可辨**。
- **一个概念一张图**，每张附**星级 + 一句话含义 + 淘汰建议**；不要给同一符号的多版本。
- 抽象 / 极简精修（负空间、光学修正、网格对齐）留到**方向定稿之后**再做。

## 六、调研依据（可引用，勿凭感觉断言）

- **LogoLounge 2026 趋势报告**（统计 30,000+ 标志；logonews.cn 有中文版）：年度主题 = **动势（dynamics）**；
  第 1 趋势 **V Balls**（举臂 / V 形围合 = 人群、团结、共享能量，「community in motion」）；
  报告对过去十年「扁平极简、彼此长得一样」是**反动** —— 「brands want to be **remembered**, not just legible」。
- **最被记住的标志共性**：极简 + 一个有含义的故事 + 高对比 + 可缩放 + **不过时**。
  典型：Nike 对勾 = 胜利女神的**翅膀**，同时读作「对勾 = 成功」（一形两义）；
  Mastercard 交叠双圆 = 连接 / 信任；Audi 四环 = 团结；Mercedes 三芒星 = 覆盖。
- **抖音 logo 手法正名**：故障艺术（**Glitch Art**）的「错位」—— 青 `#25F4EE` + 洋红 `#FE2C55` + 黑白，错位叠印；
  符号是「音符」（取自名字的「音」）。关键不是抽象几何，而是**有性格的强符号**。
  ⚠️ **用户明确纠正过：抖音只是举例，不是必须照做。** 错位叠印属潮流手法、与「不过时」相悖，
  只在明确需要年轻化时作为**可选项**，不要当成必选路线。

## 七、经验回流

- 新的气质方向词表 → 回填第三节表格。
- 用户对新方向的评语（通过 / 否决 + 原话）→ 回填第一节的推断规则，让下一轮少绕弯。
