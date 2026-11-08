# GitHub 生态扫描 · 2026-11（H3 提示词改写 / 爽剧剧本+分镜）

两次「帮我在 GitHub 上找找有没有 X 这类项目」的完整候选清单与判词。
**全部只读 README，未安装、未运行** —— 引用时必须带这句。

取数手法见 SKILL.md 第一节 4️⃣（中文 query 要 percent-encode、搜索接口 10 次/分钟、
`topic:` 优先、README 用 `Accept: application/vnd.github.raw`、按关键词扫行不读全文）。

---

## 一、MiniMax H3：自然语言 → 专业提示词

| 仓库 | ★ | 最后 push | 形态 | 判词 |
|---|---|---|---|---|
| `MiniMax-AI/MiniMax-H3` | 11515 | 2026-10-28 | 官方 | **唯一权威底稿**。自带 `skills/h3-prompt-writing`，装：`npx skills add https://github.com/MiniMax-AI/MiniMax-H3 --skill h3-prompt-writing`；内含 `references/base-en.txt`（文本/关键帧模式）与 `ref-en.txt`（全参考）。官方 README 把系统写成三模块：H3-Context-IR → H3-Base(768p) → H3-Regenerate-2K |
| `T8mars/comfyui-minimax-h3-prompt-enhancer-T8` | 390 | 2026-11-02 | ComfyUI 节点 | 中文圈功能最全：色彩风格库（200 配色）、导演拍法、分镜强化、首尾帧 Hybrid、语音参考、质量自检。README 夹带自家 API 小铺推广链接，要挑。1000+ 行文档，读起来费劲 |
| `benjiyaya/Minimax-H3-Prompt-AgentSkill` | 160 | 2026-08-06 | Agent Skill | 星最多的技能型。自动判五模式（Ref2VA/T2VA/I2VA/FL2VA/L2VA）+ 七维度创意增强（相机身份/视觉质感/节奏弧线/角色细节/空间地理/连续性/声音设计） |
| `hyukudan/ComfyUI-MiniMax-H3-Prompt-Enhancer` | 24 | 2026-08-29 | ComfyUI 节点 | **校验+自修复型，不是加词型**：六段/三段合同结构化校验、对白 100% 逐字、17 语言 88 方言、音频参考绑定 `<Audio N>`→`<Subject N> (Sx)`、标题字幕确定性配方、GPL-3.0、自报 764 测试通过。批量稳定优先看它 |
| `ye4wzp/minimax-h3-prompt-skill` | 12 | 2026-08-07 | Agent Skill（中文） | 自称「不是提示词库，是决策补齐器」：9 项默认值（时长/风格锚/镜头数/前2秒/三层声音/台词/素材分工/画幅）、7 类拒绝触发、五模式对齐模板。自认**案例库是空的**，多为合成结论 |
| `smithysw7/minimax-h3-video-prompt` | 2 | 2026-08-06 | Hermes Skill（中文默认） | 官方格式 + 五模式路由 + Revision Compiler（改稿全量重编译、不留补丁）+ 中文运镜对照表 12 种 |
| `chiphoton/MiniMax-H3-Codex-Drama` | 60 | 2026-09-28 | Codex 插件 | 角色设定→分镜→ComfyUI 整条生产线 |
| `xiaowuapple-pixel/ComfyUI-Prompt-Enhancer` | 6 | 2026-10-01 | ComfyUI 节点 | 通用加词型，含 H3 模板 |
| `bobdoylemedia-ai/hailuo-h3-prompt-builder` | 7 | 2026-08-09 | 本地网页 | 手动填表拼提示词，不含改写模型 |

**判词**：格式权威只用官方；「自然语言→决策补齐」的思路看 ye4wzp；要稳定批量不出格式错看 hyukudan 的校验型。

**一个待验的说法**（第三方 README 提出，**未经实测，不要当规则用**）：
> 走海螺官网 / MiniMax API 时 Context-IR 在跑，应写**中文自然语言**、只补齐决策，手工结构化会跟它打架；
> 走本地 ComfyUI / 开源权重时没有 Context-IR，**必须写完整英文结构化格式**。

