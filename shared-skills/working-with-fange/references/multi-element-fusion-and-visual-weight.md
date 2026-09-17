# 多元素融合 · 视觉重量 · 二维单色 · 实景呈现

> 2026-09-14，天使OPC数字社区 logo 项目（凡哥重启后的推进）。素材：凡哥给的①一对写实羽毛翅膀（564×564，RGB 白底，翼为深色、bbox x68-495 y139-467）②「OPC」圆头等宽线条字标（198×81，白底，深色字母 + 一颗蓝点；O 有缺口、P 有开口、C 开口向右）。
> 项目资产根：`D:\数字资产\图片资产\logo-天使OPC数字社区\`（`wingopc/` 早期探索、`wingopc4/` 融合成品、`tian3/` 汉字字形、`english/` 副行排版）。

## 1. 直接合成：7 种结构全部不成立（不要重复试）

| 结构 | 失败表现 |
|---|---|
| 翼在上、字嵌进翼中间缺口 | 字母太小被翅膀压死，上下失衡 |
| 字在上、翼在下方托举 | 翅膀像从字母里长出来，糊成一团 |
| 双翼分列字母两侧 | 出现 4 个半翼，像蜘蛛 |
| 翅膀缩小嵌进 O 的环内 | 太小，读成一坨黑块 |
| 字母反白压在翼身上 | 羽毛尖刺把字母切碎 |
| 字母加粗去咬合翅膀 | 笔画撞在一起，闷 |
| 双翼合围成一个圆 | 读成一对括号，没有翅膀感 |

### 根因（这条最值钱）
**两套素材的"视觉重量"差太远。** 写实羽毛是**插画**（纹理 + 明暗 + 渐变 + 软化边缘），OPC 是**线条字**（纯平 + 等宽 + 圆头 + 断口）。压平插画 → 丢掉羽毛的美；保留纹理 → 标志糊。**这不是排版能救的问题**，必须在"语言"层面统一。

附带失败：从位图素材放大的字标参与合成时，锐利度不够；正式定稿必须**矢量重绘**（该在交付时就讲明，别等对方发现发虚）。

## 2. 有效的解法：让翅膀说和主元素一样的语言

保留 OPC 的字形与蓝点不动，**把翅膀按同款线条语言重画**：等宽线宽、圆头收笔、相同的断口节奏。

### 实测有效的生图提示词（monoline 翼）
```
A pair of symmetric angel wings drawn as minimal rounded monoline line art:
each wing made of 3 smooth flowing strokes with uniform stroke thickness and
rounded caps, no fill, no feather detail, no texture, flat single dark navy
color on pure white background, no gradient, no shading, no 3D, vector line
icon style, generous margin, centered, clean and simple like modern geometric
monoline lettering
```
变体：把 `3 smooth flowing strokes` 换成 `one bold curved stroke sweeping outward
and upward with two shorter parallel strokes below it suggesting feathers`
→ 更粗更有气势（N2）。

**不要**用「两翼合成一个圆」那种写法（生成结果读成心形/圈，不是翅膀）。

### 可用的构图（同一对素材，四种成品用途）
- **N1 线条翼 + OPC（同色）** —— 主标志最稳，重量完全匹配
- **N3 蓝色翼 + 墨色字（双色）** —— 最像成熟品牌；翅膀品牌蓝、字母墨色，靠色彩分级
- **N6 蓝底反白 + 圆角方块** —— 直接就是能上架的 App 图标
- **N7 横版锁标** —— 翼左字右，网站导航/名片/邮件签名
- 被否的变体：字母顶进翅膀尖（线段打架）

### 落地技术要点
- 从 AI 生成的白底翼图抠透明：`alpha = clamp((200 - L)/160) * 255`，再 `tint()` 整体填目标色 → 边缘平滑、无白边
- 需要精确单色时用 `alpha = 255 - min(R,G,B)`（抗锯齿边缘天然正确）
- 加粗位图字标：对 alpha 通道做 `MaxFilter` 膨胀，可让细线字与粗翼的重量接近

## 3. 二维单色版：不要"抠"，要"重新生成"

试了 4 轮自动提取，**全部失败**：
1. 灰度 + Otsu 软阈值 → 光晕被带进来，边缘发虚
2. 硬阈值（88 百分位）+ 保留最大 3 连通域 → 把底部的字标文字也当成主体保留，还丢笔画
3. 裁掉底部文字区 + 76 百分位 + 最大域 + 近邻大块 → 01/03 直接糊成块（它们的美本来就在材质里）
4. 逐图调阈值 + 抬高裁切 → 把徽章/门户的顶部切掉；阈值 90 时只剩细线

**正解**：把同一图形**直接以目标风格重新生成** —— prompt 里写死
`flat 2D logo mark, ONE solid flat color, no gradient / no glow / no 3D / no shading / no texture / no text`，
白底深色稿走 `alpha = 255 - min(R,G,B)` + 填色 + 按 alpha 包围盒裁切补 10% 留白 → **一次全干净**。
另出**反白版**（同 alpha 填白）供深色底使用。

**推广规则：要什么最终形态，就按那个形态生成，不要在别的形态上做后期转换。**

## 4. 发光字实景图（决策者说服力最强的一步）

1. `image_generate` 出**空背景墙**：暗色石材/水泥、拼缝自然、中央一池柔光，prompt 写死 `no text, no logo, no objects, photorealistic, brand signage mockup backdrop`（横构图）
2. PIL 合成：标志 + 中文标准字 + 全大写英文副标，整块水平居中
3. **光晕两层**：① 复制合成层 → 高斯模糊（约 26-34px @4K）→ 低透明度叠底 ② 再叠一层更大更淡的泛光（约 80-90px 模糊、更低透明度）
4. 字面颜色用近白 `(250,252,255)`；**纯白会显假**
5. **居中要对整个锁标块算** —— 英文行的宽度必须计入字距（`宽 = Σ字符宽 + 字距 × (n-1)`），只按中文行算会整体偏左

## 5. 命名（本轮结论）
- 「天使OPC数字社区」直译 = **Angel OPC Digital Community**；全大写副行 = `ANGEL OPC DIGITAL COMMUNITY`
- 音译 = **TIANSHI OPC DIGITAL COMMUNITY**（中国品牌出海惯例：Huawei / Xiaomi / BYD / NIO）
- 参照视频成品用的是**全大写拼音** `JIYITIAN DESIGN` —— 与"中国企业用汉字做骨架"是同一套逻辑
- 风险提示：`Angel` 英文语境 = 天使投资（angel investor），To B 有歧义

## 6. 字体/渲染坑
- `Source Han Serif SC Heavy`（思源宋体）**缺 U+00B7（`·`）** → 小标签统一用思源黑体（Noto Sans SC Medium），只有大标题用宋体
- PIL 文本度量要用**临时 draw 对象**（`ImageDraw.Draw(Image.new(...))`）在创建画布前测量，否则 `textlength` 不可用
- 画布尺寸依赖文本宽度时要 `int()` 强制取整，否则 `Image.new` 报 `'float' object cannot be interpreted as an integer`
- 本地 HTML 自查截图：Chrome headless `--screenshot` + `--window-size`，再喂 vision 逐个核对（本轮反复验证有效）
