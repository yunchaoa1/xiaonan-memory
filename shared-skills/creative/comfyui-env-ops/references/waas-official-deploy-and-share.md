# 云扉官方部署脚本 + 云扉OS 界面地图（2026-10-08 实机读脚本 + 官方文档核实）

> 触发：新账号实例「环境在但模型全没了」／要按官方标准方式部署／用户问「云扉OS 在哪」「共享盘怎么挂」。
> 配对阅读：`waas-cloud-storage-and-mirroring.md`（存储矩阵、共享盘规则）；本篇是它的**操作层**。

## 1. 官方镜像布局 vs 我们自建（差异必须先认）

| 项 | 官方 | 我们自建（h3-0300） |
|---|---|---|
| ComfyUI | `/root/comfyui/ComfyUI` | `/root/h3-0300/ComfyUI` |
| Python | `/root/miniconda3/bin/python`（base + `--system-site-packages`）| `/root/h3-0300/venv/bin/python` |
| 启动 | `/etc/waas-script/restart_comfyui.sh`（平台托管）| 手工 nohup 命令 |
| 模型 | 共享盘 / 数据盘**自动软链** | 手工软链 |

⚠️ **官方脚本路径写死 `/root/comfyui/ComfyUI`，不能直接跑在自建布局上** —— 机制照搬，路径要改。

## 2. 官方脚本包在哪（两份，内容相同）

```
/datasets/utils/ComfyUI/nodes/      ← 云扉官方插件（只读源）
    comfyui-aigate     公模库 3.9TB 同步 + 一键打开云扉OS
    comfyui-waas       云扉基础插件
/datasets/utils/ComfyUI/scripts/    ← 官方脚本（只读源）
    start.sh  restart_comfyui.sh  refresh_models.sh  sync_share_models.sh
```

安装到系统盘（官方「老镜像兼容」命令，ComfyUI 路径按自己的改）：

```bash
cp    /datasets/utils/ComfyUI/scripts/* /etc/waas-script
cp -r /datasets/utils/ComfyUI/nodes/*   /root/comfyui/ComfyUI/custom_nodes
```

**自建镜像缺的正是这个插件** → 所以既没有「公模库同步」也没有「一键打开云扉OS」入口（控制台里当然找不到云扉OS）。这是"环境自己搭的、功能不全"的根因。

## 3. `start.sh` —— 开机自动做的四件事

1. `rm -rf /var/log/waas/*`
2. 建目录 + 软链：`/home/waas/ComfyUI/{models,output}` → `/root/comfyui/ComfyUI/{models,output}`（数据盘 ↔ 程序目录）
3. **`bash /etc/waas-script/sync_share_models.sh`** ← 共享盘模型接入（见 §4）
4. `bash /etc/waas-script/restart_comfyui.sh &` ← 起 ComfyUI

## 4. ★ `sync_share_models.sh` —— 共享盘模型"挂上即用"的实现

```bash
source="/home/personal_share"
destination="/root/comfyui/ComfyUI/"
link_readonly_subdirs $source $destination
```

逻辑（读脚本得到）：
- `get_readonly_subdirs_abs` 解析 `/proc/mounts`，**只挑 `/home/personal_share` 下挂载选项含 `ro` 的子目录**（那些才是真正的共享盘挂载点）
- `symlink_recursive` 对命中的目录**递归 `find -type f`**，逐文件 `ln -s` 到 `<destination>/<相对路径>`，父目录按需 `mkdir -p`
- 已存在的**正确软链跳过**／**指向不同的软链跳过并打印**／**同名实体文件或目录一律跳过**（绝不覆盖）

→ **共享盘一挂上，模型自动出现在 ComfyUI，用户零操作；没挂 → 脚本静默空转、什么都不链。** 新账号"模型全没了"就是这个状态，不是环境坏了。

## 5. `refresh_models.sh` —— 个人/团队模型刷新

- `syncmodels "/home/waas/ComfyUI/models/" → "/root/comfyui/ComfyUI/models/"`（递归软链）
- 再扫 `/home/teams/*/ComfyUI/models/` 同样处理（团队存储）
- 规则：软链的源保持软链、目录递归建、常规文件建软链；**目标已有同名一律跳过**

## 6. `restart_comfyui.sh` —— 官方启动（带 150 秒自检）

```bash
PYTHON_CMD="/root/miniconda3/bin/python"
COMFYUI_SCRIPT="/root/comfyui/ComfyUI/main.py"
PORT=8188 ; LOG_FILE="/var/log/waas/comfyui.log"
# 先 ss -tlnp 找 8188 占用 → kill -9 → nohup 起 → ss -tln 轮询最多 150 秒
$PYTHON_CMD $COMFYUI_SCRIPT --port $PORT --listen 0.0.0.0 --enable-cors-header '*'
```
另按环境变量启动：加密服务（`IMAGE_TAG=COMFYUI_ENCRYPT`，8189/8089）、Ollama（11434）、Aigate 应用（`AIGATE_APP=TRUE`，5006/16539）。

