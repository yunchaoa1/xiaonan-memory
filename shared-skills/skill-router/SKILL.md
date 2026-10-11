---
name: skill-router
description: 技能总调度——凡哥提提示词、分镜、运镜、景别、情绪、动作、表情、台词、生图、视频、Seedance、LTX、MV、镜头、灯光、风格、角色、南溟岛、网站复刻等任何创作制作需求时，先加载本技能做任务拆解与技能编排，按路由表逐项加载专项技能，确保不遗漏。凡哥说"出分镜""写提示词""运镜方案""镜头方案""帮我做视频"等模糊需求时必加载。
---

# 技能总调度 · Skill Router

凡哥的模糊需求 → 拆解维度 → 逐项加载专项技能 → 全齐了才动笔。

## 使用规则

1. 凡哥需求涉及创作/制作（提示词、分镜、镜头、运镜、情绪、动作、台词、生图、视频、MV、Seedance、LTX）时，**第一步先加载本技能**。
2. 按下方路由表拆解凡哥需求涉及哪些维度，**逐项加载对应技能**（可以一次加载多个）。
3. 加载完对着"输出前自查清单"打勾，缺维度就补加载，**不遗漏才输出**。
4. 双线规则冲突时以对应技能正文为准：LTX线=英文/全正向/禁否定词；Seedance线=中文/可处理否定。

## 路由表（凡哥说 → 加载）

### 提示词类
| 凡哥说 | 加载 |
|--------|------|
| 镜N提示词 / 给我镜N | prompt-interview（先采访缺项）→ prompt-master-pipeline（八站流水线）→ ltx-video-prompt（弗雷法+定稿模板） |
| 写提示词 / 出提示词 | prompt-master-pipeline → prompt-dictionary（查词库） |
| 抽象情绪词（"氛围感""难过"） | prompt-dictionary（19情绪×265近义词，拆物理动作） |
| 避坑/检查提示词 | ltx-video-prompt 自检清单 + seedance-antislop（去AI套话） |

### 分镜/镜头类
| 凡哥说 | 加载 |
|--------|------|
| 出分镜 / 分镜方案 | shot-language（景别/运镜决策）→ 按维度补：运镜/情绪/动作/台词 |
| 运镜 / 镜头怎么动 | seedance-camera（Seedance线）+ ltx-video-prompt（LTX线运镜铁律：小缓慢/≤45°/禁远景） |
| 景别 / 特写中景 | shot-language + seedance-camera |
| 镜头语言 / 镜头分析 | shot-language |

### 表演类（人物）
| 凡哥说 | 加载 |
|--------|------|
| 表情 / 情绪表达 | prompt-dictionary + ltx-video-prompt（表情递进：笑意→收拢→泛红→涣散） |
| 动作 / 肢体 / 走位 | seedance-motion + ltx-video-prompt（人物动态铁律：三步法/视线轨迹） |
| 台词 / 说话 / 口型 | seedance-audio + seedance-characters + ltx-video-prompt（台词{}格式/声线规则） |
| 角色一致性 | seedance-characters |

### 视频生成类
| 凡哥说 | 加载 |
|--------|------|
| Seedance（任意） | seedance-director（总入口）→ 按需求补子技能 |
| Seedance 续集/接镜 | seedance-continuation + seedance-sequence |
| Seedance 报错/崩了 | seedance-troubleshoot + seedance-filter |
| Seedance 灯光 | seedance-lighting |
| Seedance 风格/特效 | seedance-style + seedance-vfx |
| Seedance 版权/名人 | seedance-copyright |
| LTX（任意） | ltx-video-prompt（总入口） |
| MV / 歌曲视频 | ltx-video-prompt（MV分镜方法论：空镜/叙事/对口型分配）|

