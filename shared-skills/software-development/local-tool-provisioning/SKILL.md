---
name: local-tool-provisioning
description: 装工具/库/CLI/模型到本机、或评估别人发来的成品包能不能装时用。含换皮套壳验明正身+环境隔离决策树+实测验证。
version: 1.0.0
author: 小南
license: internal
metadata:
  hermes:
    tags: [环境, 安装, venv, WSL, 依赖隔离, 镜像]
    related_skills: [lightpanda-fastfetch, aria2-downloads, local-web-capabilities, skill-library-maintenance]
---

# 给本机装工具 / 库 / 模型（环境隔离 + 验证）

> 2026-10-11 定。那天连装 aria2、Lightpanda、trafilatura、markitdown、scenedetect、camoufox，
> 中间**把 Hermes 自己的依赖搞冲突了**（见铁律 1 的真实案例），所以把规则固化下来。

## When to Use（何时加载）
凡哥说「**装一下 / 装上 / 能不能装 / 用这个工具 / 把这个项目拿下**」，或我自己判断需要新工具时 —— **先加载本技能再动手**。

## 铁律 0 · 装之前先查本机有没有

```bash
command -v <cli>                                                    # 系统里有没有这个命令
python -c "import importlib.util as u; print(bool(u.find_spec('<pkg>')))"
```
**别重复装已有的东西**；也别凭印象说"本机没有"，查了再说。

## 铁律 0.5 · 别人发来的成品包，先验明正身再谈装

凡哥常从微信/群里拿到一个 zip 或安装包，丢过来问「**这是什么项目 / 我能不能直接用**」。
**别读宣传页、别照 README 的产品名下结论** —— 按这 5 处查，全程只读不改：

1. **包内自证文件**：`README.md`、`*版本.txt`、`【先看我】*.pdf`、**`开源许可/`** 目录。
   换皮包通常留着一张 `修改说明.md`，里面直说**上游项目名 + 许可证 + 改了哪几个文件**。
2. **引擎真身**：`pyproject.toml` / `package.json` 的 dependencies，
   再 `grep -n "npm install\|pip install\|git clone" setup.sh setup.ps1` —— 上游引擎必现形
   （实例：`npm install -g openclaw@latest`）。
3. **上 GitHub 核上游**：有仓库名就 `web_search "github <org>/<repo>"`，确认真的存在、许可证、
   star 量级。**没核到就不能说"这是开源的"**（凡哥尺子：禁推测）。
4. **判定商业模式**：换皮 + 中文一键装 + 傻瓜手册 + **机器码激活**（一机一码、离线验签、带到期日）
   = 卖「装好能用 + 出事有人管」，技术本体开源免费。这句要直说，别替卖家美化。
5. **授权闸在哪**：`grep -rn "license\|激活\|machine" <pkg>/`，看是不是 web 入口和 CLI 都卡。
   **卡住的这步 agent 过不去** —— 只能凡哥本人找发件人换码，我负责把机器码读出来给他。

### 「能不能直接用」照三段答，别只答能/不能

| 段 | 谁干 | 我怎么答 |
|---|---|---|
| 装环境 | **我** | 当场查前置 `command -v node npm ffmpeg` + `python -V`，报齐不齐、大概多久 |
| 大模型 Key / 账号 | **凡哥** | 给具体一家 + 充多少钱起，别让他自己研究 |
| 激活码 / 授权 | **凡哥**（找发件人） | 说清机器码怎么来、一机一码、到期要续 |

### 装机前三个附加动作

- **先把包从微信缓存目录复制到 D 盘再装**：`...\xwechat_files\<id>\msg\file\...` 是只读的，
  微信一清缓存就没了。
- **查本机有没有同名旧引擎**（`command -v openclaw` 等）：安装脚本多是「有就跳过」→
  版本漂移必报错，先升级再装。
- **确认它用自己的独立配置目录**（例 `~/.openclaw-<profile>/`），别让它的全局 npm 包装到
  Hermes 头上（见铁律 1）。

> 实战案例（CUPID superAI 3.0 = 浙大 Easel 换皮 + openclaw 引擎 + 机器码授权）：
> `references/rebranded-package-triage.md`

## 铁律 0.6 · GitHub 项目：先核真身，再判「三层能不能用」

凡哥丢一个 GitHub 链接 + 「**这个项目看看 / 我们能不能用 / 我不会安装**」时，这是**取证 + 判断**，不是"看完 README 就答"。
（2026-10-22~27 连着四次：OpenGCUA／Harness²／hongguoTV 等）

### 〇、连项目名都不知道 → 从画面里找（视频来源）

