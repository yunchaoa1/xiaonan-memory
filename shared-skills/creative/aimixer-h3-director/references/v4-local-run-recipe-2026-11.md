# 本地 V4 直投跑片 · 可复用配方（2026-11-19 实测）

工作流：`D:\SDkecheng\ComfyUI\user\default\workflows\4-MiniMaxH3-V4-Singularity版-实测1.json`
实例：主版 `D:\SDkecheng\ComfyUI`（.venv），端口 18188，RTX 5080 Laptop 16G / RAM 31G
产出：`末位_场03_42秒_forest版.mp4`（43.37s / 1440×832 / 24fps / AAC）
      `打斗测试_sdcombat_14秒.mp4`（14.82s / 1440×832）

---

## 一、提交链路（绕开 Qwen 改写后的最小执行图）

```
5 × LoadImage ──► 201.ref_images.ref_image_0..4
                  201.prompt = <六段式常量字符串>
201.av_latent ────► 125.latent_image        （跳过 226 AudioLock）
子图 1297 铺平后：
  UNET 127 ─► 1249 SigmaShift ─► 1362 ─► 1220 ─► 1299 LoraLoaderModelOnly.model   （一采）
  UNET 1221 ─► 1250 SigmaShift ─► 1370 ─► 1222 ─► 1335 LoraLoaderModelOnly.model  （二采）
  CLIP 128 / VAE 119 / VAE_1 120 ─► 201.clip / video_vae / audio_vae
201 ─► 一采采样 ─► 1317 LatentUpscaler3D ─► 二采 ─► 227 / 245 VHS_VideoCombine
```

**从 payload 里删掉的节点**（删了不影响主链路，且省显存）：
`220, 221, 226, 1300, 1301, 1378, 1379, 1380, 1382, 1383, 1384, 1385, 1386, 1387, sg_1369, sg_1371`

- `220/221` 媒体面板与分流器 → 换成 LoadImage
- `226 AudioLock` → `125.latent_image` 直接吃 `201.av_latent`（我们没有参考音频，锁没意义）
- `1301/1379/1380/1382-1387` Qwen 改写链 + 5 套 system prompt
- `sg_1369/sg_1371` 两个 BlockSparseAttention（参数映射易错，删了只影响速度不影响出片）
- `1300/1378` 两个 ShowText 只是显示用，但会引用被删节点 → 必须一起删

---

## 二、201 的关键参数

| 参数 | 值 | 说明 |
|---|---|---|
| `mode` | **`ref2va`** | 绝不能 `auto`（会判成 t2va，参考图全废） |
| `prompt` | 六段式常量 | 不接改写节点 |
| `ref_image_size` | `match` | |
| `width` / `height` | 960 / 544 | 一采 |
| `duration` | 段秒数（float） | 帧数自动 snap 17n+5 |
| `ref_images.ref_image_N` | `["9001",0]`… | N 个 LoadImage，AUTOGROW 不限数 |

## 三、1317 二采上采样参数（必须逐项写对）

```json
{
  "latent": ["1313", 0],
  "model_name": "minimax_h3_bf16_CONSERVATIVE_v5.safetensors",
  "mode": "scale by multiplier",
  "mode.scale": 1.5,
  "align": 32,
  "enable_temporal_chunking": true,
  "force_unload": true,
  "device": "cuda",
  "precision": "fp16"
}
```
`mode.scale` 的点号写法是硬要求，写成 `scale` 报 `Required input is missing ... extra_info: mode.scale`，二采被跳过（只出一采片，不报整体失败）。

## 四、模型路径（照报错字符串抄，别照 ls 抄）

```
unet  : MiniMax-H3\Minimax-h3_Singularity_ref2va_Pruned_v1.3_int8.safetensors   （大写目录）
clip  : MiniMax-H3\qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors                （大写目录）
vae   : minimax-h3\minimax_h3_video_vae_int8_convrot.safetensors               （小写目录）
audio : minimax-h3\minimax_h3_audio_vae_fp32.safetensors                       （小写目录）
```
注意 `vae/` 根目录下还有一个同名 `minimax_h3_video_vae_int8_convrot.safetensors`，两个都可用。

## 五、参考图预处理（必做）

```python
from PIL import Image
im = Image.open(src)
w, h = im.size
if w > 1024:
    im = im.resize((1024, int(h * 1024 / w)), Image.LANCZOS)
im.save(dst_jpg, quality=88)
```
- 原图 2848×1600 / 4.5MB → 1024×575 / ~100KB
- **不缩就崩**：`Fatal Python error: Aborted`，崩点 `vae.py tiled_decode → _decode_pixels → forward`
- 竖版图（如 1728×2304）缩到高 1024 → 768×1024

## 六、跑完的处理

```bash
# 拼接（同参数直接 copy，不重编码）
cd /d/SDkecheng/ComfyUI/output
printf "file 'A.mp4'\nfile 'B.mp4'\n" > list.txt
/d/tools/ffmpeg/ffmpeg -y -f concat -safe 0 -i list.txt -c copy out.mp4

# 抽帧（cv2，路径必须 D:/ 不能 /d/）
cap = cv2.VideoCapture(r'D:/SDkecheng/ComfyUI/output/xxx.mp4')
cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps))
ok, fr = cap.read()
cv2.imwrite(rf'D:/Hermes/cache/f_{t}.jpg', fr)   # 返回 False 就是路径没写成 D:/
```

## 七、服务管理

- 启动：`cd /d/SDkecheng/ComfyUI && ./.venv/Scripts/python.exe main.py --port 18188 --listen 127.0.0.1`
- 启动时刷的 `Traceback` 多为 ComfyUI-Manager 联网拉缓存失败（GitHub 被墙），**不影响跑片**，别当致命错误
- 就绪判定：`curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:18188/system_stats` 返回 200
- 长任务（>10 分钟）用 background + notify，别 foreground 轮询
- 崩溃后重启前先确认旧进程真的死了，否则端口占用

## 八、报错对照

| 报错 | 根因 | 修法 |
|---|---|---|
| `Required input is missing ... extra_info: mode.scale` | 1317 动态 combo 子参数 | 写 `"mode.scale": 1.5` |
| `end_percent ... > max 1.0` | BlockSparseAttention widget 前移 | 删节点 |
| `'X\\f.safetensors' not in [...]` | 目录名大小写 | 照报错列表抄 |
| `KeyError: '1297'` | 子图没铺平 | 展开 13 个内部节点 |
| `Fatal Python error: Aborted`（解码期） | 参考图太大 OOM | 缩到 1024 |
| HTTP 全超时 + 进程消失 | 同上，ComfyUI 已崩 | 重启 + 缩图 |
| 片子里该出现的人不出现 / 道具全不对 | `mode=auto` 判成 t2va | 设 `ref2va` |
