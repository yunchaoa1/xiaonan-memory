---
name: book-distillation
description: 蒸馏一本书成可执行skill时用。四步法:类型判定→提取→结构化→边界。
version: 2.0.0
author: 小南
license: internal
metadata:
  hermes:
    tags: [蒸馏, 读书, skill制作, 知识管理]
    related_skills: [carnegie-human-relations, mishangwo-attraction-system, hermes-agent-skill-authoring, skill-library-maintenance]
---

# 图书蒸馏 · 四步蒸书法 v2

把一本书蒸成**可执行的方法论技能**（不是摘要、不是概念词条库）。

> **v2（2026-10-11）**：吸收开源项目 `book-to-skill`（33.8k★ / MIT）的**机制**——脚本化提取、按章按需加载、token 预算、成本预检、大书切片、折叠更新、生成后规范体检。
> **保留我们的判断层**（它没有的）：分诊表、边界写厚、反例、查重划界、中文触发、双产物（docx 给凡哥）、DASHBOARD 回流。
> 它的 topic index 是「术语→章节」＝**检索**；我们的分诊表是「症状→流程」＝**判断**。别把判断换成检索。

## 何时加载
- 凡哥说"蒸馏这本书""把《X》蒸成 skill"
- 凡哥发来一段蒸馏提示词（多为四步法：类型判定→提取→结构化→适用边界）
- 已有原文（PDF/EPUB/DOCX/TXT），要产出可复用技能

## 铁律（八条）
1. **蒸的是"能执行的方法"** —— 每条都落到"遇到什么情况，做什么动作"
2. **忠于原书，不编造** —— 作者没说的原理不替他说；推断必须在"我的分析"层标明
3. **提取结构，不是摘要** —— 保留作者**精确命名**："5个为什么" ≠ "多问几次为什么"
4. **密度优先，绝不填空凑数** —— 1,000 tokens 的精华胜过 10,000 tokens 的摘录
5. **实践者口吻** —— 写"当 X 时用 Y"，不写"书中解释了 X"
6. **绝不抄原文** —— 综合、压缩、提信号；金句是佐证，不是主体
7. **边蒸边标出处** —— 每条方法论标原书章节（第几章/第几节），事后补不回来
8. **边界比方法值钱** —— 边界与反例必须写厚，这是我们的差异化，不许一段打发

---

## 第一步 · 类型判定（先判定，再动手）

| 类型 | 特征 | 提取目标 | 提取模式 | 默认深度 |
|---|---|---|---|---|
| **工具书** | 有步骤、流程、公式、清单 | 方法论：可执行步骤/流程/原则 | `technical` | study |
| **非工具书** | 讲思考方式、决策逻辑 | 思维框架：作者的思考方式/分析框架 | `text` | study |
| **混合型**（最常见） | 主干是方法，外层是心法 | 以主干定结构，心法作「底层机制」章节 | `text` | study |

- `technical` = 保留表格版式，章节里要有「代码/公式/参考表」区块
- `text` = 最快路径，章节聚焦「框架/心智模型/要点」
- **判定结果要明确写出来给凡哥看**，别闷头蒸。凡哥只说要查资料/速览 → 走「仅分析」模式（只出提取报告，不生成技能）。

## 第二步 · 提取（脚本化，不再一个字一个字读）

```bash
# 0) 先看环境有哪些提取器（第一次用/报错时）
python "D:\Hermes\skills\knowledge-management\book-distillation\scripts\extract_book.py" --check

# 1) 提取（文件/目录/glob 都行，可多个源合并）
python "D:\Hermes\skills\knowledge-management\book-distillation\scripts\extract_book.py" \
  "<书.pdf>" --mode text --out "<工作目录>"
```

产出（脚本会打印三个路径，**以它打印的为准**）：
- `full_text.txt` —— 各源合并全文，每源前有 `===== SOURCE: 文件名 =====` 分隔
- `metadata.json` —— 每源 `sha256` / 字符 / 词数 / 估算 tokens / 提取器 / 告警 + 汇总