凡哥刷视频问「**这项目出自哪里**」时，**答案常常不在口播里**：

- **抽帧看**水印／角标／桌面图标／任务栏／窗口标题／地址栏 ——
  `ffmpeg -ss <秒> -i x.mp4 -frames:v 1 fr.png`（**单帧原尺寸最清楚**，别用缩太小的宫格读小字）
- 读不清就 `vision_analyze(..., region=[左,上,右,下])` **裁左上角那列放大，逐个念图标名**
- 实例：Vidu S 那条**全片没提项目名**（口播只是演示对话），项目名印在**画面水印「AI生成数字人 | Vidu S」**；
  同一招还从桌面图标读出 `OBS Studio／直播伴侣／数字人直播助手`，才判断出"博主在直播"
- 拿到名字/特征词再去 GitHub、官网核。⚠️ **视频的数字和话术都要核**：
  Harness² 说 16K star，实际 **17,462**（基本准）；OpenGCUA 说"小白一键上手"，官方要求 **macOS 14+ / Rust / Xcode**

### 一、核真身（三件事，缺一件不开口）

```bash
# ① 仓库存在吗、多少星、什么许可、还活着吗
curl -sL -H "User-Agent: Mozilla/5.0" "https://api.github.com/repos/<owner>/<repo>"
# ② 真实安装包在哪（★ 别只信 README 里的下载链接）
curl -sL -H "User-Agent: Mozilla/5.0" "https://api.github.com/repos/<owner>/<repo>/releases" | head -c 2000
# ③ README 全文（简介会漏关键限制）
curl -sL "https://ghfast.top/https://raw.githubusercontent.com/<owner>/<repo>/main/README.md"
```

**两个真实坑（2026-10-27）**：

- **README 给的下载地址可能是死的**：hongguoTV 的 README 指向 `hongguoTV-updates/releases/latest`，
  而该仓库**存在但没有 release** → API 返回 `404 Not Found`；真包在**主仓库** `releases` 里（`kotlin-v0.8.0`）。
  → **`releases` API 404 有两种含义**：仓库不存在 **或** 仓库存在但无 release。
  **别急着说"下载地址死了"**，同时查主仓库 releases 列表。
- **平台适配器是硬门槛**：README 只列 `macOS / Android / browser / Linux` 时，**Windows 就是装不了**。
  这不是"再研究一下"，是**直接判不能装**，别让凡哥白等。

### 二、下完必须校验（不许裸装）

release 一般带 `SHA256SUMS`：

```bash
curl -sL "<镜像>/<...>/SHA256SUMS" -o SHA256SUMS && cat SHA256SUMS
sha256sum <下到的文件>        # 两串必须一字不差
```

不一致 = 文件被改过或下坏了，**不许交给凡哥**。

### 三、「我们能不能用」按三层答，别只答能/不能

| 层 | 判什么 | 例子（OpenGCUA） |
|---|---|---|
| **软件** | 装得上吗？平台／依赖／成本？ | ❌ 无 Windows 适配器 → 装不了 |
| **数据** | 它的评测／基准对我们选型有用吗？ | ✅ 8 个模型同框架下的提升幅度，可当选型依据 |
| **思路** | 它的方法能不能直接改我们的做法？ | ✅ 「能写脚本就别点鼠标」—— 不用装任何东西就能用 |

**凡哥要的不是"能/不能"，是"哪种用法值得、代价多大"。** 答完**主动补反面**
（画质不够用／每任务 4 倍成本／官方自认不稳／与研究代码同跑要先隔离）。

### 四、交给他之前

- 装到本机的东西 → **给完整绝对路径** + 字节数／实分辨率
- 要装到**他的设备**上（电视 APK 这类）→ **先问设备型号/系统**再给步骤：
  安卓电视／华为鸿蒙／老电视（需外接盒子）装法完全不同，别直接甩一套 U 盘流程
- **没实测过的不许说"好用"**：分清「看材料得出的判断」和「我跑过」

> 七个项目的完整证据链（真身数据、水印/桌面图标的找法、star 核对、各自真实门槛与"不装"的理由）见
> `references/项目溯源与适配判断-2026-10.md`。**七次里六次结论是不装** —— 先判关系，再谈安装。

## 铁律 1 · 绝不往 Hermes 自己的 venv 装带复杂依赖树的包 ⚠️

**先确认你要用的 python 是谁**：
```bash
python -c "import sys; print(sys.executable)"
# D:\Hermes\hermes-agent\venv\Scripts\python.exe   ← 这是 Hermes 自己的环境，别乱塞
```

