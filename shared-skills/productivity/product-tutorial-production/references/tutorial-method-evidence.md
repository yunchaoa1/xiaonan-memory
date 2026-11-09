# 教程制作方法依据（原文摘录 + 适用边界）

2026-11-09 为影剧工坊教程议题核证，四条来源全部读过原文。

## 1. Diátaxis（文档四分类）

出处：<https://diataxis.fr/start-here/>、<https://diataxis.fr/tutorials/>

关键原文：
- 「there are fundamentally four identifiable kinds of documentation, that respond to four different needs」——教程（tutorial）、任务指南（how-to）、参考（reference）、解释（explanation）四类。
- 教程的性质：「A tutorial is always learning-oriented… Its purpose is not to help the user get something done, but to help them learn.」
- 四条硬标准：练习必须 **meaningful**（有成就感）、**successful**（一定做得完）、**logical**（路径合理）、**usefully complete**（该碰的动作和概念都碰到）。
- 原则词：repetition、action、small steps、results early and often、concreteness。
- 明确警告：很多产品根本没有教程，或者「tutorials are often conflated with how-to guides」——两者混写是常见失败原因。

**用于**：分四类入口；手把手教程单独一条主线；每步小、早出结果。

## 2. Guo, Kim & Rubin 2014（教学视频投入度）

出处：ACM L@S'14，第 41-50 页，DOI 10.1145/2556325.2566239
PDF：<https://up.csail.mit.edu/other-pubs/las2014-pguo-engagement.pdf>

规模：**6.9 million video watching sessions**，四门 edX 课程。

原文建议表（逐条）：
- 「Shorter videos are much more engaging.」→「segment videos into chunks **shorter than 6 minutes**」
- 「Videos that intersperse an instructor's talking head with slides are more engaging than slides alone.」→ 在合适时机出现讲解人头
- 「Videos produced with a more personal feel could be more engaging than high-fidelity studio recordings.」→ 因地制宜、不必棚拍
- 另有结论：Khan-style tablet drawings 更投入；「students engage differently with lecture and tutorial videos」（讲课型和教程型视频的观看行为不同，教程型需要更密的操作节奏）。

**适用边界（必须说明）**：这是慕课教学视频的数据，不是产品教程；「短 / 有人讲 / 别过度精修」可直接借用，6 分钟当上限目标而不是铁律数字。

## 3. WCAG 2.2 SC 1.2.2（字幕）

出处：<https://www.w3.org/WAI/WCAG22/Understanding/captions-prerecorded.html>

要点：预录视频的同步字幕是 **A 级（最低合规档）** 要求，内容是「对话 + 说话人识别 + 有意义的声音信息」。不是锦上添花，是底线。

**用于**：视频交付必须带字幕，且字幕按界面原文写；自动识别字幕不能直接出。

## 4. 谷歌技术写作（开头四件事）

出处：<https://developers.google.com/tech-writing/one/documents>

原文要点：
- 「Define the scope of your document clearly, including what it covers and, importantly, **what it does not cover**」
- 「Identify your target audience and their existing knowledge」
- 结论先给，再展开。

**用于**：每页开头四行（讲什么 / 给谁 / 准备 / 不讲）。

## 5. 同类产品结构（Runway Academy）

出处：<https://academy.runwayml.com/>（2026-11-09 实读）

页面实况：Courses（按模块 + 难度分级，如 AI for Advertising 10 modules / Beginner）／Tutorials（单功能快速视频）／Prompt Guide（速查参考）／Help Center（独立，查和排错）。

**用于**：课程、短视频、帮助文档三套分开，对应 Diátaxis 的四类。
