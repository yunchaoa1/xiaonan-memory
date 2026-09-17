# LTX 2.3-22b 模型对比（2026-07-24 实测数据）

## 两个模型的真实数据

| | V3工作流要求 `dev-bf16-fp8` | 凡哥已有的 `distilled-1.1` |
|------|------|------|
| 完整来源 | `szwagros/ltx-2.3-22b-dev-bf16-fp8`（Hugging Face社区版） | Lightricks 官方蒸馏版 |
| transformer (FP8) | 21.4 GB | — |
| transformer (BF16) | 38 GB | — |
| 单文件大小 | — | 46 GB（单一体式checkpoint） |
| 其他组件 | audio_vae (107MB), vae (1.45GB), vocoder (258MB), emb_connector (4GB), txt_proj (2.3GB) | 未知是否包含 |
| 音频VAE | ✅ 独立文件 | ❓ 不确定 |
| 仓库总大小 | 90.5 GB | — |
| HF下载量 | 0（小众） | Lightricks官方 |

## 结论

- V3工作流需要独立的 **audio_vae** 来做音频驱动对口型。凡哥的 distilled-1.1 是单文件46GB，可能不包含音频VAE。
- dev-fp8 的 FP8 transformer 21.4GB——RTX 5080 16GB显存无法完全加载。但凡哥的46GB distilled-1.1 能跑说明 ComfyUI-LTXVideo 有CPU卸载机制，dev-fp8 应该也能用同样方式跑。
- **建议**：先用 distilled-1.1 试试V3工作流——如果音频驱动报错缺 audio_vae，再下 dev-fp8 的 FP8 版（总~29.5GB）。

## 下载地址

`szwagros/ltx-2.3-22b-dev-bf16-fp8` → https://huggingface.co/szwagros/ltx-2.3-22b-dev-bf16-fp8
