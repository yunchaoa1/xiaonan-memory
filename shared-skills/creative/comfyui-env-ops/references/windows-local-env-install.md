# 本机 Windows 装环境/下模型：原生工具路径与 uv venv（2026-09-14 实测）

凡哥本机 = Windows + Git-Bash（MSYS），ComfyUI 在 `D:\SDkecheng\ComfyUI`、其 `.venv` 由 **uv** 创建。
在云端（Linux）顺手的一套命令，搬到本机**会静默失败**。以下每条都是本次真金白银踩出来的。

## 1. 原生程序不认 `/d/...` 路径 —— 一律给 `D:/...`

MSYS 路径转换在这台机器上是关闭的。bash **内建**（`mkdir` / `ls` / `find` / `rm`）认 `/d/...`，但**原生 Windows 程序**（`curl` / `pip` / `uv` / `stat`）不认。

**症状（极易误判成"下载成功"）**：

```
curl: (23) client returned ERROR on write of 16384 bytes
```

`curl -o /d/SDkecheng/.../x.gguf` → curl 把路径当 `D:\d\SDkecheng\...`（目录不存在）→ **写 0 字节就退出**；脚本若只看 exit code 或 `ls` 目录，会当"下完了"。本次因此白下两轮（连后台 20GB 任务也一起空转）。

**规则**：

```bash
D="D:/SDkecheng/ComfyUI/models/LLM/Qwen"   # ✅ 原生程序用这个形式
mkdir -p "$D"                               # bash 内建，两种都行
curl -L -C - -x "$P" -o "$D/x.gguf" "$URL"  # -o 必须是 D:/ 形式
got=$(stat -c%s "$D/x.gguf")                # stat 也是原生程序 → D:/ 形式
```

**下载脚本模板（可直接复制）**——带断点续传 + 逐字节校验，适合 GB 级：

```bash
#!/bin/bash
P="http://127.0.0.1:7897"          # Clash Verge；curl 用 -x
get() { # $1=url $2=目标(D:/形式) $3=期望字节 $4=名称
  mkdir -p "$(dirname "$2")"
  echo "[$(date +%H:%M:%S)] 开始 $4"
  # ⚠️ 重试环：每轮断点续传，直到逐字节对上才 return。
  # 单发版（不带这个环）会在网络抖动时留下半截文件就跳去下一个 —— 2026-09-14 实测：
  # ① 12.5GB 下到 3.8GB(30%) 时连接断，脚本打了个 ⚠️ 就继续下 ②，① 从此被遗忘。
  for i in 1 2 3 4 5 6; do
    got=$(stat -c%s "$2" 2>/dev/null || echo 0)
    [ "$got" = "$3" ] && { echo "✅ $4 已完成 ($got)"; return 0; }
    echo "[$(date +%H:%M:%S)] 第 $i 次 下 $4（已有 $got / $3）"
    # --speed-time/--speed-limit：连接假活（有速率但几乎不动）时主动掐断，把控制权交回重试环，
    # 否则 curl 会抱着一条死连接一直挂着，后台任务看起来"在跑"其实永远下不完。
    curl -L -C - --retry 8 --retry-delay 5 --connect-timeout 30 --speed-time 60 --speed-limit 1024 \
         -x "$P" -s -o "$2" "$1"
  done
  echo "❌ $4 6 次都没完成，停在 $got / $3"
  return 1
}
```

**现成脚本**：`scripts/dl_model_resumable.sh <url> <目标D:/路径> <期望字节> "<名称>"`（本模板的可直接调用版，勿再手抄）。

**先取官方精确字节再下**（HF `?blobs=true` 的 `size` 字段），下完比字节而不是看 `du -h`（GB 级文件的进位会骗人）。

### 判「在跑还是死了」——凡哥会反复问这个，要给确定答案

两个互补信号，别只盯着文件大小：

```bash
# ① 增速：隔几秒 stat 两次（+0 字节 = 停了）
A="D:/.../x.safetensors"; s1=$(stat -c%s "$A"); sleep 8; s2=$(stat -c%s "$A")
echo "+$(( (s2-s1)/8/1048576 )) MB/s"
# ② 谁在飞：列 curl 进程的真实命令行（原生程序 → powershell 才看得到完整参数）
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='curl.exe'\" | ForEach-Object { \$_.ProcessId.ToString() + '  ' + (\$_.CommandLine -replace '.*-o ','' ) }"
```

② 能一眼看出「当前下的是哪个文件」——串行脚本里后一个文件出现 = 前一个已经结束（**结束 ≠ 成功**，必须再看字节数）。本次靠 ② 才发现 ① 早已停止而脚本已跑到 ②。

## 2. 长命令/heredoc 会被硬拦 —— 写文件再跑

