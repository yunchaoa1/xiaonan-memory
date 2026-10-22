# 云电脑（智算云扉）· OPC 影剧工坊实例：服务入口与启动命令

> 依据：2026-10-10 从实例 **5e4be19a…**（RTX 5090 32G）backup 出来的脚本原文，本机留档在
> `D:\Hermes\cache\opc-deploy\recon\comfyui\start-comfyui.sh`、`...\recon\platform\start-all.sh`、
> `...\instance-check2.txt`（六服务实测日志）。凡哥再问「云电脑启动 comfyui 的命令」时**先读本文件，别现场 grep 记忆**。

## 1. 环境位置（2026-10 起）

| 项 | 值 |
|---|---|
| ComfyUI | **`/root/h3-0300/ComfyUI`**（系统盘，v0.37；旧 `/home/waas/h3-0300` 已作废） |
| venv | `/root/h3-0300/venv/bin/python` |
| 端口 | ComfyUI **8188** · backend 8090 · pi-runtime 8093 · nginx/网页 8094 · PostgreSQL 5432 · Redis 6379 |
| 日志 | `/root/h3-0300/comfyui.log`（平台层另有 `/var/log/waas/`） |

## 2. 只起 ComfyUI（平台自带脚本，推荐）

```bash
setsid nohup bash /root/h3-0300/start-comfyui.sh >/dev/null 2>&1 < /dev/null &
```

脚本原文（6 行，可直接复用）：

```bash
#!/bin/bash
set -euo pipefail
exec 9>/root/h3-0300/comfyui-start.lock
flock -n 9 || exit 0
cd /root/h3-0300/ComfyUI
exec /root/h3-0300/venv/bin/python main.py --port 8188 --listen 0.0.0.0 --disable-auto-launch >> /root/h3-0300/comfyui.log 2>&1
```

- `flock` = 已在跑就直接退出，**不会起两份**（所以「重复执行」是安全的，不需要先 pkill）。
- 脚本用 `exec` 前台接管进程 → **直接 `bash start-comfyui.sh` 会占住当前终端**；要后台必须套 `setsid nohup … &`。
- 等价手打（不经过脚本）：

```bash
cd /root/h3-0300/ComfyUI && unset PYTHONPATH && setsid nohup /root/h3-0300/venv/bin/python main.py --port 8188 --listen 0.0.0.0 --disable-auto-launch >> /root/h3-0300/comfyui.log 2>&1 &
```

## 3. 整套平台一起起（一键做剧要全都在）

```bash
bash /opt/opc-platform/start-all.sh
```

`start-all.sh` = **幂等**编排（`ss -ltn` 探端口，已在监听就跳过）：ComfyUI(8188) → PostgreSQL(5432) → Redis(6379) → pi-runtime(8093) → backend(8090) → nginx(8094)，末尾打印六端口状态。
开跑前会顺手做两步：`check-comfy-models.sh` + `relink-comfy-models.sh`（模型软链自愈），并把 `/root/h3-0300/start-comfyui.sh` 软链到 `/opt/opc-platform/`。

开机自启链：`/opt/opc-platform/start-all.sh` 由平台开机钩子 `setsid nohup … > /var/log/waas/opc-platform-boot.log` 拉起（2026-10-10 实测六服务全活）。

## 4. 验证（约 40 秒后跑）

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8188/system_stats   # 200 = 好了
tail -f /root/h3-0300/comfyui.log
```

## 5. ⚠️ 关于 `--disable-cuda-malloc`（别默认塞进去）

- 历史结论（0.30 / 0.35 云上跑 H3 二采）：**必须带**，不带会崩在显存分配（`Allocation on device`，不是显存不够）。
- 但 **0.37 这套部署脚本没带**，2026-10-10 六服务实测全活、平台在真实跑项目 → **不要因为「记忆里说必带」就去改启动脚本**。
- 正确口径：先按脚本原样起；**只有真出现二采显存分配崩溃**才在 `main.py` 后补 `--disable-cuda-malloc` 重启，并说明「和刚才的命令区别只在多了这个词」。

## 6. 回答凡哥的口径（他定过的纪律）

- 他要「**只启动 comfyui**」→ 只给第 2 节那一行；`pkill` / 检查 / 前置清理**另作单列**并注明何时才需要。
- 一个代码块 = **一条**命令；解释、参数含义一律放块外。
- 他手上可能对着**旧实例**：报「目录不存在」时把路径前缀 `/root` 换 `/home/waas` 即可（旧实例仍活时）。
