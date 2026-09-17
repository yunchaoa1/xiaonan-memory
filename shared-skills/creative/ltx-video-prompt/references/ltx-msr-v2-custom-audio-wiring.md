# MSR-V2 自定义音频驱动连线方案

> 适用工作流：Licon MSR-V2 多角色参考（`LTX-2.3_-_I2V_多角色参考.json`）

## 加两个节点

在画布空白处右键 → Add Node 搜索添加：

1. `VHS_LoadAudioUpload` — 选歌声文件（MP3/WAV）
2. `LTXVAudioVAEEncode` — 将音频波形编码为 latent

## 两根连线

| 从 | 到 |
|------|------|
| VHS_LoadAudioUpload → audio | LTXVAudioVAEEncode → audio |
| VAELoaderKJ（加载 Audio VAE 的节点）→ VAE | LTXVAudioVAEEncode → audio_vae |
| LTXVAudioVAEEncode → Audio Latent | LTXVConcatAVLatent → audio_latent |

**关键**：新线接入 audio_latent 口后会自动顶掉 LTXVEmptyLatentAudio 的旧连线，不用手动断。

## 调时长

`LENGTH (in seconds)` 节点改成音频文件的实际秒数。

## 参考

- 含完整切换开关的工作流：`LTX-2.3四图+音频数字人工作流.json`（可切换"自定义音频"和"模型生成音频"两种模式）
- Audio VAE 模型：`LTX-Kijai\LTX23_audio_vae_bf16.safetensors`（通过 VAELoaderKJ 加载）
