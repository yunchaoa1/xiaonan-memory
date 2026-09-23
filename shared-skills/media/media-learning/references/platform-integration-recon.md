# 外部 AI 平台 / 工具的可接入性侦察（JS bundle 挖法）

**场景**：凡哥发来一个"看起来很厉害"的外部工具或平台链接，问「能不能加入进来给我们赋能」。
**目标**：在一分钱不花、一个软件不装的前提下，回答三件事——
① 它是什么形态？② 它跟我们现有体系能不能对接（数据标准是否同构）？③ 接入路径是什么、需要凡哥做什么？

**核心手法**：**现代 Web 应用的前端 JS bundle 就是它的说明书。** API 端点、数据结构、字段名、
甚至它支持的第三方集成清单，全都打包在那一个 `.js` 文件里。抓下来 `grep` 一遍，比看官网宣传页准得多。

---

## 步骤 0 —— 先拿到真域名（很多站是 301 跳转）

`web_extract` 对未索引的新站常报 `CRAWL_LIVECRAWL_TIMEOUT`（不是站挂了，是抓取后端没缓存）。
不要就此罢手 —— **`curl -I` 跟随重定向，看 `Location` 头**：

```bash
curl -sI -m 25 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36" <链接> | grep -iE "^HTTP|location"
```

实测：`luzi.ai` → `301` → `https://www.luzi.top/`（真域名 + 真站点全在 `.top` 上）。

**同时打开预览面板给凡哥看**（`open_preview` + `read_preview`）：既拿到正文文本，
又让他直接看到你在查什么。SPA 的正文靠 `read_preview` 不一定全，但 `curl -sL` 另存 HTML 后正则洗文本很稳。

## 步骤 1 —— 抓前端 bundle

```bash
# 从 HTML 里揪出 bundle 路径
curl -sL -m 40 -A "Mozilla/5.0 ..." https://<站点>/ -o site.html
grep -oE '/[A-Za-z0-9_/.-]*\.js' site.html | sort -u | head
```
```python
# 下载（3~4MB 的 minified bundle 很常见）
urllib.request.urlopen(urllib.request.Request(JS_URL, headers={"User-Agent": UA, "Referer": SITE}))
```
实测：`app.luzi.top/app-assets/index-BYVH18LJ.js` = **3,574,200 字符**。

## 步骤 2 —— 三刀切开

### ① 域名列表 → 看它官方支持哪些第三方（最有价值的一刀）
```python
re.findall(r'https?://([A-Za-z0-9.-]+\.[A-Za-z]{2,})', js)
```
**实测命中（炉子）**：`hermes-agent.nousresearch.com`、`hermes-assets.nousresearch.com`、
`code.claude.com`、`chatgpt.com`、`cursor.com`、`antigravity.google`、`opencode.ai`、`docs.openclaw.ai`、
`www.trae.cn`、`www.codebuddy.cn`、`www.workbuddy.cn`、`www.kimi.com`、`www.doubao.com`、
`agent.minimaxi.com`、`www.dumate.cn`、`www.feishu.cn` …
→ **一句 `grep` 就确认了"Hermes 是它的官方一等支持"，不用猜、不用等官方文档。**

