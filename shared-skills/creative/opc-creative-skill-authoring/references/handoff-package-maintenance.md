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

## 纪律

- **交付物不加料**：凡哥"不用添加其他的东西"——只封装规定内容，不塞额外文件/说明/版本注记。
- **触发时机**：① 凡哥明确说"给小何/交接包"；② 节点 skill 更新后（主动提醒凡哥"交接包落后了"，由他决定何时出包）。
- **2026-09-24 版更新记录**（对照旧版）：分镜节点（+开场镜/对话戏焦点策略/生活化动作/空间拓扑账本/主体占框）、写作节点（+开场设计五公式）、H3 提示词（六段规则最新＋官方原文参考随包）；references 补齐 4 处（此前 3 文件缺失+1 处路径悬空）。
