# H3 官方原生 R2V 模板 — 云上可复用资产（2026-09-09 凡哥亲验音频干净）

## 官方模板（ComfyUI 0.30.0 自带，绕开 Director 的 2K 正解）
- 前端：Library → Video → "MiniMax H3：参考生视频"（MiniMaxH3ReferenceToVideo）
- API json 结构速查：UNETLoader(ref2va_pruned_int8_convrot) + CLIPLoader(qwen3vl_nvfp4_awq, type=minimax) + VAELoader×2(video_fp16/audio_fp32) → MiniMaxH3ReferenceToVideo(prompt/width/height/length/ref_image_size=match/ref_images.*) → KSamplerSelect(res_multistep)+BasicScheduler(20步,simple,denoise1)+SamplerCustomAdvanced → CreateVideo(24fps)→SaveVideo
- ResolutionSelector(16:9/megapixels/multiple32)：0.4=864×480、1.0=1376×768、2.0=1920×1088
- 时长：Duration 秒 → ComfyMathExpression `max(5, round(a*24)) + (5 - (max(5, round(a*24)) % 17)) % 17` 自动 17n+5 帧
- 参考图 ref_image_0..8（最多 9 图 + 3 视频 + 3 音频），提示词用 `<Picture N>` 引用

## 凡哥验证过的官方 r2v 提示词（可平移给其他角色：换外观段+图）
```
A warm 3D animated film style, cinematic soft indoor lighting. A young woman around 20 years old, black long straight hair with a white hair clip on the left side, cream knit cardigan over a white camisole, silver necklace with a blue teardrop pendant, light blue cuffed jeans and black shoes, exactly matching the character sheet <Picture 1>. She stands in the entryway of a modest living room, a closed front door directly behind her, warm living room before her. She looks slightly down at first, hands resting naturally at her sides, then lifts her eyes from the floor toward the living room, a soft fond smile forming; her fingers curl gently against the hem of her cardigan, she takes a small breath and holds it a beat, then speaks in a soft warm sweet young female voice at a gentle pace: <d>[Chinese] 爷爷，我回来了。</d> As she finishes, her smile deepens, her eyes soften, and she takes one relaxed half-step forward into the living room, letting the breath out slowly. Soft quiet indoor ambience, faint muffled sounds from outside the closed front door, the light rustle of her cardigan as she moves, the soft fabric sound of her step forward, clear clean audio.
```
要点：全正向（禁 "no hum/no noise" 否定句，用 "clear clean audio"）、台词 `<d>[Chinese] ...</d>` 官方原生支持、纯文本自然语言（不是 Director 六段）。

## 智算云扉(/datasets) H3 模型公模库（只读，软链进共享盘即可用）
- `/datasets/ComfyUI/models/diffusion_models/`：minimax_h3_ref2va_pruned_int8_convrot / ref2va_int8_convrot / fl2va(_pruned)(_int8/bf16/fp8) / fused_refdelta / hybrid 系列
- `/datasets/ComfyUI/models/text_encoders/`：qwen3vl_nvfp4_awq / int8_convrot / bf16、minimax_music3 TE
- `/datasets/ComfyUI/models/loras/`：fl2v_turbo 4step/8step v1.0、4step v1.1_768p、lightx2v、ref2v_turbo_4step、真实电影质感V0.1、training_adapter
- `/datasets/ComfyUI/models/latent_upscale_models/`：minimax_h3_latent_upscaler_3d_fp16/fp32
- `/datasets/studio/huggingface/models/MiniMax-H3/`：原始 HF 权重格式（ComfyUI 不能直接用）
- 软链示例：`ln -s /datasets/.../minimax_h3_ref2va_pruned_int8_convrot.safetensors /home/waas/ComfyUI/models/diffusion_models/`

## 本地工作流 json（D:\数字资产\云电脑工作流\，Director 480P→2K 方案参考）
- minimax_h3_director_r2v_480p_to_2k_云版.json（标准 h3_latent 精修基线）
- minimax_h3_director_r2v_480p_to_2k_turbo_云版.json（+4step turbo LoRA，3步→2MP 模糊，已实测不可用）
- minimax_h3_director_r2v_480p_to_2k_全加速_云版.json（turbo+KJ sage 链；sageattention 2.x 难装，云端跑不了）
- minimax_h3_director_r2v_480p_to_2k_SolAttn_云版.json（SolAttn 替代 sage；3 步无稀疏窗口，仍 OOM）
- minimax_h3_director_r2v_480p_to_2k_重精修_云版.json（10步/denoise0.5 无 turbo；未测完，32GB 预期仍 OOM）
- minimax_h3_director_r2v_480p_to_2k_turbo_小模型_云版.json（pruned+nvfp4；2MP refine 仍 OOM——证明激活峰值问题）

结论：**Director refine 2MP 二采在 32GB 放弃；要 2K 用官方原生模板直接 2.0MP 一采**（或平台换 48GB+ 实例再试 Director）。