## 7. 云扉 OS 界面地图（用户找不到入口时照这个指）

**入口**：控制台 → **实例管理** → 点开实例 → 中间「**系统工具**」栏，四个按钮：

```
ssh  |  vscode  |  云扉OS  |  jupyterlab
                    ↑ 就是这个
```

**云扉 OS 桌面图标**：此电脑／云端下载／**云扉文件存储**／缓存清理／终端／云扉OS操作指南.mp4／百度网盘／夸克网盘

**「云扉文件存储」**（= 官方文档里的「云扉云存储」）：
- 地址栏输 `/home/personal_share` 回车 → 进共享空间目录；**没挂盘时显示「此文件夹为空」**
- 左侧「快速访问」：桌面/下载/文档/视频/图片/音乐/**waas**/**我的共享**/我的接收/回收站
- 左侧栏目：保险箱／此电脑／系统磁盘／**磁盘管理**／**协作空间**／**我的存储**

⚠️ **控制台「云存储 → 共享空间」页的「新增共享盘」按钮 = 新建一个空盘**。用户要的是"挂载已有盘"时**别让他点这个**（共享盘创建后不能删，会平白多一个空盘）。
⚠️ 「协作空间」里有一个「+ 添加」按钮，**疑似**挂载/接入入口（2026-10-08 未验证到底点得通不通）—— 让用户点开截图再判断，不要断言。

## 8. 新账号「环境在、模型全没」的标准处置顺序

1. **先别下载。** 用户历来"零下载"（模型一直由共享盘/数据盘提供），先怀疑链路而不是数据。
2. 取证两条：
   ```bash
   ls -la /home/personal_share/          # 空 = 共享盘没挂
   mount | grep -iE "share|ceph"          # 只有 /home/waas 的 ceph 挂载 = 共享盘没挂
   ```
   若 `mount` 里连 `/home/waas` 都没有 → 连云存储都没初始化，先处理那一层。
3. 引导挂载共享盘（入口见 §7）。**机器上没有挂载凭据**：`/etc/ceph/` 不存在，`mount` 里平台自己挂的 `/home/waas` 都是 `secret=<hidden>`（密钥平台托管）→ **终端挂不了，只能界面**。
4. 挂上后由官方 `sync_share_models.sh` 自动接入；自建布局用等价命令（结构以 `find` 实际输出为准）：
   ```bash
   find /home/personal_share -type f \( -name '*.safetensors' -o -name '*.gguf' -o -name '*.pt' -o -name '*.pth' \) \
   | while read -r f; do rel="${f#/home/personal_share/}"; rel="${rel#*/}"; \
       mkdir -p "/home/waas/ComfyUI/models/$(dirname "$rel")"; \
       ln -sf "$f" "/home/waas/ComfyUI/models/$rel"; done
   ```
   （`${rel#*/}` 剥掉共享盘名那一层）
5. **公模库能顶的先用公模库**（`/datasets/ComfyUI/models` 是平台级、新账号也有）：核对过 H3 工作流要的 11 个模型里 **7 个公模库有**（主模型 / 一采 UNet / 视频+音频 VAE / 文本编码器 / 重绘 LoRA / taeh3），**4 个没有**（二采 UNet `minimax_h3_fl2va_pruned_w4a8_mixed`、`minimax_h3_bf16_CONSERVATIVE_v5`、两个 Qwen3.6 GGUF）。
   - latent 放大可尝试用公模库官方版改名顶上（**兼容性未验证**）：`minimax_h3_latent_upscaler_3d_fp16.safetensors` → 软链成 `minimax_h3_bf16_CONSERVATIVE_v5.safetensors`
6. 真缺且公模库没有的才下载（源见 §9）。

## 9. H3 缺模型的公开源（会话内查证到确切仓库名）

| 文件 | 源 |
|---|---|
| `minimax_h3_fl2va_pruned_w4a8_mixed.safetensors`（12.5GB）| HF `Kijai/MiniMax-H3-experimental` |
| `Qwen3.6-35B-A3B-uncensored-heretic-NVFP4-Experts-Only-Q8_0.gguf`（20.8GB）| HF `llmfan46/Qwen3.6-35B-A3B-uncensored-heretic-NVFP4-Experts-Only-GGUF` |
| `Qwen3.6-35B-A3B-mmproj-BF16.gguf`（0.9GB）| 同仓库 |

云上 `hf-mirror.com` 实测可连（HEAD → `302` + `accept-ranges: bytes`）。**先挂共享盘再考虑下载** —— 34GB 白下的坑就是这么来的。
