# 用生图模型出「品牌标记/LOGO 稿」—— prompt 模板 + 精确单色透明后处理

> 本机实测管线（2026-09-11 天使OPC数字社区 logo 首战）。适用：给品牌/平台/产品出**标记（mark）**阶段的创意发散去重。
> 原生归属技能是 `logo-generator`（但它当前是用户所有，后台不可写），故此处收录为跨技能可用的方法。

> ⚠️ **本文件的 prompt 模板是「单色扁平」路线，天花板有限。**
> 同项目后续实测：这条路线连续三轮被用户判「土 / 没高级感 / 像素材库」。
> **用户要「高级感 / 设计感 / 像大牌」时，别再用下面这套扁平单色模板** ——
> 改走 `references/brand-style-directions-and-presentation.md`
> （材质 / 光影 / 色彩层次 / 中文字标 / 发布会级呈现 + 决策层级 + 决策者选型协议）。
> 本文件的定位收窄为：概念**发散去重**阶段的快速铺量，以及确实需要单色稿时的后处理与质检。

## 什么时候该走生图，而不是纯手绘矢量

纯几何 SVG 稿（尤其单色）有高频翻车模式：**撞"素材库脸"**。
特征：元素是**能一眼叫出名字的具象物**（翅膀 / 盾 / 靶心 / 日出 / 分子 / 维恩图 / 圆内平行线），配上严格对称 + 满构图 + 线宽偏粗。

用户判「土 / 没有高级感 / 没有设计感」时，**不要只在手绘矢量里再来一轮** ——
并行开一条生图线，两条线的稿子放同一页面让用户对比，比连续盲猜省一整轮。

## 调用方式

Hermes 原生 `image_generate`（provider: openai / model: gpt-image-2-medium，方图 3840×3840）。
**一次批量 4–6 张**：同一轮里发多个 `image_generate` 调用即可并行。
每条 prompt 只描述**一个**视觉动作，不要叠比喻。

### prompt 模板（实测有效）

```
<概念：一句话写清这一个视觉动作>
flat vector logo icon, single flat color <目标色，如 deep azure blue #0052d9> on pure white background,
no gradient, no shadow, no 3D, no glow, no text, no letters, no words, no border frame, no mockup,
centered composition, generous white margins, bold uniform stroke weight,
strict geometric construction, Swiss Bauhaus brand identity, high-end minimalist, crisp clean vector edges
```

实测出过稿的概念句：
- `An abstract angel wing reduced to TWO smooth mirrored geometric arcs sweeping upward from a narrow common base`
- `A bold perfect ring with one deliberate clean gap at the top, and a single solid dot resting exactly in the ring's center`
- `Two thick rounded-square shapes overlapping at a 45 degree angle so their intersection forms a crisp diamond in the middle`
- `Three solid dots of clearly decreasing size arranged along one smooth rising diagonal line, connected by a single thin straight line`

## 后处理：白底纯色稿 → 精确目标色 + 真透明（精确解）

对「白底 + 纯色图形」的稿子，`alpha = 255 - min(R,G,B)` 是**数学上精确**的：

- 白底 (255,255,255) → alpha 0
- 纯色 #0052d9 = (0,82,217) → min=0 → alpha 255
- 抗锯齿边缘是两者线性混合，min 通道恰好给出线性 alpha → **边缘天然正确，不需要阈值抠图**

```python
from PIL import Image
im = Image.open(src).convert("RGBA")
px = im.load()
for y in range(im.height):
    for x in range(im.width):
        r, g, b, _ = px[x, y]
        a = 255 - min(r, g, b)          # 精确 alpha
        if a < 12:                       # 清掉纸纹/噪点
            a = 0
        px[x, y] = (TARGET_R, TARGET_G, TARGET_B, a)   # 整体填目标色
# 再：裁 alpha 包围盒 -> 补约 8% 均匀边距成正方形 -> resize 1024
# 再出 64/32/16 缩放实测（favicon 场景）
```

## 必须做的质检

1. **后处理前先看原图**：模型会偷偷加圆角底、细边框、微渐变 —— 后处理会一并保留。
2. 处理完把拼版丢给 `vision_analyze` **逐稿评**。本机实测靠这步挑出了「像牛头」「像上传按钮」「细线在 16px 整根消失」的废稿。
3. 必看 16px 小图：细连接线会消失 → prompt 里必须写 `bold uniform stroke weight`。

## 诚实边界（别说成已支持）

- 这条线出的是**位图**。本次**没有做描摹/矢量化**，也没实测任何矢量化工具 —— 用户要裁矢量就另找工具并**先实测再承诺**。
- 模型偶尔无视 `no text / no letters`，出稿后要肉眼确认没有多余字母笔画。

## 经验回流

好用的概念句回填到本文件；废稿类型回填到「什么时候该走生图」的特征清单。
