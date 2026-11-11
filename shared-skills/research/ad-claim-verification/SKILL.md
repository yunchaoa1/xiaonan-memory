---
name: ad-claim-verification
description: Verify an ad or product claim's credibility. 广告/宣称核查.
version: 1.0.0
author: Hermes Agent (小南)
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Research, FactCheck, Advertising, China, Compliance, Evidence]
    category: research
    related_skills: [video-analysis, grounded-citations, blocked-page-recovery]
---

# Ad / Claim Verification（广告与宣称核查）

Answer "这个靠谱吗？" with an evidence chain, not an opinion. The user usually
arrives with a **second-hand framing** ("央视打的广告", "科学界改写了X") that is
partly wrong; correcting the framing *with evidence* is half the deliverable.

## When to Use

中文触发：凡哥发来一条抖音/小红书/公众号链接、截图或广告，问"这个靠谱吗""真的假的"
"是不是智商税""太夸张了吧"；或某个产品宣称"科学突破""权威认证""央视/国家级背书"。

Also: any health, 功效, medical, financial, or safety claim you are asked to judge.

Related: `grounded-citations` (bundled — citation plumbing), `video-analysis`
(getting the actual ad footage + fine print when the claim lives in a video).

## Procedure

① **Get the ad itself, verbatim.** Do not work from the user's summary.
   - Video link → `video-analysis` skill: capture the media (Playwright route for
     抖音/SPA pages), then read 大字 + 字幕 + **片尾免责小字** frame by frame.
   - Record the **real publisher**: `page.title()` and `meta[name=description]`
     name the account and the post date ("… - 央视网于20260928发布在抖音"). A
     "央视" impression is often just a paid slot on a media outlet's own account.
   - Screenshot the claim + the fine print and keep them as evidence files.

② **Write down the claims as quoted lines, each with its timestamp/source.**
   Separate three different accusations that must not be mixed:
   | Layer | Question | Typical answer |
   |---|---|---|
   | 主体 | Who really published/branded it? Is it labelled 广告? | often differs from the user's framing |
   | 宣称 | Does the claim cross the legal boundary for that product class? | 越界 = the real violation |
   | 科学 | Does the cited science exist, and at what stage? | 实验室/临床 ≠ 上市商品 |

③ **Run the regulatory boundary first — it is the fastest hard verdict.**
   For China 化妆品/食品/保健/医疗器械 claims see
   `references/china-claims-regulatory-baseline.md` (功效类别、允许宣称的措辞、
   特证/备案怎么查、权威媒体"广告位 ≠ 背书"的官方依据). Quote the rule text.

   **⭐ 一票定性的速判：看批号反推功能边界（不用查配方）。**

   | 批号形态 | 类别 | 能宣称/能含什么 |
   |---|---|---|
   | `国妆特字G…` / `国妆特进字…` | 特殊化妆品 | 防晒、祛斑美白、染发、烫发、防脱发 —— **只有这一类才能加防晒剂** |
   | `国妆网备字…` / `<省简称>G妆网备字…`（如 `京G妆网备字`） | 普通化妆品 | **法规上不得添加防晒剂** → 保湿乳/面霜/身体乳只要是这个批号，**不必查成分表就能断定它没有防晒能力** |

   用途：商家把"含维E""滋润修护"讲成"能防晒/抗光老"时，批号就是反证；
   用户拿一瓶普通备案的乳问"够不够"，也能当场给答案。
   同一逻辑可推到其他品类：普通备案不能宣称美白祛斑、不能宣称防脱。

   → 商品页被拦 / 成分表查不到时怎么继续拿事实：见
   `references/product-facts-and-batch-numbers.md`（批号表 · 短链 resolved-URL 取元数据 ·
   拍瓶身取证 · 药监局备案核验 · 三条判断纪律）
   ⚠️ 以批号为准，不以商品标题为准——标题里的"防晒"经常只是关键词堆砌。

④ **Build the brand/company track record as a timeline.** 处罚记录、监管曝光、
   投诉与平台处置、财报结构（营销费用率 vs 研发费用率、营收/利润/股价）。
   一条"越卖不动、话术越激进"的因果链比任何形容词都有说服力。
   Search terms that work: `<品牌> 处罚`, `<品牌> 虚假宣传 投诉`, `<品牌> 曝光 回应`,
   `<品牌> 财报 销售费用率`.

⑤ **Layer the science claim.** Sort it into three buckets and say which bucket the
   ad borrows from: 教科书级生理常识 → 实验室/临床阶段前沿（专利已申、人体试验未做、
   未上市）→ 已上市且有循证的手段（药品/处方药/械字号）。Name what actually works
   in the last bucket so the answer is useful, not just debunking.

⑥ **Report in 凡哥's format**: 一句话结论 → 素材原话/画面证据（表）→ 免责小字原文
   → 前科时间线（表）→ 给用户的三条可执行建议 → 证据文件的**绝对路径**。
   大白话、结论先行、不堆术语；截图用 `MEDIA:<绝对路径>` 直接发给他。

## Pitfalls

- **顺着用户的框架答。** "央视打的广告" 要先核实发布主体；用证据温和纠正（"严格说这是投在央视网抖音号上的付费广告，标题自带（广告）"），别为了顺口把结论建立在错的框架上。
- **拿搜索摘要当结论。** `web_search` 的 description 常来自自媒体/财经号。监管口径必须落到 药监局/市场监管/新华网/中国医药报 这类源；自媒体只用来找线索。
- **把"持证为真"和"功效宣称合法"混为一谈。** 特证/备案是真的，不等于广告里那句话合法。要分别说清：✅有证 ✅备案功效只到A ❌宣称越界到B。
- **漏读片尾免责小字。** 广告自己写的"仅为产品突破点描述""效果因人而异""非新闻人员 非医疗人员 部分内容含AI生成""内容仅为广告创意 并无其它暗示"往往就是结论——务必原文引用。
- **OCR/截图里不确定的编号不要写成确定值。** 看不清就说"画面显示某报告编号/变化率36.87%"，绝不杜撰证书号、专利号、检测机构编号。专利证书类要区分"配方/制备方法专利"与"功效证据"。
- **"权威媒体曝光"与"权威媒体背书"要分开陈述。** 同一家媒体既做新闻调查又卖广告位；不要把广告位读成认可，也不要把曝光当成定论（若品牌否认、监管无公开结论，就说"至今无公开统一结论"）。
- **只答"智商税"没用。** 一定给出分级结论：可以用作什么、不能指望什么、真有问题先去哪里（如脱发→皮肤科）。
- **把商业判断写成道德判断。** 财报、费用结构、股价是证据；"黑心"不是。
- **不要因为来源在卖课/带货就整条丢掉，也不要整条照收。** 正确做法是**按段拆**：平台机制、用户画像、行业规则这类可验证的情报照收；成交话术（"评论区扣XX领资料""进主页粉丝群找助理"）和无法核实的战绩数字（"一小时20个号""一下午三小时就在一起"）整段剔除。识别特征：内容每隔几分钟就插一次引流动作 = 这条内容的目的就是卖课，不是科普。
- **效率类数字默认不可核实，不进结论。** 成功率、成交率、涨粉数、转化率，除非有第三方数据源，否则写"博主自称，无法核实"。这一点在"导师型"视频里最常被忽略，因为数字听起来特别具体。

## Verification

Deliverable is done when every sentence of the verdict points at either
(a) 素材画面原话, (b) 监管文件/官方声明原文, or (c) 权威媒体报道 — and at least
one of them is a primary/regulatory source, not a content-farm summary. If a
claim cannot be sourced, mark it 未核实/存疑 rather than smoothing it over.