**真实案例（2026-10-11，我踩的）**：把 `crawl4ai` 装进 Hermes venv →
它要求 `snowballstemmer~=2.2`，而 Hermes 要求 `==3.1.1` →
**pip 直接把 Hermes 的依赖降级了**，有破坏 Hermes 功能的风险。

**修复动作**（照做即可）：
```bash
python -m pip uninstall -y crawl4ai
python -m pip install "snowballstemmer==3.1.1"
python -m pip check            # 必须回到 No broken requirements
```

**升级 Hermes 自带的包（不是新装）→ 一律加 `--no-deps`**（2026-10-27 实测）：
Hermes venv 里那些包（`edge-tts`、`aiohttp`、`tabulate`…）本身就是 Hermes 的运行依赖，
`pip install -U <pkg>` 会**顺带挪动它们的依赖**。只换这一个包时锁死依赖树：

```bash
D:/Hermes/hermes-agent/venv/Scripts/python.exe -m pip install --no-deps -U "edge-tts==7.3.1"
D:/Hermes/hermes-agent/venv/Scripts/python.exe -m pip check     # 升级后照样要复检
```

## 装哪里：决策树

| 东西的形态 | 装到哪 | 例子 |
|---|---|---|
| **纯 Python、无重依赖树** | Hermes venv 可以（**装完必须 `pip check`**） | trafilatura、markitdown、scenedetect |
| **框架型 / 带重依赖树（torch 系等）** | **独立 venv**：`D:\Hermes\venvs\<用途>` | crawl4ai、whisperX、VL 模型相关 |
| **只有 Linux 二进制** | **WSL**（`wsl.exe -d <发行版>`） | Lightpanda |
| **单文件 exe** | `D:\Hermes\bin\<名字>\` | aria2c |
| **GUI 应用** | **先问值不值** —— 多数只是壳，先看它的**引擎/CLI 能不能单装** | Motrix（壳）vs aria2（引擎） |

建独立 venv（**注意路径写法**）：
```bash
python -m venv "D:/Hermes/venvs/media"           # ✅ 原生 D:/ 形式
"D:/Hermes/venvs/media/Scripts/python.exe" -V
```
> ⚠️ `python -m venv /d/Hermes/...` **会失败** —— MSYS 的 `/d/...` 不转译给原生 Windows 程序。

## 装完必须过三道闸

1. **`pip check`** → 必须 `No broken requirements found`
2. **真跑一次**（不能只看"pip 安装成功"）
   - 拿**真实素材**跑，看输出对不对
   - 2026-10-11 实例：markitdown **装成功但转不了 docx**（可选依赖没装）→ 补 `markitdown[docx,pdf,pptx,xlsx]` 才行
   - 实测过的都要把**数字**留档（耗时 / 字数 / 检出数）
3. **回流 —— 这一步不是"可选的收尾"，它就是"吸收"这个动作本身**（凡哥 2026-10-11 强调，原话：
   > **"但凡我们决定要吸收一个技能或者项目时，就已经确认是我们需要的东西，一定要自动确保这项吸收到的内容能够使用起来。"**）

   **完整链条，缺一环 = 没吸收成功：**

   | # | 动作 | 检验标准 |
   |---|---|---|
   | 1 | **装** | 真跑通一次（不是看安装日志说"成功"） |
   | 2 | **验** | 拿**真实素材**跑，数字留档（耗时/字数/检出数） |
   | 3 | **写进技能** | 边界表 + 踩过的坑 + 实测数字，都在技能里 |
   | 4 | **挂 `skill-router` 路由** | **凡哥换个说法也能命中**（中文触发词写进路由表） |
   | 5 | **更新 `DASHBOARD.md`** | 技能索引加行 + 记录段 |
   | 6 | **提交同步** | `sync_skills.py push` + git commit/push |

   ⚠️ **三个真实翻车点（2026-10-11 全踩过）**：
   - **"写进技能" ≠ "接进路由"**：trafilatura/markitdown/scenedetect 只写进了技能正文、**没挂路由**，凡哥一句"**为什么大多数还没接进自动路由**"才发现；其中 `ocr-and-documents` **压根不在路由表里**（等于完全悬空）。
     → 前者是"**能读到**"，后者是"**会被想起来**"，**两步都要做**。
   - **顺序不能攒**：装一个→验一个→接一个。攒到最后的结果是：camoufox 一卡一小时，前面装好的全悬着。
   - **做了要说**：沉淀进技能/DASHBOARD 的动作要在对话里讲出来，别让凡哥觉得东西凭空冒出来。

## 国外源拉不动 → 镜像表（国内网络）

| 目标 | 办法 |
|---|---|
| GitHub release 资产（下载） | URL 前缀 `https://ghfast.top/`（2026-10-27 实测一次通，2.6MB）或 `https://ghproxy.net/` + 原 URL |
| HuggingFace 模型 | `HF_ENDPOINT=https://hf-mirror.com` |
| Playwright 浏览器 | `PLAYWRIGHT_DOWNLOAD_HOST=https://cdn.npmmirror.com/binaries/playwright` |
| pip 包 | `-i https://pypi.tuna.tsinghua.edu.cn/simple` |
| GitHub **信息**（API） | `api.github.com` **通常直连可用**，匿名限流 60 次/小时/IP |
| GitHub **文件**（releases 下载） | ⚠️ **和 API 是两回事**：走 `objects.githubusercontent.com`，**常被墙**（实测 `curl: (28) Failed to connect to github.com port 443`）。**查信息走 API、取文件走镜像** |