超长 inline 命令（巨型一行、heredoc）会被 hardline 拦（"command parser limit or malformed executable payload"），并提示把脚本落到 `D:\Hermes\cache\blocked-scripts\`。
**做法：用 `write_file` 写 `.sh` / `.py` 再 `bash D:/path/x.sh`** —— 顺带避开 **heredoc 里反斜杠被吃掉**的坑（本次 `f.split('\\')` 进到文件里变成 `f.split('\')` → `SyntaxError: unterminated string literal`）。

## 3. uv 建的 `.venv` 没有 pip

```
D:\SDkecheng\ComfyUI\.venv\Scripts\python.exe: No module named pip
```

**装包一律用 `uv pip` + 显式指向 venv 解释器**：

```bash
VENV="D:/SDkecheng/ComfyUI/.venv/Scripts/python.exe"
uv pip install --python "$VENV" --no-deps "$W/x.whl"
uv pip install --python "$VENV" diskcache          # 缺的运行时依赖单独补
"$VENV" -c "import x; print('OK')"                 # 装完单测 import 再重启
```

- **`.venv` 的 Python 版本决定 wheel 的 `cp3XX`**：本机 **3.12.11 → `cp312`**（先 `"$VENV" -c "import sys;print(sys.version)"`，别猜）
- `--no-deps` 可避免 uv 去动 numpy / torch（本机 torch `2.13.0+cu130`、numpy 1.26.4 是 ComfyUI 的底盘，别让它升级），**代价是作者声明的运行时依赖要自己补**（本次漏了 `diskcache`）

## 4. uv 拒绝"改过名"的 wheel

```
error: The wheel filename "llama_cpp.whl" is invalid: Must have a version
```

用 `curl -o` 存成随意名字再 `uv pip install` 会失败。**存盘时就用原生 wheel 全名**（从 `browser_download_url` 抄，含 `+cu130`、`cp312`、`win_amd64`）：

```
llama_cpp_python-0.3.49+cu130-cp312-cp312-win_amd64.whl
```

## 5. llama_cpp（JamePeng fork）在本机的正确装法

`comfyUI-llama-TE` 的本地提示词链要它，且**必须是 JamePeng fork**（PyPI 的 abetlen 原版不支持 Qwen3.5+，会报"不支持 Qwen35ChatHandler"）。

- **Windows 有 cu130 wheel**（Linux 反而没有 cu130）→ 本机按 `cu130` × `cp312` × `win_amd64` 选，没有降级问题
- release 示例：`v0.3.49-cu130-win-20260831` → asset `llama_cpp_python-0.3.49+cu130-cp312-cp312-win_amd64.whl`（约 **297,796,276 字节**）
- tag / asset 名**一律用 GitHub API 抄**（`releases?per_page=N` 打印 `browser_download_url`），手打易错
- **装完必须验 handler 列表**（只看 pip 成功不算数）：

```python
import llama_cpp, llama_cpp.llama_chat_format as cf
print(llama_cpp.__version__)                       # 实测 0.3.49
print([h for h in dir(cf) if 'Qwen3' in h])        # 需要 Qwen35ChatHandler
# 实测本机输出：['Qwen35ChatHandler', 'Qwen3ASRChatHandler', 'Qwen3VLChatHandler'] ✅
```

首次 import 会打印 `loaded bundled OpenMP runtime` / `ggml-base.dll` / `llama.dll` 等行，**属正常**。

## 6. 代理分工（本机 7897）

| 工具 | 写法 |
|---|---|
| `curl` | `-x http://127.0.0.1:7897` |
| `git`（clone/fetch） | `git -c http.proxy=... -c https.proxy=... <cmd>` |
| `uv pip` / `pip` | `export HTTPS_PROXY=... HTTP_PROXY=...`（环境变量，不是 flag） |
| HF 专用 | 国内也可换 `hf-mirror.com`（把 `huggingface.co` 换掉即可，路径不变） |

## 7. `ComfyUI/models` 是 junction，真身在 `D:\SDkecheng\models`

`D:\SDkecheng\ComfyUI\models` 的真实路径 = **`D:\SDkecheng\models`**（一整座共享模型库：animatediff / BiRefNet / clip / controlnet / diffusers / LLM / loras / vae …）。

```python
import os
print(os.path.realpath(r'D:\SDkecheng\ComfyUI\models'))   # → D:\SDkecheng\models
print(os.path.islink(r'D:\SDkecheng\ComfyUI\models'))     # ⚠️ junction 可能返回 False
```

**判定用 `realpath` 对比，不要靠 `islink`**（本次 `islink` 返回 False 但 realpath 不同 → 它是 junction）。
**好处**：往 `ComfyUI/models/...` 放文件就等于放进共享库，换个 ComfyUI 安装也在；**注意**：`find` 只查 `ComfyUI/models` 不会漏，但不要以为两者是两份、白找一遍。

## 8. 「和云电脑部署不一样吗？」——本机为什么总比云端多干活

凡哥会问这句（2026-09-14 原话）。**部署方式其实一样**（同一份工作流、同一批插件、同样的模型名逐字照搬），差的是两台机器的底子 —— 汇报时要把这个结构原因讲清，否则他会以为你装法不对：

| | 云端（智算云扉） | 本机 |
|---|---|---|
| 系统 / 显卡 | Linux + RTX 5090 32GB | Windows + RTX 5080 16GB |
| **共享模型库** | **有公模库 `/datasets`** —— 一大批 H3 模型已躺在那儿，**软链即用、零下载** | **没有**（`D:\SDkecheng\models` 只是本地库） |
| 部分模型 | **机器自带**（例：放大模型 `minimax_h3_bf16_CONSERVATIVE_v5.safetensors` 是云端环境自带的，所以云端一跑就通） | 得自己下 |
| 插件 / 工作流 / 模型名 | 照云端 | **同样照云端**（差异只在上两行） |

**结论口径**：云端「软链即用」的东西，本机就是「必须真下」。所以本机多出几 GB 下载**不等于装法不同** —— 先讲这条再列下载清单，凡哥就不会追问「为什么云端不用下」。

## 9. 收尾检查清单

1. `ls -la` 目标目录 + **字节对比**（不是 `du -h`）
2. `"$VENV" -c "import ..."` 单测新装的包
3. 装插件后：重启实例 → `grep -iE "IMPORT FAILED"` → 复跑 `scripts/audit_workflow_missing_nodes.py` 到 **0 缺**
4. 需要软链/别名目录时，先 `rm -f` 半截文件（curl 中断的残留会占位造成假成功）
