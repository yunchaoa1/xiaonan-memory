# H3 / AI 音乐视频（MV）工作流版图（2026-09-14 调研，含同日修正）

触发：凡哥要「做 MV」「数字虚拟偶像出歌」「歌曲驱动视频」，或问「最新的 MV 工作流」。
证据分级：🟢 本机实测 ｜ 🟡 社区作者自述 / 官方文档（未在本机实测）｜ 🔴 未验证。

> ⚠️ **本文件首版把 `MultiRef` 列为「✅ 首选（最新）」，是错的**，凡哥当场追问后做了时间排序核验并修正（见第二节）。
> 教训已固化进 SKILL.md「选包前：先核『最新』，再判『同代』」。**引用本文件时先看第二节的日期列。**

## 一、先选路线，再选包

| 路线 | 机制 | 适用 | 画风风险 |
|---|---|---|---|
| **A 接力续写** | 上一片段的画面/音频 latent 传给下一片段，长镜头连续 | 访谈、长叙述、单场景长镜 | ⚠️ 累积漂移：线条变粗、色调偏移、风格渐变 |
| **B 独立片段**（MV 主流） | 同一组参考图各自生成 ~5s 片段，最后拼接 | MV（本来就一镜一换） | 低——不继承 latent，风格最稳 |
| **C 音画呼应** | 音频驱动画面律动（LTX-2.3 Audio-Reactive LoRA 等），**不产生对口型** | 无主唱的氛围/空镜段 | 低，但无演唱镜头 |

歌是成品母带时：**B** 是主路，**C** 只用来补氛围段。

## 二、现成方案 —— 按「最后推送」时间排序（🟢 2026-09-14 用 GitHub API 实拉）

排序依据 = `api.github.com/repos/<r>` 的 `pushed_at`，不是搜索快照、不是 README 自述。

| 包 | 最后推送 | ★ | 撞名 | 缺模型 | 说明 |
|---|---|---|---|---|---|
| `xmarre/MiniMax-H3-Flow-Aligned-Regenerate` | **09-14** | 15 | 🔴未验 | — | 高清重生成 / 精确前缀续接，**不是 MV**；含 Continuum 加速路径 |
| **`ukr8b3g-cmyk/ComfyUI-H3-Continuum` v3.8** | **09-12** | **88** | **无 ✅** | 4（皆 turbo LoRA 版本差异，非必需） | 生产级长视频采样器：分段生成 / 审阅 / **局部重做** / 断点续跑；自带 `examples/workflows/MiniMax_H3_Continuum_V38.json`；48 节点；依赖 Spectrum / Turbo / sage / rgthree / KJNodes（多为可选）；作者标注 issue #13 长续接质量未解 |
| **`KabalMcBlade/ComfyUI_MusicVideo`** | **09-11** | 1 | **无 ✅** | 2（LoRA 版本差异） | **MV 专用且极轻（1 个节点）**：母带歌切块 → 逐块独立 REF2VA → FFmpeg 流式存 `shot_###.mp4` → 组装；模型常驻不重复加载 |
| `mohammednabarawy/ComfyUI-MiniMax-H3-Music-Video` | 09-10 | 5 | 🔴未验 | — | 全自动：Whisper large-v3 扒词+时间戳 → LLM 导演层排全曲分镜 → 逐片段断点续跑 → 拼回净音轨。依赖 Turbo + Pixaroma + VHS；需 ≥0.32；`MAX CLIPS` 先设 1 试跑 |
| **`seitanism/ComfyUI-H3-Motion-Context-MultiRef`** | 09-05 | **199** | **撞 4 个 ❌** | 3 | 20 片段 MV、母带音轨整条保护、逐片段提示词、VHS 流式输出。**星最多 / 功能最全，但不是最新，且是唯一有撞车的** → 见 SKILL.md 撞车体检专节 |
| `liaodaobin/comfyui-liao2049` | 08-25 | 3 | **无 ✅** | **0 ✅** | 中文一体化；**内有「数字人 MV 模式」**：独立图片轨道 + 音乐轨道，音乐可拖手柄截取、每图可设 2–15s、尾段按上一帧自动续接；不带权重（复用本机 H3 模型） |
| `Shrek3OnVH5/…NativeAudio-MusicVideo-Workflow` | 08-05 | **91** | 🔴未验 | — | 星数高的老牌：`ComfyUI-H3-NativeAudioLock`（锁源音频进 H3 audio latent）+ 两个 MV 模板 + MV 提示词模板 |
| `sepiablue-ai/minimax-h3-mv-runner`（かみもと） | 08-24 | 1 | — | — | YAML 驱动；**故意不继承视频 latent**；算出 5 帧 preroll 的时间偏移；RTX 4070 跑 30s ≈ 28 min |
| `ethanfel/ComfyUI-MiniMaxH3-Contex-Loop` / `Ltamann/…-Auto-Chain-addon` | 08-2x | — | — | — | 备选：`source_track` 母带模式 / 自动切片排队拼接 |
| **官方模板库** | 跟版本 | — | — | — | `LTX-2.3 IA2V`（图+音→对口型）、`Image → Song → Audio-Reactive Video`、`MiniMax Music 3`；官方 docs：`docs.comfy.org/tutorials/video/minimax/minimax-h3` |

