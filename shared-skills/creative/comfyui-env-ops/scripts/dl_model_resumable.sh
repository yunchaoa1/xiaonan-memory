#!/bin/bash
# 断点续传 + 逐字节校验 + 自动重试的模型下载器（Windows / Git-Bash 实测可用）
#
# 用法：
#   bash dl_model_resumable.sh <url> <目标路径> <期望字节> "<名称>" [代理] [最多尝试次数]
#
# 例：
#   bash dl_model_resumable.sh \
#     "https://huggingface.co/Kijai/MiniMax-H3-experimental/resolve/main/minimax_h3_fl2va_pruned_w4a8_mixed.safetensors" \
#     "D:/SDkecheng/ComfyUI/models/diffusion_models/MiniMax-H3/minimax_h3_fl2va_pruned_w4a8_mixed.safetensors" \
#     12540858008 "w4a8_mixed 主模型 (11.68 GiB)"
#
# 为什么需要它（别用单发 curl）：
#   单发版在网络抖动时留下半截文件就跳去下一个文件，且只打一行 ⚠️ 就继续，
#   后半程根本不知道前一个没下完（2026-09-14 实测：12.5GB 停在 3.8GB 被静默跳过）。
#
# 关键坑：
#   * 目标路径必须是 D:/... 原生形式 —— curl / stat 是原生 Windows 程序，
#     给 /d/... 会当成 D:\d\... → `curl: (23) client returned ERROR on write`，写 0 字节假成功。
#   * 期望字节从 HF `?blobs=true` 的 size 字段取，不要用 du -h（GB 级进位会骗人）。
#   * 存盘就用官方文件名：uv pip 不接受改过名的 wheel，工作流也按名字匹配模型。

set -u

URL="$1"
DEST="$2"
EXPECT="${3:-0}"
LABEL="${4:-$DEST}"
PROXY="${5:-http://127.0.0.1:7897}"
TRIES="${6:-6}"

mkdir -p "$(dirname "$DEST")"

size_of() { stat -c%s "$DEST" 2>/dev/null || echo 0; }

for i in $(seq 1 "$TRIES"); do
  got=$(size_of)
  if [ "$EXPECT" != "0" ] && [ "$got" = "$EXPECT" ]; then
    echo "[$(date +%H:%M:%S)] ✅ $LABEL 已完成并校验通过 ($got 字节)"
    exit 0
  fi
  echo "[$(date +%H:%M:%S)] 第 $i/$TRIES 次下载 $LABEL  (已有 $got / $EXPECT)"
  # --speed-time/--speed-limit：连接假活（挂着但几乎不动）时主动掐断，把控制权交回重试环，
  # 否则 curl 抱着死连接一直挂，后台任务看起来"在跑"其实永远下不完。
  curl -L -C - \
       --retry 8 --retry-delay 5 \
       --connect-timeout 30 --speed-time 60 --speed-limit 1024 \
       -x "$PROXY" -s -o "$DEST" "$URL"
done

got=$(size_of)
if [ "$EXPECT" != "0" ] && [ "$got" = "$EXPECT" ]; then
  echo "[$(date +%H:%M:%S)] ✅ $LABEL 校验通过 ($got 字节)"
  exit 0
fi
echo "[$(date +%H:%M:%S)] ❌ $LABEL $TRIES 次均未完成，停在 $got / $EXPECT"
exit 1
