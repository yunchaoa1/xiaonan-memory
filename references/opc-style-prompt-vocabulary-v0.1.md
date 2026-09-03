# OPC 画风提示词书写指南 v0.2（针对 GPT Image 2）

> 依据：OpenAI GPT Image 2 官方 Cookbook + 多模型画风控制实测。
> 核心：GPT Image 2 用「推理层」，风格控制 minimal prompting；但**必须写「笔触」（怎么画的），否则默认漂向 painterly 渐变（写实）**。

## 为什么「笔触」是关键

画风漂移的根因：只写抽象风格词（cel-shaded）时，模型默认走「painterly 渐变」路线（写实皮肤、柔和过渡）。**必须用笔触词明确"画面怎么被画出来"**，才能锁定非写实/手绘感。

两条笔触路径，选错拉不回来：

- **平涂（cel shading）**：平涂色块、明暗硬分界、锐利边缘、几乎无渐变笔触。
  笔触词：`flat color fills`, `hard shadow edges`, `two-tone shadow blocks`, `no gradient brushwork`, `inked outline strokes`
- **绘画感（painterly）**：分层笔触、连续明暗过渡、强体积。
  笔触词：`layered brushstrokes`, `soft painterly brushwork`, `visible brush texture`, `continuous light-to-shadow`

## 通用画风写法（GPT Image 2）

每个画风用「结构化风格声明 + 笔触描写」：

`[风格名] with [笔触描写]; not [相邻风格/写实].`

- 风格名 + 笔触描写（2~3 个关键笔触特征）；
- 一个明确排除词；
- 声明放提示词靠前。

## 五种画风的「风格声明 + 笔触描写」

### 1. 3D动漫电影风（三渲二 / NPR）
- **笔触**：手绘墨线描边 + 平涂色块 + 二分阴影，无渐变笔触（模拟 2D 手绘，但有 3D 体积）。
- **声明**：`3D anime film style with hand-drawn cel-animation brushwork — crisp inked outline strokes, flat brush-painted color fills, two-tone shadow blocks, no gradient brushwork; not photorealistic, not realistic CGI.`
- **漂移风险**：漂向写实 3D/Pixar（"3D" 默认关联写实 CGI）。
- **避坑**：`cel-animation brushwork + no gradient brushwork` 钉死三渲二，禁止单独写 "3D animated film style"。

### 2. 日式动漫风（2D 赛璐璐）
- **笔触**：干净手绘线稿 + 平涂色块 + 硬阴影边缘，无 painterly 渐变。
- **声明**：`2D Japanese anime with clean hand-drawn line art, bold ink linework, flat cel-painted color fills, hard shadow edges; not 3D render, not photorealistic.`
- **漂移风险**：漂向 3D 渲染（模型默认 3D）、漂向写实。
- **避坑**：`2D hand-drawn line art + not 3D render`。

### 3. 韩式彩漫/条漫风（manhwa / webtoon）
- **笔触**：干净数字线稿 + 柔和数字笔触渐变（介于平涂与 painterly 之间，偏柔和立体）。
- **声明**：`Korean webtoon / manhwa with clean digital line work, soft digital brush shading, detailed iris brushwork; not manga, not photorealistic.`
- **漂移风险**：漂向日式动漫（manga）。韩式=全彩+柔和立体，日式=平涂+重线稿。
- **避坑**：`soft digital brush shading + detailed iris` 区分日式，`not manga` 钉死边界。

### 4. 国风水墨/工笔风
- **笔触**：毛笔笔触 + 墨韵 + 宣纸肌理。水墨写意用 `expressive loose brushwork / wet-on-wet washes / dry brush`；工笔用 `fine linework / mineral color`。
- **声明**：`Chinese ink wash (sumi-e) with expressive loose brushwork, wet-on-wet ink washes, dry brush texture, visible rice-paper texture, fine gongbi linework; not photorealistic, not glossy, not 3D render.`
- **漂移风险**：漂向日式浮世绘、写实水彩、现代插画。
- **避坑**：`Chinese + rice-paper texture + loose brushwork` 锚定国风，区分日式。

### 5. 写实电影概念设计风
- **笔触**：painterly 分层笔触 + 电影光影（这是唯一走 painterly 路线的画风，但要"概念设计"而非"照片"）。
- **声明**：`cinematic concept art with painterly brushwork, layered brushstrokes, cinematic three-point lighting, color grading; not casual snapshot photo.`
- **漂移风险**：漂向普通手机照片（缺概念设计艺术感）、漂向 3D 渲染（缺电影感）。
- **避坑**：`concept art + painterly brushwork + cinematic lighting` 拉出电影质感。

## 使用规则

- 生成任何资产图，`[STYLE]` 填上面对应画风的「风格声明 + 笔触描写」，不要堆砌十几个关键词。
- 风格声明放提示词靠前（主体描述之前）。
- 五种画风一次只用一个；人物/场景/道具共用同一套声明。
- 禁止品牌词（Pixar/Disney/Ghibli），直接描述视觉特征 + 笔触。