**选型结论（2026-09-14）**：优先**零撞名**的 —— 主选 `H3-Continuum 3.8`（最新 + 逐段重做/续跑正是 MV 所需）或 `liaodaobin 数字人MV`（中文、零缺模型、图片轨道形态最贴虚拟偶像 MV）；`KabalMcBlade` 当轻量一键试水；**MultiRef 已降级**。

⚠️ **未验的命门**：以上只有 MultiRef 的 README 明确「最终 MP4 音轨 = 原曲本身」。`H3-Continuum` / `Kabal` / `liao2049` 是否同样支持**母带整轨锁定**（而非生成近似音频）**尚未读源码确认** —— 这是 MV 的命门，用前必须验，别照抄自己的推荐。

## 三、`NEW - Music Video.json` 解剖（MultiRef 的，UI 格式，196 节点）

**结构**：20 组完全平行的片段链 —— 每组 = `MiniMaxH3ReferenceToVideo`（Ref2VA，接参考图）→ `MiniMaxH3SongMaskedAVContext`（切该片段的母带音频片，音频 mask=0 保护原音）→ `RandomNoise` / `BasicGuider` / `SamplerCustomAdvanced` / `VAEDecode` → `VHS_VideoCombine`；全局件 = `MiniMaxH3MusicVideoController` + `MiniMaxH3StreamLiveMusicVideoToVHS`（流式拼最终 MP4）+ `MiniMaxH3FinalizeVHSOutput` + `MiniMaxH3LastActiveVHSPreviewBarrier` + `MiniMaxH3AudioVAECompatibility`；另有 23 个 `ComfyMathExpression` 算时间偏移。

**要点**
- 对口型由 H3 依母带音频自动完成，**提示词里不写歌词**
- 最终 MP4 音轨 = **原曲本身**（不是各片段生成音频的拼接）
- 形象靠参考图锁，**服装 / 场景 / 动作写在提示词里换**
- 4 个 `LoadImage` = 最多 4 张参考图
- **不含任何 NikoDemon80 原版包的节点** → 与「已存工作流」不冲突（但两包**互相覆盖**照旧存在）

**模型引用（🟢 本机全部已有，无需下载）**

```
UNETLoader        minimax_h3_ref2va_pruned_int8_convrot.safetensors
CLIPLoader        qwen3vl_32b_minimax_h3_int8_convrot.safetensors
VAELoader         minimax_h3_video_vae_int8_convrot.safetensors
VAELoader         minimax_h3_audio_vae_fp32.safetensors
LoraLoaderModelOnly  minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors
```

⚠️ 最后一行本机只有 **`minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors`** →
**在节点里换文件名即可**（采样步数要跟着调到 4），不是缺模型、别去下载。

## 四、实测经验（🟡 社区自述，本机尚未实测）

