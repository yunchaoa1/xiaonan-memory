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

### 维护类
| 凡哥说 | 加载 |
|--------|------|
| 清理技能 / 技能体检 / 整理技能库 / 技能打架 | skill-library-maintenance（十步流程：盘点→重复检测→停用→合并→修引用→补描述→同步路由表→验证→更新总控台→git同步） |

### 其他业务
| 凡哥说 | 加载 |
|--------|------|
| 爽剧 / 剧本 / 短剧故事 | short-drama-story-engine |
| 网站复刻 | website-cloning + sparkart-clone |
| 帮我回复 / 怎么回她 | barnum-effect |
| 更新ComfyUI | comfyui-update + comfyui |
| 总控台 / 进度 | project-dashboard + dashboard-tree + dual-agent-memory-sync |
| 歌词 / Suno | songwriting-and-ai-music |
| 视频学习 / 分析视频 | video-learning + video-analysis |

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
