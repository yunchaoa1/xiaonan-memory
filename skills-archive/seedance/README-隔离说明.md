# Seedance 技能 · 隔离柜

**凡哥 2026-10-22 定**：Seedance 的提示词技能收起来，**他没明说「用 Seedance」时不要翻出来、不要加载、不要引用**。

## 为什么在这

它们不属于任何启用中的技能库路径（`D:\Hermes\skills`），所以 Hermes 不会扫到、skill-router 也不会路由到它们。写 H3 提示词时不会再串味。

## 怎么恢复用

凡哥明确说「这次用 Seedance」时：

```bash
# 临时装回来（30 个目录）
cp -r "D:/Hermes/xiaonan-memory/skills-archive/seedance/"* "D:/Hermes/skills/creative/"
```

用完再收回：

```bash
cd "D:/Hermes/skills/creative" && ls -d seedance-* | xargs -I{} mv {} "D:/Hermes/xiaonan-memory/skills-archive/seedance/"
mv "D:/Hermes/skills/seedance-director" "D:/Hermes/xiaonan-memory/skills-archive/seedance/"
```

## 内容

- `seedance-director`（总入口：导演引擎）
- `seedance-prompt` / `seedance-prompt-short`
- `seedance-audio`（台词/口型/声音层次）
- `seedance-characters` / `seedance-camera` / `seedance-motion` / `seedance-lighting` / `seedance-style` / `seedance-sequence` / `seedance-continuation`
- `seedance-troubleshoot` / `seedance-filter` / `seedance-antislop` / `seedance-vfx` / `seedance-copyright`
- `seedance-interview` / `seedance-interview-short` / `seedance-pipeline` / `seedance-recipes`
- `seedance-core`（Emily2040 原库底座）
- `seedance-examples-zh/ja/ko`、`seedance-vocab-zh/en/ja/ko/es/ru`

来源：Emily2040/seedance-2.0 开源技能包（v6.6.0），原封未改。
