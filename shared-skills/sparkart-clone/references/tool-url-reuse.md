# 原站工具URL复用模式

发现于2026-07-24逐页爬取个人版工具时。多个URL跳转到同一页面。

## 复用页：商品套图（上传商品图→一键生成5张主图）

以下URL全部跳转到同一个商品套图页面：

| URL | 说明 |
|-----|------|
| `ai.sparkart.hk/tools/cover-gen` | 商品套图入口 |
| `ai.sparkart.hk/tools/video-remake` | → 商品套图 |
| `ai.sparkart.hk/tools/ecommerce-video-remake` | → 商品套图 |
| `ai.sparkart.hk/creative-canvas` | → 商品套图 |
| `ai.sparkart.hk/deliverables` | → 商品套图 |
| `ai.sparkart.hk/product-images` | → 商品套图 |

## 克隆策略

只维护一个 `tools-cover-gen.html`（商品套图页面）。其余URL在克隆中可以作为重定向或直接链接到同一个文件。不需要为每个URL建独立HTML文件。

## SPA路由注意

原站是React SPA，路由由前端JS接管。`team.sparkart.hk` 和 `ai.sparkart.hk` 共享同一应用，通过scene/workplace切换区分团队/个人模式。URL路径不一定对应独立页面——可能只是SPA内部state切换。

## 已验证的工具页（独立页，非复用）

- `ai.sparkart.hk/tools/video-translation` → AI视频翻译 ✅
- `ai.sparkart.hk/tools/video-upscale` → AI增强 ✅
- `ai.sparkart.hk/tools/subtitle-removal` → 字幕擦除 ✅
- `ai.sparkart.hk/tools/video-breakdown` → 参考视频解析 ✅