### ② API 端点 → 判能不能程序化对接
```python
sorted(set(re.findall(r'["\'`](/api/v[0-9][A-Za-z0-9_/${}.-]*)["\'`]', js)))
```
实测：`/api/v1`；具体调用形态散在 minified 代码里，配合 `post("/assets/"`、`put(\`/assets/${id}\`` 这类找得到全貌。

### ③ 关键词计数 → 一眼判数据标准是否同构
```python
for kw in ["SKILL.md","frontmatter","skills/",".claude","AGENTS.md","mcp","SKILL","zip","agent-skill"]:
    print(kw, js.count(kw))
```
实测：`SKILL.md ×78`、`SKILL ×91`、`agents.md ×23`、`mcp ×66`、`agent-skill ×2`、`frontmatter ×1`
→ **结论：它的"能力包"就是 Agent Skills 标准（zip + `SKILL.md` 入口）**，跟 Hermes 的 `skills/` 同构。

## 步骤 3 —— 挖"集成定义"这种结构化配置

比关键词更有力的是**配置数组**。用关键词开窗读上下文（minified 代码里配置都是字面量）：

```python
def ctx(kw, before=180, after=320, maxn=6):
    out = []
    for m in re.finditer(re.escape(kw), js):
        out.append(js[max(0, m.start()-before): m.start()+after])
        if len(out) >= maxn: break
    return out
```

炉子里挖到 `deployment_targets` / `roots` / `skill_entries` / `supported_capabilities` / `bundles` ——
**这是它的"支持哪些 Agent、每个 Agent 怎么部署"的完整定义表**，等于提前拿到了接入说明书。

## 炉子（LUZI, luzi.top）实测结论表

| 项目 | 结论 |
|---|---|
| 形态 | **桌面端 AI 能力网络**（秋芝2046 团队）。Web 版 `app.luzi.top` + 桌面端（Windows/macOS），**内测需邀请码** |
| 它自己跑不跑 AI | **不跑**。官网原话「运行：交给熟悉的 AI 读取能力包」→ 它是能力包分发器 |
| 能力包格式 | **zip + 入口文件 `SKILL.md`**（资产分 `skill` / `prompt` / `reference` 三类） |
| API | base `/api/v1`（`POST /assets/`、`PUT /assets/{id}`、`PATCH /assets/{id}/prompt-use`、`GET /assets?type=&status=active&asset_id=`） |
| 上传结构 | `{asset:{summary,tag_ids,title,title_zh,type:"skill"}, skill_content:{cover_file_object_id, entry_file:"SKILL.md", package_file_object_id}}` |
| 官方支持 Agent | Claude Code / Codex / Cursor / Antigravity / OpenCode / **Hermes** / OpenClaw / Trae / CodeBuddy / WorkBuddy / Kimi / 豆包 / MiniMax Agent |
| **Hermes 接入定义** | `primary_entry: "SOUL.md"`；`roots: ~/.hermes`；`skill_entries: ~/.hermes/skills`；能力：识别 / 复制部署 / 内容预览 / Agent 迁移；记忆按原生格式读写 `MEMORY.md` / `USER.md` |
| Hermes 部署目标 | `deployment_targets: [{id:"user-skills", display_name:"Hermes 用户级 Skill", mode:"copy_directory", relative_path:"skills", root_id:"config", scope:"user_agent", supported_deployment_modes:["copy","link"]}]` ← **copy 与 link 都支持** |
| 官方套餐 | 小白包 `[doubao-work, codex, hermes]` / 高手全套 `[claude-code, codex, opencode, hermes, openclaw]` |
| 内置能力 | `luzi-companion`（炉子伴侣）/ `web-access` / `daily-brief` / `lark-cli`（飞书好）/ `doc-export` / `code-review` / `browser-mcp` |

### ⚠️ 落地卡点与解法
它默认找 **`~/.hermes/skills`**，而凡哥的 `HERMES_HOME=D:\Hermes`、技能库在 **`D:\Hermes\skills`**
（`C:\Users\bobby\.hermes` 存在但没有 `skills` 子目录）→ 一键部署会装到错的地方。
**解法：做目录联接力（junction），把 `~/.hermes/skills` 指到 `D:\Hermes\skills`**——它读写的就是真库，双向都通，零风险可回滚。

### 边界（交付给凡哥时必须写清的）
| 可以流通 | 绝不外发 |
|---|---|
| 方法论类：提示词框架、镜头语言、ComfyUI 运维、Seedance/LTX 技巧、OPC 流程 | 南溟岛 IP（世界观/角色/剧本）、齐白兰·顾蓝汐项目、客户项目、团队考核数据 |
建议节奏：**先只做导入方向**（拉别人的能力进我们库），发布方向等凡哥划完边界再说。

---

## 坑与备选路径

- **`browser_exec` 起不来时**（daemon 报 `DevToolsActivePort not found`）：不要卡在这里 ——
  改用 `curl` 抓 HTML/JS + `open_preview`/`read_preview` 走应用内浏览器。**这两条路足够完成上面全部侦察。**
- **`web_extract` 超时 ≠ 站点不可达**：先 `curl -I` 看状态码与 `Location`，多数是后端没索引、或域名 301 了。
- **别猜，读代码**：官网宣传页只会讲愿景；`grep` bundle 才拿得到"它支持谁、怎么装、API 长什么样"。
- **评估阶段不装软件**：安装包可以下载后做静态检查（大小/后缀/内部字符串），但**安装、登录、申请邀请码一律留给凡哥本人**。
