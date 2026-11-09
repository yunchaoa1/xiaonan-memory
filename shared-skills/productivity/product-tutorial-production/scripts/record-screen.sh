#!/usr/bin/env bash
# 全屏录屏（Windows / git-bash 实测可用）
# 用法: bash record-screen.sh 输出文件.mp4 [帧率]
# 停止: Ctrl+C —— ffmpeg 收到中断会正常收尾，文件可播

set -u
OUT="${1:-tutorial_$(date +%Y%m%d_%H%M%S).mp4}"
FPS="${2:-30}"
FFMPEG="/d/tools/ffmpeg/ffmpeg"

if [ ! -x "$FFMPEG" ]; then
  echo "找不到 ffmpeg: $FFMPEG" >&2
  echo "先确认路径（which ffmpeg / ls /d/tools/ffmpeg）" >&2
  exit 1
fi

echo "录制中 → $OUT  (Ctrl+C 停止)"
"$FFMPEG" -hide_banner -loglevel warning \
  -f gdigrab -framerate "$FPS" -i desktop \
  -pix_fmt yuv420p -c:v libx264 -preset veryfast -crf 20 \
  -y "$OUT"

echo "已保存: $OUT"
