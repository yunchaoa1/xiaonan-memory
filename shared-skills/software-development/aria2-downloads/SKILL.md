---
name: aria2-downloads
description: 下载大文件/BT/磁力/批量时用。aria2多线程断点续传+RPC接口。
version: 1.0.0
author: 小南
license: internal
metadata:
  hermes:
    tags: [下载, aria2, Motrix, BT, 磁力, 断点续传, RPC]
    related_skills: [comfyui-env-ops, video-learning, local-web-capabilities]
---

# aria2 下载引擎（Motrix 的底层引擎）

> **2026-10-11 吸收自抖音「Motrix」视频**（开源项目 `agalwood/Motrix`，官网 56,319★）。
> 它的架构是 `React UI → app core → engine adapter → **aria2**` —— 也就是说 **Motrix 的灵魂就是 aria2**。
> **取机制不取框架**：只装了 **2.36MB 的 aria2c 引擎**，没装 ~100MB 的 Electron GUI。因为"能接入你的智能体"的本质 = aria2 的 **CLI + JSON-RPC**，GUI 只是壳。
> 实测装成 2026-10-11（v1.37.0，Windows x64）。

## When to Use（何时加载）
凡哥说：**下载 / 下载太慢 / 断点续传 / 批量下载 / BT / 磁力 / 种子 / torrent / 这个链接下不来 / 帮我下这个模型**。

## 装在哪（本机已验证）
```
D:\Hermes\bin\aria2\aria2c.exe        # v1.37.0，aria2 version 1.37.0 已验证
```

## ⚠️ 第一步：先看边界表，别用错工具

| 你要干的事 | 该用谁 | 为什么不是 aria2 |
|---|---|---|
| 抓网页正文 / 搜索 | `wigolo` / `scrapling`（local-web-capabilities） | 那不是"下载文件" |
| 下 B站/YouTube/抖音 视频 | **yt-dlp** | 专站解析，aria2 不懂视频站接口 |
| 下 HF 模型（要逐字节校验 + 自动重试环） | `comfyui-env-ops\scripts\dl_model_resumable.sh` | 那个脚本带 expect 字节校验，专门防"半截文件被静默跳过" |
| **大文件 / 多线程 / 断点续传 / 批量列表 / BT / 磁力** | **aria2c**（本技能） | ← 这里 |
| 顺手抓个小文件 | `curl` | 够用，不必上 aria2 |

> 一句话：**aria2 补的是"批量 + 多线程 + P2P + 可远程调度"这块空白**，替换不了 yt-dlp 和模型校验脚本。

## 用法 1 · 命令行（最常用）

```bash
A2="/d/Hermes/bin/aria2/aria2c.exe"
"$A2" -x16 -s16 -k1M --continue=true --file-allocation=none \
      -d "D:/目标目录" -o "目标文件名" "URL"
```
- `-x16` 每服务器最大连接数 ｜ `-s16` 分片数 ｜ `-k1M` 分片大小
- `--continue=true` 断点续传（中断后再跑同一条命令即续传）
- `--file-allocation=none` NTFS 上更快（预分配会卡住不动）
- 批量：把 URL 写成一行一个的文件，`-i urls.txt -j5`（5 个并发）

## 用法 2 · RPC（"接入智能体"的正解，已实测）

**启动常驻服务**（Windows 下 `--daemon=true` 不生效，必须用后台进程跑）：
```bash
/d/Hermes/bin/aria2/aria2c.exe --enable-rpc --rpc-listen-port=16800 \
  --rpc-secret=<自己定的口令> --continue=true --max-concurrent-downloads=5 \
  --dir="D:/下载目录"
```
**调用**（JSON-RPC 2.0，`params` 第一项是 `token:<口令>`）：
```python
import json, urllib.request
def rpc(method, params):
    req = urllib.request.Request('http://127.0.0.1:16800/jsonrpc',
        data=json.dumps({"jsonrpc":"2.0","id":"t","method":method,"params":params}).encode(),
        headers={"Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))

rpc('aria2.addUri', ['token:口令', ['URL'], {'out':'文件名'}])   # 加任务，返回 gid
rpc('aria2.tellStatus', ['token:口令', gid, ['status','completedLength','totalLength']])
rpc('aria2.tellActive', ['token:口令'])                          # 进行中
rpc('aria2.pause', ['token:口令', gid])                          # 暂停 = 断点续传的锚
```
安全：默认只监听 `127.0.0.1`，**不要**开 `--rpc-listen-all`（等于把下载器暴露到局域网）。

**配套脚本（实测可用，省去手搓 JSON）**：
```bash
export ARIA2_SECRET=<你的口令>
RPC="D:/Hermes/skills/software-development/aria2-downloads/scripts/a2rpc.py"
python "$RPC" version                       # 连通性 + 版本
python "$RPC" add "<URL>" --out 文件名 --dir D:/目标目录
python "$RPC" list                          # 进行中（含进度/速度）
python "$RPC" all                           # 全部（等待+进行+完成）
python "$RPC" status <gid>
python "$RPC" pause <gid> | unpause <gid> | remove <gid>
```
> 2026-10-11 实测：`version` / `add`（返回 gid）/ `list`（active 61% 204KiB/s）/ `all` 全通过，文件真实落盘。

## 用法 3 · BT / 磁力

```bash
"$A2" --seed-time=0 -d "D:/目标目录" "magnet:?xt=urn:btih:...."
"$A2" --seed-time=0 "D:/xx.torrent"
```
`--seed-time=0` = 下完不做种（否则会一直挂着上传）。**只下合法内容**，不碰侵权/盗版资源。

## 实测坑（2026-10-11 本机实录，别重踩）

1. **镜像站常不支持多线程** → 走 `ghproxy.net` 时实测 **`CN:1`**（只给 1 个连接），`-x16` 形同虚设但也不报错。**要真多线程，源站必须支持 Range 分片**（GitHub/官方源支持，多数加速镜像不支持）。
2. **aria2 不读系统代理** → 国外源必须显式 `--all-proxy=http://127.0.0.1:7897`，且**代理得先开着**（2026-10-11 实测本机 7897/7890/10809 均未监听）。
3. **GitHub releases 直连会失败**：aria2 直连 `github.com` 报 `connection attempt failed`/超时；**同期 curl 却能通** —— 所以别因为 curl 通了就以为 aria2 也能直连，直接上镜像（`ghproxy.net`）或代理。
4. **`--daemon=true` 在 Windows 不工作** → 用后台进程方式启动。
5. **路径给原生程序必须 `D:/...` 形式**，给 `/d/...` 会被 MSYS/原生程序误解析（同 `dl_model_resumable.sh` 里记的坑）。

## 验证方式（必须做）
- 下载完用 `stat -c%s` 比对**期望字节数**（别只看"下载完成"的提示）
- 确认文件真实落盘：`ls -la`
- 中断后重跑同一条命令，看是否从断点续（aria2 会读 `.aria2` 控制文件）

## 可选：Motrix GUI
如果凡哥要**可视化界面 + 任务管理**（而不是命令行），再装 `agalwood/Motrix`（Windows 安装包 ~100MB，Electron，底层同一套 aria2 1.37.0-motrix）。它适合手动拖种子、看进度条；**自动化场景用上面 CLI/RPC 更省事**。