这与现有 `h3-video-prompt` 的「国内平台与本地节点规则同一套」不一致。
**正确动作：先拿官方 `base-en.txt` / `ref-en.txt` 和本地实拍对照，再决定改不改规则，绝不因第三方说法动铁律。**

---

## 二、爽剧 / 短剧：剧本 + 分镜

| 仓库 | ★ | 最后 push | 覆盖 | 判词 |
|---|---|---|---|---|
| `zenstory-ai/drama-skills` | 3833 | 2026-11-06 | 点子/原著→分集剧本→分镜→图片/视频提示词→成片 | 十二技能；五份 md 分工（剧本/视觉设定/分镜/图片提示词/视频提示词）；**跨文件一致性校验**（分镜 2s 与视频提示词 3s 不一致直接报错）；公开 68 秒竖屏样片 = 有实证 |
| `0xsline/short-drama` | 1565 | 2026-04-17 | 剧本层 | **爽点最硬**：五种钩子（悬念/反转/情绪/信息/危机）、8 类爽感矩阵配比（打脸/逆袭/甜宠/虐心/悬疑/燃/搞笑/感动）、四层反派（隐藏反派压后 1/3）、付费卡点 10-15%、🔥重点集 25-35%、题材→第1集钩子→卡点类型对照表。**不出分镜** |
| `A-cat-with-carrots/OnlyShot` | 363 | 2026-07-07 | 一句话→剧本/分镜/分镜图/视频/剪辑 | 「红果必爆 7 招」**秒级时间轴**：对抗式开场 / 30s 爆破 / 60s 爽点 / 90s 反转 / 120s 爽点 / 150s 钩子 / 180s 倒计时，写进 `节奏地图.json`；分镜图当视频首帧（3 积分 vs 55 积分，省 1/18）；17 个失败模式 |
| `doublesq97-ui/su-ai-short-drama` | 66 | 2026-07-28 | 编剧/导演/选角/分镜 | 男频女频拆两套配置 + 岗位制。男频=身份兑现/秩序重建，女频=情绪回报/偏爱与信任。受众区分做得比多数准 |
| `chengbenchao/short-drama-script` | 38 | 2026-05-06 | 剧本+大纲 | **四级卡点**（一卡/二卡/三卡/日常卡点）+ 男频爽文 22 种套路库 + 卡点标注。只到剧本 |
| `Liuxiangjian-ai/shuangwen-skill` | 11 | 2026-05-05 | 单章爽文→短剧分镜 | 纯爽文血统：选 5 个选项出约 2000 字；结构固定「深度羞辱→反派加码→分层打脸→章末钩子」；只做单章不做整部 |
| `UnderleveledBuilder/awesome-short-drama-skills` | 1861 | 2026-11-03 | 索引 | 短剧/漫剧 skill 精选目录，当雷达用 |
| `Vi7QY/screenwriter-skill` | 98 | 2026-04-12 | 审稿 | 37 条实战规则 |
| `kylvia/mimeng-skill` | 24 | 2026-05-26 | 情绪设计 | 咪蒙表达 DNA，102 篇语料 + 听花岛短剧业务数据蒸馏 |
| `zenstory-ai/oh-story-claudecode` | 8336 | 2026-11-06 | 网文层 | 扫榜/拆文/写正文/去 AI 味，与 drama-skills 同团队，接起来是「网文→本子→分镜」全链 |

**判词**：三块互补，不重复 —— 爽点怎么排（0xsline）／节奏卡死 + 分镜落地（OnlyShot）／工程化防前后不一致（zenstory）。

---

## 三、这类搜索的可复用结论

1. **中文全领域搜「爽剧」基本无效**：返回的是房价、书单、Telegram 群。有效入口是 `topic:ai-short-drama`（62 个对口）与「短剧 分镜」精确组合。
2. **星数与形态要一起看**：最高星是「目录/平台」而非「可直接用的 skill」，说明这个领域大家在找资料、成品少 → 是机会也是坑（同 SKILL.md 第一节 3️⃣ 的诊断法）。
3. **有公开样片的项目可信度高一档**（zenstory 的 68 秒样片），只有文档的只能算「设计思路」，不能说成「能用」。
4. 用户要「地址发给同事」时：**URL 必须反链接化**（`github[.]com/owner/repo`），否则桌面版会自动开窗弹窗；并说明「发的时候把方括号去掉」。
