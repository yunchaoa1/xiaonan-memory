# 来源登记（原样安装，未做任何改动）

| 项 | 内容 |
|---|---|
| **技能名** | `sd-storyboard-engine`（漫剧老李 · 分镜引擎） |
| **来源** | https://github.com/lixiaoxiao9888-create/manju-laoli-skill |
| **原作者** | 漫剧老李（lixiaoxiao9888-create） |
| **许可证** | MIT |
| **版本** | V7.5.0-SLIM（套装 V7.4.26） |
| **安装日期** | 2026-11-18 |
| **安装方式** | 原样下载，**一个字未改** |
| **仓库状态** | ★2,145 / 256 forks / 创建 2026-08-15 / 最后推送 2026-11-15 |

## 装了什么

```
sd-storyboard-engine/
├── SKILL.md                                    37,187  流程（原样）
├── references/
│   ├── model-adapters.md                       85,367  ★从总控借的，七段式投喂格式（含 H3 适配）
│   ├── short-drama-camera-system.md            56,517  机位体系
│   ├── shot-economy-and-acting.md              42,440  镜头经济性与表演
│   ├── storyboard-sheet-template.md            22,455  故事板模板
│   ├── p45-previs-storyboard.md                11,262  P4.5 预演故事板
│   ├── plot-deduction-grid.md                   9,970  剧情分镜格
│   ├── scene-space-adaptation.md                7,197  场景空间适配
│   └── segment-linkage.md                         870  段间衔接
└── scripts/
    └── check_p45.py                            16,221  机检脚本（P450~P458）
```

**注意**：`model-adapters.md` 原在 `short-drama-director/references/`（总控目录），因分镜输出必须按它封装投喂词，一并借用。**这不是改动，是把依赖补齐。**

## 它的独特价值（我们没有的）

1. **台词承接契约**：上游剧本每一句台词默认必须原样进分镜稿，**分镜层无权删除/合并/改写**。要精简只能出「精简建议清单」并征询同意。
   *（它记的教训：上游 40 句台词，分镜稿只留 19 句，用户完全不知情）*
2. **剪辑决定禁止越权**：分镜层不得决定切不切镜，不得用「多画一格」暗示未授权切镜。
3. **影像基底感知**：3D CG **禁「特写×平视正面」**（无纵深/塑料感/恐怖谷）；真人守 1/3 配额；2D 同场 ≤2 次。**直接对应我们的 3D 国漫风。**
4. **动作相位七态**：起势/过程/接触/顶点/结果/反应/出口 —— 故事板按相位拆格，**格数 = 镜数**（不是机械九宫格）。
5. **出口帧 = 下段入口帧**：段间衔接的硬约束。
6. **机检可跑**：`scripts/check_p45.py`（P450~P458），不是纸面清单。
7. **物理可行性 > 叙事情绪 > 多样性指标**（冲突时前者压倒后者）。

## 与现有技能的关系

| 技能 | 管什么 | 状态 |
|---|---|---|
| **sd-storyboard-engine**（新装） | **剧本→文字分镜 + 故事板图**（专业级，带机检） | ⏳ 待实测 |
| `h3-storyboard` | 怎么想（构图优先、一镜一主节拍、表情生理顺序） | ⏳ 待实测（105KB 太大） |
| `screenplay-to-15s-storyboard-opc-test` | 我们自己的 15 秒分镜规则 | 🔍 待对比 |
| `storyboard-keyframe-opc-test` | 宫格关键帧**图**（Seedream 出图） | 在used |
| `h3-video-prompt` | H3 提示词语法 | 在用 |

## 已知限制

- **SKILL.md 37KB**：单次加载可能触发 PRUNED 被剪（1.2-1.8 万字符就会剪）。**处置**：被剪时手动 `read_file` 读全文，或先读关键章节。
- **原套装是 11 个技能**（总控 + 10 引擎），这里**只装了分镜引擎**。它的 description 写着"通常从总控进入"，单独用时总控的锁系统（模型版本/画幅/交付形态/段缝衔接）需我们自己定。
- **依赖总控的机检口径 C1~C33**（`short-drama-director/scripts/validate_prompt.py` 未装）。

## 评估待办

- [ ] 拿真实剧本实测拆镜
- [ ] 实测 `check_p45.py` 能否跑
- [ ] 与 `h3-storyboard`、`screenplay-to-15s-storyboard-opc-test` 三方对比
- [ ] 好用 → 挂路由；不好用 → 删掉换下一个
