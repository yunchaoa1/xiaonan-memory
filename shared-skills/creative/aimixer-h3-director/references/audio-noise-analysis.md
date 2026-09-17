# H3 视频音轨噪声排查方法（mp4 → 数值分析定位噪声类型）

音频杂音的"听感"不可靠，用数值分析区分噪声类型。目标文件为 ComfyUI SaveVideo 输出的 mp4。

## 步骤 1：确认音轨参数

```bash
ffprobe -v error -show_entries stream=codec_type,codec_name,sample_rate,channels,duration \
  -of compact "D:/SDkecheng/ComfyUI/output/video/xxx.mp4"
# 预期：h264 视频 + aac 音频 @32000Hz（H3 AudioVAE 原生 32kHz，直接 mux，未经 44.1k 重采样）
```

## 步骤 2：提取 PCM + 频段能量分析

```bash
ffmpeg -y -v error -i "xxx.mp4" -vn -acodec pcm_s16le out.wav
```

```python
import wave, numpy as np
w = wave.open('out.wav'); sr = w.getframerate(); ch = w.getnchannels()
a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, ch).mean(axis=1).astype(np.float64)
n = len(a)
def band_energy(a, sr, lo, hi):
    sp = np.abs(np.fft.rfft(a * np.hanning(len(a))))  # 长窗谱
    f = np.fft.rfftfreq(len(a), 1/sr)
    return sp[(f>=lo)&(f<hi)].sum() / sp.sum()
print('低频<200Hz: %.1f%%' % (band_energy(a,sr,0,200)*100))
print('低频哼200-500: %.1f%%' % (band_energy(a,sr,200,500)*100))
print('中频0.5-2k: %.1f%%' % (band_energy(a,sr,500,2000)*100))
print('人声2-6k: %.1f%%' % (band_energy(a,sr,2000,6000)*100))
print('高频6k+: %.1f%%' % (band_energy(a,sr,6000,20000)*100))
# 分 5 秒窗找每段频谱主峰（定位哪段时间是什么声音主导）
for s in range(0, n, sr*5):
    seg = a[s:s+sr*5]
    if len(seg)<sr: break
    sp = np.abs(np.fft.rfft(seg*np.hanning(len(seg))))
    f = np.fft.rfftfreq(len(seg), 1/sr)
    print(f'{s/sr:.0f}-{s/sr+5:.0f}s 主峰: {int(f[np.argmax(sp)])}Hz')
```

## 判定参考（2026-09-02 实测案例）

| 特征 | 判定 |
|------|------|
| 高频>6k 占比极低（~0.5%）+ 白噪排除 | 不是电流/白噪声 |
| 接缝处 RMS 平滑、无尖峰 | 不是段拼接爆音 |
| **93% 能量 <500Hz、主峰 100-200Hz、有人声段主峰跳 5kHz** | **低频嗡**——无台词/环境声段落被低频轰鸣主导 |

## 定位到低频嗡后的排查方向（均为待验证项，未实测不得当结论）

1. **H3 双时钟**：video shift 12 / audio shift 3 是两条时钟，stock sampler（res_multistep）单时钟调度理论上使音频失配。凡哥已装 `ComfyUI-MiniMaxH3DualClockSampler` 插件但工作流用的是 stock sampler——启用 DualClock 重跑是对比实验的首选。
2. **分段对照**：凡哥实测单段 14s 干净提示词音频正常、4 段 955 帧长版低频嗡——多段/长时生成相关的差异点（每段独立采样后音频 cat、总 latent 长度、内存 swap 拖慢采样数值稳定性）逐个排查。
3. 若怀疑是内容引导问题（声景写"底噪"被模型放大成嗡），可 mute 段对照（确认噪声只来自 generate 音频）。
