# 换皮/套壳成品包 · 拆包实录（判据与命令）

> 配套 `local-tool-provisioning` 铁律 0.5。凡哥问「这是什么项目 / 我能不能直接用」时，照这页走。

## 案例：CUPID superAI「超级新媒体人 3.0」（2026-10-19）

**来路**：微信收到的 zip（15 MB），解压得 `CUPID-superAI/`，手册落款「CUPID MEDIA · 2026.10」，
宣传语「一句话让 AI 找热点、写脚本、做图文，一稿改 7 个平台」「114 个新媒体技能」。

### 拆出来的真相

| 层 | 是什么 | 证据 |
|---|---|---|
| 上游本体 | **浙大 ZJU-REAL 团队的 Easel**（Apache-2.0，社媒运营 Agent 工作台，112 个 skill，六平台发布） | `开源许可/修改说明.md` 自述；GitHub `ZJU-REAL/Easel` 实核存在 |
| 引擎 | **openclaw**（npm 全局包，开源 agent 引擎） | `setup.sh`：`npm install -g openclaw@latest`；`cupid/engine_cmd.py` 直跑 `openclaw.mjs` |
| 卖方加的东西 | 品牌皮肤、中文一键装（Mac/Win 各一套双击脚本）、6 家国产模型对接（走 Anthropic 兼容接口）、傻瓜手册、**机器码激活** | `cupid/cupid_license.py`：Ed25519 离线验签、机器码=MachineGuid 哈希、含客户名与到期时间 |
| 卖点实质 | 卖「装好能用 + 中文手册 + 出事有人管」，技术本体开源免费 | — |

合规性：LICENSE 与修改说明都随包保留、写清改了哪些文件 —— **属于合规的换皮二次分发**，不是盗版。

### 拆包命令（可复用）

```bash
P="<包目录>"
# 1 自证文件
ls "$P"; cat "$P"/*版本.txt; ls "$P/开源许可"; head -40 "$P/开源许可/修改说明.md"
# 2 引擎与依赖
cat "$P/pyproject.toml"; grep -n "npm install\|pip install\|git clone" "$P"/setup.sh "$P"/setup.ps1 | head -30
# 3 授权闸
head -60 "$P/cupid/cupid_license.py"; grep -rn "激活\|license" "$P/cupid/cli.py" | head
# 4 技能体量（判断是壳还是真家伙）
find "$P/skills" -name SKILL.md | wc -l
# 5 手册读真话（PDF 直接 read_file 会抽文本）
#   重点看：前置要求、模型表、每日流程、FAQ 里的「平台风控」提示
```

### 这台机器上的前置盘点（2026-10-19 实测）

- `python 3.11.15` ✓（要求 ≥3.10）、`node v24.18.0` / `npm 12.0.2` ✓、`ffmpeg` ✓
- **已存在旧引擎**：`C:\Users\bobby\AppData\Local\OpenClaw\deps\portable-node\openclaw`
  → `openclaw --version` = **OpenClaw 2026.6.10**（6 月留下的）
  → 安装脚本「有就跳过」，会带着旧版本跑 → **先升级再装**
- `~/.openclaw-cupid`、`~/.cupid-superai` 均不存在 → 从未装过 / 从未激活

### 结论口径（对凡哥怎么说）

1. 这是**别人打包卖的 AI 新媒体运营工作台**，底子是浙大开源项目换皮 + openclaw 引擎 + 机器码授权。
2. 三道门：**装环境（我干）/ 大模型 Key（他充 20 元起，MiniMax 最稳）/ 激活码（他找发件人，一机一码，我读机器码给他）**。
3. 三个坑要说：发布类有平台限流风险（手册自己都劝小红书手动发）；换电脑要重新要码、到期要续；
   生图/生视频/配音要另开 Key 按次付费。
4. 对咱们自己的价值：它的 **114 技能目录 + 发现/策划/创作/发布/归因五层拆法**，可直接当影剧工坊、
   浪浪椰「内容发布层」的产品参考 —— 比从零想省事。

## 通用判据速查

- README 里出现「交付/激活/对接人/购买者」字样 → 商业封装。
- 有 `修改说明.md` 或 `第三方组件致谢.md` → 换皮包，上游名字就在里面。
- 装个包要先「把机器码发给对接人」→ **这不是开源分发，agent 无法替用户跨过这道闸**。
- 附带 PDF 手册里一定有「出问题找对接人」→ 说明支持靠人，不是靠文档。