硬规则：
- **先读 `metadata.json` 确认提取的就是你要的那本书**（`sources[].file` 对得上）再动手
- 坏源会被跳过并警告，其余照常 —— 见 `metadata.json` 的 `skipped`
- 扫描版 PDF 抽不出文本（脚本会明确告警）→ 先 `ocrmypdf in.pdf out.pdf` 再喂进来
- 缺库不用慌：降级链已覆盖本机已有的 pdftotext / python-docx / bs4；要更高质量再按 `--check` 的提示补装

## 第三步 · 成本预检（先报价，再生成）

读完 `metadata.json` 后，**先给凡哥报一次账，等他点头再生成**：

```
📖 源: <N> 个（<文件名列表>）
📄 合计: ~<页数> 页 / ~<词数> 词 / ~<tokens> tokens
🧩 预计章节: ~<N> 章
💰 预计产出: 主SKILL ~4k + 章节 ~<N×预算>k + 三件套 ~5k tokens
⏱ 预计: ~<N> 分钟
➡ 继续生成？还是先只出「提取报告」看一眼？
```

书小（<20k tokens）可跳过报价直接干，但要一句话说明。

## 第四步 · 结构分析（大书不许整本读入）

- **<50k tokens**：一次读 `full_text.txt` 没问题
- **>50k tokens**：**别整本灌进上下文**（200 页 ≈ 75k tokens，按 28 章重读一遍 = ~2M tokens 白烧）。用切片：

```bash
wc -w full_text.txt                                        # 先看体量
grep -n -E "^\s*(第[一二三四五六七八九十]+[章节]|Chapter|CHAPTER)\s*[0-9一二三四五六七八九十]*" full_text.txt | head -40   # 拿章节偏移
sed -n '120,340p' full_text.txt                            # 只切要用的章
grep -c -i "关键词" full_text.txt                           # 写入前先证明确实讲过，别脑补
```
        （Windows 下也可直接 `read_file(path, offset, limit)` 按行取。）

要识别：书名、作者、**章节结构**、核心主题、章节数。有目录页就先读目录。

## 第五步 · 产物结构（多文件 + 按需加载）

技能的「主文件」要小、要前置；厚的部分拆出去按需读。**Hermes 原生支持**：主 SKILL.md 用 `[ref:名字]` 引用 `references/名字.md`，按需 `skill_view(name=..., file_path="references/xxx.md")` 加载。

```
D:\Hermes\skills\<category>\<skill-name>\
├── SKILL.md                    # <4,000 tokens：核心方法论 + 分诊表 + 章节索引 + 主题索引
└── references\
    ├── ch01-<slug>.md          # 每章一文件，按需加载（主文件里写 [ref:ch01-<slug>]）
    ├── ch02-<slug>.md
    ├── glossary.md             # 术语表，字母序，≤1,500 tokens：**术语** — 定义（第N章）
    ├── patterns.md             # 技法/模式，≤2,000 tokens：用法/步骤/权衡
    └── cheatsheet.md           # ≤1,200 tokens —— 见下，别写成词表
```

**每章 token 预算矩阵**（预算按 类型×深度 取；是目标不是硬上限，薄的章就让它薄，**严禁凑字数**）：

| | reference（查阅型） | study（研读型，默认） |
|---|---|---|
| text | 800–1,200 | 1,000–1,800 |
| technical | 1,200–1,800 | 2,000–3,000 |

`study` 深度是靠**内容**挣的，不是靠字数：每章至少复现 1 个书中实例（填好的模板/一段对话/一次决策），加写 1–2 个框架的「怎么用/什么时候翻车」。

**cheatsheet.md 是最见功力的一层** —— 不是术语表（那是 glossary），而是**作者的判断力**，按优先级：
1. **决策规则** ——「当 X，就做 Y，因为 Z」
2. **决策树/流程**（超两个分支时）
3. **权衡矩阵** —— 选项按作者在意的维度打分
4. **阈值与默认值** —— 作者commit的具体数字/比例（如"函数别超 20 行"）
5. **气味信号** —— 快速识别处境的启发式（"看到 X，多半已经掉进 Y"）

**章节模板**见 `templates/chapter-template.md`（含我们特有的「边界与反例」区块）。