### 生图类
| 凡哥说 | 加载 |
|--------|------|
| 生图 / 生成图片 | image-prompt + z-image-prompt + z-image（中文直出规范） |
| 场景图 / 场景统筹 | scene-image-generation（正面平视图→Qwen拓展角度） |
| 人物四视图 | z-image-prompt（四视图格式） |

### IP/世界类
| 凡哥说 | 加载 |
|--------|------|
| 南溟岛 / 世界观 / 反派 | nanming-island + nanming-ip-design + nanmingdao-villain-design + worldbuilding |
| 十二生肖 / 生肖故事 / 动物文化IP | short-drama-story-engine + worldbuilding；角色数量、文件拆分或长期总控再加 creative-project-structure。先区分史料、地域民俗、后世传说和原创设定，不把固定生肖性格当成事实 |
| 角色设计 | nanming-ip-design + worldbuilding |

### 技术/抓取类
| 凡哥说 | 加载 |
|--------|------|
| 抓网页 / 爬取 / 抓数据 / 填表单 / 网页截图 / browser-use / 浏览器自动化 | **agent-browser**（⚠️ 必须 PTY 跑、禁管道；`browser_exec` 挂了就用它顶上） |
| 搜索/抓取被拒 / 403 / 反爬 / SPA 空白 / web_search 报 Keyless Exa 失败 | **local-web-capabilities**（需要真浏览器交互时叠加 `agent-browser`） |
| 抓网页 / 批量抓取 / 爬取太慢 / 把这个页面抓下来 | **lightpanda-fastfetch**（WSL 里的 Lightpanda 无头浏览器，实测 **670ms vs wigolo 34s**；⚠️ **强反爬站抓不到**——那种改用下面这条） |
| **抓不到 / 被拦了 / 403 / 人机验证 / 反爬 / 抖音·小红书这类** | **camoufox-antidetect**（反检测浏览器：**抖音实测 920,392 字节 vs Lightpanda 0 字节**；慢 10–27s，**只用于反爬，不做批量**） |
| **验证码 / 滑块 / 人机验证 / 过不去 / 一直弹验证** | **captcha-solving**（三层：①**不触发** → Camoufox / Scrapling.StealthyFetcher ②**本地识别** → `ddddocr`（字符 3/3 实测、滑块/点选/GPU 都在）③云服务=**付费兜底，未采用**；⚠️ **短信类无解、行为风控只能靠不触发**） |
| 下载大文件 / BT / 磁力 / 种子 / 批量下载 / 下载太慢 / 断点续传 | **aria2-downloads**（aria2c 引擎在 `D:\Hermes\bin\aria2\`；RPC 客户端 `scripts\a2rpc.py`；**先看技能里的边界表**——视频站走 yt-dlp、HF 模型走 `dl_model_resumable.sh`） |
| **看下这个 / 学习一下 / 吸收这个 / 对比一下 / 这个项目怎么样**（凡哥丢来链接·视频·文件） | **content-ingestion**（**按源型强制清单，一维都不能少**：视频→**必转写口播 + 切镜头看画面**、网页→提正文、文档→转 MD；**配验收六问防漏**；⚠️ 视频只抓网页文字=没吸收） |

### 文档/资料类
| 凡哥说 | 加载 |
|--------|------|
| 读这个 PDF / 提取文档内容 / 这个 Word 写了什么 / 转成 Markdown / 扫描件 / 图片里的字 / 资料整理 | **ocr-and-documents**（**先试 `markitdown`**：PDF/DOCX/PPTX/XLSX/图片OCR/音频 一步转 Markdown，2026-10-11 装；转不出再走 pymupdf / marker-pdf 旧流程） |
| Excel / 表格 / 台账 | **xlsx** |
| PPT / 幻灯片 / 汇报稿 | **powerpoint** + docx |
| 生成 PDF / 合并拆分加密 | **pdf** |

### 项目/创作类
| 凡哥说 | 加载 |
|--------|------|
| **我有个新项目想法 / 接了个单怎么落地 / 这个项目该怎么做 / 帮我想想** | **project-idea-to-mindmap**（**四层拆解**：需求→架构→任务→风险；**想清楚再出图**；⚠️ 人力分配不由小南定） |
| 画拓扑图 / 更新拓扑图 / 思维导图 / 项目总图 / XMind / 日报更新 | **project-topology-diagrams**（**XMind `.xmind` 直出**（`xmind_writer.py`，一条命令不用开 XMind）+ draw.io 树形 WBS；含凡哥定稿标准：**左→右、零术语、一级 3-4 条**） |

### 维护类
| 凡哥说 | 加载 |
|--------|------|
| 装工具 / 装库 / 装 CLI / 装上这个 / 能不能装 / 拿下这个项目 | **local-tool-provisioning**（**环境隔离决策树** + 三道闸验证 + 国内镜像表；⚠️ 铁律：**绝不往 Hermes 自己的 venv 塞带重依赖树的包**，重包走独立 venv） |
| **复盘 / 学到了什么 / 为什么又犯 / 你怎么保证不再犯 / 任务收尾** | **self-reflection**（**反思三问**：错在哪→提炼什么原则→落到哪；**经历进 DASHBOARD、原则进技能/记忆**；**反模式扫描**揪重复错误） |
| 清理技能 / 技能体检 / 整理技能库 / 技能打架 | skill-library-maintenance（十步流程：盘点→重复检测→停用→合并→修引用→补描述→同步路由表→验证→更新总控台→git同步） |

### 管理/人际类（凡哥令：先加载对应技能，不凭小南自己思路答）
| 凡哥说 | 加载 |
|--------|------|
| 管理 / 带人 / 人际沟通 / 说服 / 反馈 / 冲突 / 拒绝 / 家庭关系 / 怎么开口 | **carnegie-human-relations**（先走卡耐基六步：P0分诊→P1刹车→P2换位→P3找共同点→P4说话结构→P5落到行动）；涉及考核/带团队/汇报再叠加 **team-management-ops** |
| 帮我回复 / 怎么回她 / 追女生 / 表白 / 她冷淡了 / 聊天卡住 | **mishangwo-attraction-system**（迷上我四步骤分诊；**原 barnum-effect 已并入本技能并归档**） |

### 其他业务
| 凡哥说 | 加载 |
|--------|------|
| 爽剧 / 剧本 / 短剧故事 | short-drama-story-engine |
| 网站复刻 | website-cloning + sparkart-clone |
| 更新ComfyUI | comfyui-update + comfyui |
| 总控台 / 进度 | project-dashboard + dashboard-tree + dual-agent-memory-sync |
| 歌词 / Suno | songwriting-and-ai-music |
| 视频学习 / 分析视频 / **镜头怎么剪的 / 剪辑节奏 / 切了几个镜头 / 分镜还原** | video-learning + video-analysis（**先跑 PySceneDetect 镜头检测**：纯 CPU·0 显存，42MB 视频 14.4 秒出 50 个镜头，2026-10-11 装） |

## 输出前自查清单

- [ ] 凡哥需求涉及哪些维度？（镜头/运镜/情绪/动作/灯光/台词/风格/角色/场景/道具/音乐/剧情）
- [ ] 每个维度对应的技能都加载了吗？（路由表逐项核对）
- [ ] 双线规则确认：LTX线英文全正向禁否定词；Seedance线中文可否定
- [ ] 输出格式：纯文本不带代码框；台词{}包裹；参考图标签原样保留
- [ ] 不确定的缺项先采访凡哥，不脑补

## 注意事项

- 路由表里的技能若已停用（不在 enabled 列表），跳过并用最近似技能替代，并在回复中说明。
- 凡哥需求跨多个维度时，**全部**加载对应技能，不要只加载最像的一个。
- 单次任务技能加载上限视需求复杂度而定，宁可多加载也不遗漏。
