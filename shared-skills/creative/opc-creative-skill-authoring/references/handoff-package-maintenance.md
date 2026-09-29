# OPC 节点 Skill 交接包维护（交付给平台团队/小何的封装流程）

**包位置**：`D:\Hermes\xiaonan-memory\opc-sim\交接包_OPC平台\`
**结构（2026-09-24 起）**：`00_先读这个_使用说明.md` + `01_节点Skill/`（**只含 7 个节点 skill**）。凡哥 2026-09-24 明确："我们的 skill 只需要 7 个节点的 skill 其他的都不要，能保证这 7 个 skill 可以跑通就好。"——02_方法论Skill / 03_产品设计参考已按此移除（留本地自用，不进交接包）。

**7 个节点**：writing-opc-entry-test ／ novel-to-screenplay-opc-test ／ screenplay-asset-extraction-opc-test ／ qwen-image-subject-assets-opc-test ／ screenplay-to-15s-storyboard-opc-test ／ qwen-image-storyboard-keyframe-opc-test ／ minimax-h3-shot-prompt

## 更新流程（2026-09-24 实测跑通）

1. **对比差异**：交接包内每个 `<name>/SKILL.md` 对 `D:\Hermes\skills\creative\<name>\SKILL.md`（fallback `D:\Hermes\skills\<name>\SKILL.md`）做 diff，列出有差异的。
2. **同步最新**：以本地为准 cp 覆盖交接包（交接包=交付快照，本地=活文件）。
3. **补 references（关键步骤·防断链）**：读每个 SKILL.md 里所有 `references/...` 引用，确认文件在 **skill 自己的 references/ 目录**内——共享参考文件（如 `xiaonan-memory/references/opc-*.md`）要 copy 进 skill 目录，相对路径才能解析。
4. **修跨包引用**：正文指向包外 skill 的路径（如 `prompt-master-pipeline/references/xxx.txt`）改成包内 `references/xxx.txt` 并把文件拷进来——交接包必须**零外部依赖**（"能跑通"的硬标准）。
5. **完整性验证**（每轮必跑）：
   ```bash
   cd "01_节点Skill" && for d in */; do n=${d%/}; echo "【$n】"; \
     grep -h -o "references/[A-Za-z0-9_.\-]*" "$n/SKILL.md" | sort -u | \
     while read ref; do [ -f "$n/$ref" ] && echo "  ✓ $ref" || echo "  ✗ 缺: $ref"; done; done
   ```
   - frontmatter 检查：每个 SKILL.md 必须有 `name:` 和 `description:`。
   - **误报边界**："来源：…references/ref-en.txt" 这类**出处标注**也会被 grep 命中——判上下文再决定补不补；能找到的官方原文文件顺手补进包内（更完整，如 H3 官方 `ref-en.txt`）。
6. **说明书同步**：只列 7 个 skill；旧的 02/03 提及删净；涉删除 skill 的指引改写（如"用 opc-output-inspection 检查"→"用证据链方法检查"）；底部"打包时间"更新为当天。
7. **打包**（git-bash 无 zip 命令，用 python）：
   ```python
   python -c "
   import zipfile, pathlib
   src = pathlib.Path(r'D:\Hermes\xiaonan-memory\opc-sim\交接包_OPC平台')
   dst = r'D:\数字资产\OPC节点Skill交接包-YYYY-MM-DD.zip'
   with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
       for f in sorted(src.rglob('*')):
           if f.is_file(): z.write(f, f.relative_to(src.parent))
   "
   ```
   输出到 `D:\数字资产\`，zip 路径**交凡哥本人转发**给小何（我们不直接发）。
8. **收尾**：git 提交 xiaonan-memory ＋ `sync_skills.py push`（本地 skill 侧的改动）。

## 工具换代换轨（2026-09-24b：GPT Image → Qwen-Image 2.1）

出图工具换代时交接包要整体换轨——**目录改名 + 内容换轨 + 全库引用同步 + 重打包**，四件一起做完才叫"能跑通"。

1. **skill 改名**：`gpt-image-subject-assets-opc-test` → `qwen-image-subject-assets-opc-test`、`gpt-image-storyboard-keyframe-opc-test` → `qwen-image-storyboard-keyframe-opc-test`（目录名 + frontmatter `name:` + `tags` 一起改）。改名技术细节见 `skill-library-maintenance` §4.5（目录 busy 用 `cp -r` + `sleep` + `rm -rf`）。
2. **内容换轨四个必改点**：
   - **工具口径**：所有 "GPT Image 2 / Nano Banana" → "Qwen-Image 2.1 工作流（云电脑 ComfyUI）"。**工作流文件不随包**（凡哥定："他可以看到云电脑"）。
   - **提示词策略反转**：旧的"少写提示词（模型有推理层）" → **Qwen 详细自然语言描述（官方 PE 标准约 400-500 词）+ 肯定式为主**。这条最容易漏——旧 skill 里 "minimal prompting" 的说法与新规范直接冲突。
   - **分辨率**：旧的"16:9 原生 4K（3840×2160）" → **Qwen 原生最大：横屏 2752×1536 / 竖屏 1536×2752**（凡哥："按照原生最大的来，横屏竖屏两个版本"）。**不虚标 4K**。
   - **去门禁形态**：扫掉 skill 里残留的"自检/核对/重写/不生成"段落，改成**生成规则形态**。本次实例：故事板 skill《剧情核对铁律》第 2 条"prompt 写完，调生图**之前**，对照卡**自检**一遍…缺一个=违规，**重写** prompt，**不生成**" → 改为《剧情动作抄写规则》"写 prompt **时**把剧情动作逐字写进去"。依据：凡哥 2026-09-24 重申"**我们的 skill 没有自检的作用，不要给它增加检查错误的任务**"。
3. **references 全量重拷**：改名后共享参考文件要重新拷进新目录——本次补了 4 个（tiering／attractiveness／templates／**vocabulary**，其中 vocabulary 此前一直悬空）。
4. **两层引用检查（本次新增）**：除 SKILL.md → references 外，还要查 **references 之间相互引用**：
   ```bash
   grep -rh -o "references/[A-Za-z0-9_.\-]*\.md" <skill>/references/*.md | sort -u
   ```
   逐个 `find` 校验——本次正是这层查出 `opc-style-prompt-vocabulary-v0.1.md` 悬空（它只在仓库共享 `references/` 下、没进 skill 目录）。
5. **全库引用同步**：在 `/d/Hermes/skills` + `/d/Hermes/xiaonan-memory` 全库 grep 旧名，**活文档批量精确替换**（本次 14 处：4 个 skill 的 SKILL.md/references、DASHBOARD 6 处、说明书 2 处）；**历史快照不动**（`opc-lean-plan/`、`opc-sim/v2/` 运行数据、旧 zip）。
6. **重打包**：`OPC节点Skill交接包-YYYY-MM-DD<b>.zip`（同日出多版加 b），旧 zip 删除。

## 共享 references 多副本清扫（2026-09-24 两处漏网教训）

**同一份共享参考文件在多个节点下各有一份副本**（实测：`opc-high-attractiveness-character-rules-v0.1.md` 在生图节点＋写作节点各一份；`opc-style-prompt-vocabulary-v0.1.md` 在仓库共享 `references/` ＋ skill 目录各一份）。

**两处漏网（凡哥追问"是否只是更新的生图节点的 skill？"时才查出）**：
1. 只改了"主副本" → 另一节点的副本仍是旧口径，**包内自相矛盾**（写作节点那份还写着"OpenAI GPT Image 提示指南"）。
2. **cp 早于 patch**：先把共享文件拷进 skill 目录、又在源文件上继续改 → **拷进去的是半改版本**（vocabulary 标题改了、正文没改，直到复验才现形）。

**规则**：
- **顺序**：**先在源文件上改完 → 再 cp**；每次 cp 后立刻复验被拷文件的关键行（别在中间态停下）。
- **收包前跑内容扫描**，不是只查文件是否存在：
  ```bash
  cd 交接包 && grep -rn "旧口径关键词" . | head -20     # 期望只剩"已退役/换轨说明"这类必须保留的行
  grep -rln "<共享文件名>" .                              # 先找全部副本，再逐个对齐
  ```
- 扫描覆盖：所有 `<skill>/references/*.md`、说明书、**以及同一文件的其他副本**。

## 出图工具换代补充（2026-09-24c：双工作流写进交付文档）

Qwen-Image 2.1 有**两个工作流**（凡哥："两个功能切换需要更改工作流节点，太麻烦，所以做成两个流…一起写进说明里"）：

| 流 | 工作流文件 | 用途 |
|---|---|---|
| 图生图/编辑流（12 节点，有参考图）| `qwen image2.1图片编辑工作流-2.json` | 定妆 / 换装 / 改年龄 / 故事板关键帧 |
| 文生图流（8 节点，空 latent 起步）| `qwen image2.1文生图工作流.json` | 首次出图 / 纯文字场景 / 概念图 |

- 两流**同模型三件套**（UNET `qwen_image_2.1_int8_convrot` + CLIP `qwen3vl_8b_bf16` + VAE `qwen_image_2.1_vae_bf16`）；工作流文件**不随包**（凡哥定："他可以看到云电脑"）。
- **判断规则写进交付文档**：有参考图 → 编辑流；纯文字 → 文生图流。
- **必须写明尺寸陷阱**：文生图流 `EmptyLatentImage` 默认 **1024×1024**，出图前手动改**原生最大**（横 2752×1536 / 竖 1536×2752）。
- **同步点四处一次改完**：说明书 + 两个生图节点 skill + `image-prompt` skill + DASHBOARD（只改说明书＝漏）。

## 遗留：门禁形态清点（待凡哥拍板，勿擅自改）

已清两处：《剧情核对铁律》→《剧情动作抄写规则》；《缺失任一出场人物的参考图 → 阻断，不生成》→ 规则说法。
**尚未处理**：`minimax-h3-shot-prompt` 的 `Pre-Output Hard Checklist` / `Hard Gates` / `Verification Checklist` / `Shot Count Stability Default` 下的 `Self-check` —— 同属检查形态，已向凡哥报告并等他决定。**未获明确指示前不要擅自删改**（该 skill 已交付过，改动会让平台侧困惑）。

## 纪律

- **交付路径（2026-09-24 凡哥明确要求）**：zip 交凡哥时回话里**必须写完整绝对路径**（`D:\数字资产\...zip`）——原话"要直接给我文件路径，不要只给我文件名称"；用 `MEDIA:` 时路径文本再写一遍。
- **交付物不加料**：凡哥"不用添加其他的东西"——只封装规定内容，不塞额外文件/说明/版本注记。
- **触发时机**：① 凡哥明确说"给小何/交接包"；② 节点 skill 更新后（主动提醒凡哥"交接包落后了"，由他决定何时出包）。
- **2026-09-24 版更新记录**（对照旧版）：分镜节点（+开场镜/对话戏焦点策略/生活化动作/空间拓扑账本/主体占框）、写作节点（+开场设计五公式）、H3 提示词（六段规则最新＋官方原文参考随包）；references 补齐 4 处（此前 3 文件缺失+1 处路径悬空）。