**GitHub API 限流实战（2026-10-11）**：三个并行子代理 + 我共用同一个 IP 的配额 → 全 403。
**绕开的正解 = 别去问 API，直接拼 release 资产 URL**：
1. 命名规则从**项目源码/配置文件**里拿 —— 例：camoufox 的 `repos.yml` 写着
   `pattern: "{name}-{version}-{build}-{os}.{arch}.zip"`
2. 拼出来**先用 HEAD 验证**（看 `HTTP 200` + `Content-Length`）：
   ```bash
   curl -sIL -m 25 "<拼出来的URL>" | grep -iE "^(HTTP/|content-length)"
   ```
3. 确认后再下载；**大文件用 `aria2c --continue=true`**（断了能续，见 `aria2-downloads`）
4. **下下来只是第一步 —— 还要手工装进它的缓存布局**：目录名规则、`version.json` / `config.json` 的
   字节、**以及"缺了就会被整个删光"的标志文件**（Camoufox 的 `.0.5_FLAG` —— 这个坑真吃过一次）。
   → **完整配方见 `references/manual-offline-install.md`**（1.31 GB 实战走通；
   收尾已实测：抖音 **920,392 字节**，同站 Lightpanda 是 0 字节）

## 坑（都踩过）

- **MSYS 路径不转译**：给原生 Windows 程序（python/node/git）必须 `D:/...`；写 `/d/...` 报 `No such file or directory`
- **`[extras]` 别省**：很多包"装成功 ≠ 能用"（markitdown 的 docx/pdf 支持在 extras 里）
- **体积别信二手描述**：下载前先 HEAD 拿 `Content-Length`。实测 camoufox 浏览器内核 **1.31 GB**，而调研报告写的是"300-400MB"（**错了 3 倍**）
- **跨 WSL 传参**：用 `wsl.exe -d <发行版> -- <绝对路径> <参数...>` **直接执行**；
  套一层 `bash -lc "..."` 时，URL/引号会被外层 shell 吃掉（实测踩过）
- **WSL 默认用户可能是 root** → 家目录是 `/root/`，不是 `/home/<user>/`
- **卸载后同样要复检**：`pip uninstall` 完再跑一次 `pip check`
- **升级 Hermes 自带包必须 `--no-deps`**：否则 pip 顺手挪动 `aiohttp`/`tabulate` 等，把 Hermes 依赖搞乱（见铁律 1）
- **装 / 升级完必须「真重启」Hermes 桌面 App**：`venv/Lib/site-packages/**` 的改动对已运行的
  `hermes_cli.main serve` **不生效**（模块早在 `sys.modules` 里了）。**在 `terminal` 里另起进程测通 ≠ App 内生效**
  —— 这是最容易误判成"已经装好了"的地方。
  桌面板有 **Tray + 单实例锁**，点窗口 X 只收托盘、再点图标是把老实例唤回来 →
  **判据只看进程 `CreationDate` 是否晚于改动文件 mtime**。一键真重启：
  `hermes-network-proxy` 的 `scripts/restart_hermes_app.ps1`（带延时、取消标记、日志）

## 与"取机制不取框架"尺子联动

装之前先过三问（凡哥 2026-10-11 授权放开的同一套尺子）：
1. **是不是真有的痛** —— 有实测数字支撑吗？
2. **会不会跟现有体系打架** —— 功能重叠？触发词抢位？
3. **要不要额外背重依赖** —— 能不能只取其中一块？

→ 三条通不过就别装，或者只取零件（例：只装 **aria2c 引擎**不装 Motrix GUI；
用 **Lightpanda + trafilatura** 自组替代 crawl4ai 框架）。