- **5 帧 preroll 必须算进偏移**：124 帧 @24fps = 5.1667s ≠ 5s。片段 2 起前 5 帧是 preroll，音频切片若不按此补偿 → **对口型越到后面越偏**。示例起始点：0 / 4.958 / 9.917 / 14.875 / 19.833 / 24.792 / 29.750 s
- 分辨率宽高**必须是 32 的倍数**；**20 片段为上限**（≈100s 歌）
- 母带音频 latent 的 noise mask 置 **0** → 音频不被重采样/去噪
- 片段间**换场景**是正解；同一场景长时间连续反而触发路线 A 的漂移
- **接缝口型**：下一片段往回退 ~1s 与上一片段**重叠**，剪辑时有移动余地去对嘴（实测有效，🟡）
- **只喂人声更准**：先把歌做分轨、只喂 vocal 给音频参考，口型比整轨准（🟡）
- 画质：**特写 > 远景**（远景人物小 → 糊 + 崩脸）；`easy cache` 开着会**伤对口型**，唱段建议旁路（🟡）
- `MiniMaxH3SigmaShift`：调高 = 动态大，调低 = 更稳，唱段 ~12 是社区常用值（🟡）

## 五、本机落地状态（2026-09-14，🟢）

- ComfyUI **v0.35.0**（`D:\SDkecheng\ComfyUI`）；内核已原生支持 `minimax_refs`（PR #15439 等价，见 `comfy/model_base.py`）
- H3 模型四件套 + 4step turbo LoRA + VHS / KJNodes / rgthree **全在**
- 已装包来源核对（顺带发现）：**20+ 个 `custom_nodes` 的 `git remote` 指向 `comfyanonymous/ComfyUI`** → 属**手动解压安装**，**不能用 `git pull` 更新**，升级需重新下载
- 已装的相关包：`ComfyUI-H3-Motion-Context`（NikoDemon80 **v0.6.2**）、`ComfyUI_MiniMaxH3_Director`(导演台)、`ComfyUI-MiniMaxH3DualClockSampler`(shuaixn)、`ComfyUI-YCNodes-MiniMax-H3`、`TE-Speed-MiniMaxH3-OSS`、`ComfyUI_Swan_Bits`、`ComfyUI-LTXVideo`；**无 LTX 权重**（`find models -iname "*ltx*"` 为空）→ 走 LTX 路线要先下大模型，H3 路线不用
- 拉包：`git clone` 直连 github 会 `RPC failed; curl 28 Recv failure` → 用
  `git -c http.proxy=http://127.0.0.1:7897 -c https.proxy=http://127.0.0.1:7897 clone --depth 1 <url>`
  （本机 Clash Verge 端口 7897；`curl` 直连 `api.github.com` 反而通，git 必须走代理）

## 六、视频教程（2026-09-14 核验链接真实存在；**内容未看**）

核验手法：YouTube 用 `oembed` 取标题/频道 + 抓 watch 页 `"uploadDate"` / `"viewCount"`；中文平台用 **`web_search` 加 `site:bilibili.com` 操作符**（B 站搜索接口在无登录态下返回非 JSON）。
**给凡哥列教程时必须分清「视频存在已核验」与「内容已看过」**——本次只验了前者，别把标题描述当内容摘要。

- **最贴「母带歌→虚拟偶像 MV」**：B站 `BV1rzuJ6SEiD`（无限数字人·一键来个MV·上传音频）、`BV1ruhN68EaQ`（数字人/动作参考长视频踩坑总结）、`BV1kp8X6AEqX` + `BV1hQuw6UEeQ`（真音频驱动 ≠ 音频参考）
- YouTube：`3LrjnNgU9uc`（fal，8-05，1.87万，MV 全流程拆解）、`0jtzoegQNwg`（8-07，母带歌→对口型，附工作流+音频切段工具）、`qc5C4P_5p6o`（8-07，逐节点最细，8GB 显存）、`VuOYM095Y1U`（8-20，4 步出全片 + 接缝 1s 重叠技巧）、`PBOMfxjAkGw`（8-26，2.05万，四合一含对口型）
- 系统向：B站「程序员萝卜」306/307/308/310/313 集；「ComfyUI-101/104/106」系列（104 = 上下文插件接力，106 = 长视频循环流）
- ⚠️ 教程用的节点包各不相同（`NativeAudio` / 导演台 / LightX2V 版）；**Continuum / Kabal MV 太新，暂无中文视频教程**

## 七、商务边界（诚实口径）

H3 **本地**生成的商用输出需要 MiniMax 商用授权（Comfy 官方声明其为唯一代理）→ 商业交付前单独核验，**别写成「本地生成即可商用」**。