## 第六步 · 主 SKILL.md 怎么写

- **前加载**：最重要的放最前（压缩从尾部截断，越前越保得住）
- 必备四段：核心方法论 / **分诊表（症状→走哪条流程）** / 章节索引（`[ref:chNN-<slug>]` 表格）/ 主题索引（术语→章号）
- description ≤60 字符、**中文触发词放最前**（决定以后能不能被自动路由到）
- 加一节「边界与适用条件」，别只写"看情况"

## 第七步 · 边界与反例（我们比开源那套厚的地方）

必须回答：
- 什么场景下有效
- **什么场景下会翻车**（要具体到可识别的情形，不许写"视情况而定"）
- 需要什么前提条件
- 作者自己承认的局限
- 与凡哥现实处境的差距（书里的时代/文化/行业背景 vs 现在）

工具书还要逐条给**反例**：什么时候这条会失效、甚至反噬。

## 第八步 · 查重划界 → 交付 → 验证

1. **查重划界**：`search_files` 全库搜关键词，判断是否跟现有技能打架——重叠就**合并**，或**划清触发边界**（防蒸出第二个打架的技能）
2. **双产物**：
   - 技能 → `D:\Hermes\skills\<category>\<skill-name>\`（给自己用）
   - 成品文档 `.md` + `.docx` → `D:\Documents\我的文档\04_规范与工具\蒸馏\`（给凡哥看/存档，python-docx，注意中文字体）
3. **规范体检**（生成后必跑）：
   ```bash
   python "D:\Hermes\skills\software-development\skill-library-maintenance\scripts\validate_skill.py" \
     --lens hermes "D:\Hermes\skills\<category>\<skill-name>\SKILL.md"
   ```
   有 ERROR 必须改掉再交付；WARN（如 description >60 字符）尽量清掉。
4. **回流**：更新 `D:\Hermes\xiaonan-memory\DASHBOARD.md` → git 提交 → 跑 `health_check.py`
5. **验证**：`skill_view` 能加载（主文件 + 至少一个 `[ref:]` 分章）+ `health_check.py` 无悬空引用

## 折叠更新（新素材并入已有技能）

凡哥给来新章节/续作/另一本书 → **不要新建技能**：
1. 读旧技能的 SKILL.md（章节索引/主题索引/核心方法论）+ `ls references/` 找最大章号
2. 新内容分两类：**修订已有章**（读旧章文件，合并重写）/ **新增章**（从最大章号往后编号）
3. 合并 glossary（字母序、已有词条追加新章号）、patterns、cheatsheet
4. 重写主 SKILL.md 的索引与核心层（仍 <4,000 tokens），更新日期与章节数
5. 跑体检 → 更新 DASHBOARD → 提交

---

## 坑（都踩过）

- **技能重名/重叠**：动手前 `search_files` 全库搜，别蒸出第二个打架的
- **一本厚书别想一遍读完再蒸**：分章读、分章蒸，中间产物落盘（`references/` 就是落盘处），防上下文被挤爆
- **别把"金句"当"方法"**：金句是佐证，方法是动作清单
- **docx 中文字体**：python-docx 默认字体中文会乱，需显式设东亚字体
- **description 一行定生死**：≤60 字符、中文触发放最前，否则以后不会被自动加载
- **样例先行**：厚书可先蒸 1 章给凡哥验风格再全蒸；但凡哥说"直接蒸"就直蒸
- **扫描版 PDF**：提取器读的是文本层，扫描件要 OCR 前置
- **PDF 双栏错位**：`pdftotext` 默认流式会把双栏串行，`--mode technical`（-layout）更还原

## 已验证案例
- 《人性的弱点》→ `carnegie-human-relations`（management 类）
- 《迷上我》28 章 → `mishangwo-attraction-system`（relationships 类），结构 = 分诊表 + 四流程 + 工具箱 + 边界

## 来源与致谢
v2 的机制层参考 `book-to-skill`（https://github.com/virgiliojr94/book-to-skill ，MIT）。提取脚本与规范体检工具为其思路的本地化重写，非直接移植。
