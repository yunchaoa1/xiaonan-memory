---
name: local-tool-provisioning
description: 装工具/库/CLI/模型到本机时用。环境隔离决策树+实测验证。
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
| GitHub release 资产（下载） | URL 前缀 `https://ghproxy.net/` + 原 URL |
| HuggingFace 模型 | `HF_ENDPOINT=https://hf-mirror.com` |
| Playwright 浏览器 | `PLAYWRIGHT_DOWNLOAD_HOST=https://cdn.npmmirror.com/binaries/playwright` |
| pip 包 | `-i https://pypi.tuna.tsinghua.edu.cn/simple` |
| GitHub 网页 / API | 直连不通；**API 匿名限流 60 次/小时/IP** |

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

## 与"取机制不取框架"尺子联动

装之前先过三问（凡哥 2026-10-11 授权放开的同一套尺子）：
1. **是不是真有的痛** —— 有实测数字支撑吗？
2. **会不会跟现有体系打架** —— 功能重叠？触发词抢位？
3. **要不要额外背重依赖** —— 能不能只取其中一块？

→ 三条通不过就别装，或者只取零件（例：只装 **aria2c 引擎**不装 Motrix GUI；
用 **Lightpanda + trafilatura** 自组替代 crawl4ai 框架）。
