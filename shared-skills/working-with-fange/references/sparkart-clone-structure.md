# 星火智画 克隆结构

> 项目路径：`D:\SDkecheng\sparkart-clone\`
> 40页 | 严格对应JS源码路由表

## 页面清单

### 入口 (5)
- index.html → `/`
- login.html → `/login`
- register.html → `/register`
- forgot-password.html → `/forgot-password`
- workspace-select.html → `/workspace-select`

### 场景选择 (2)
- personal-scene-select.html → `/personal-scene-select`
- scene-selection.html → `/scene-selection`

### 短剧场景 (8)
- dashboard.html → `/dashboard`
- adaptations.html → `/adaptations` (含4个弹窗模组：灵感/剧本/小说/新建)
- image-creation.html → `/image-creation`
- image-generator.html → (图片生成器，从image-creation进入)
- video-fusion.html → `/video-fusion`
- video-editor.html → (视频编辑器，从video-fusion进入)
- asset-library.html → `/asset-library`

### 电商场景 (4)
- dashboard-ecommerce.html → `/dashboard/ecommerce`
- product-images.html → `/product-images` (→ image-generator)
- tools-ecommerce-video-remake.html → `/tools/ecommerce-video-remake` (→ video-editor)

### 媒体场景 (1)
- dashboard-media.html → `/dashboard/media`

### 通用功能 (20)
- credits.html → `/credits`
- settings.html → `/settings`
- ai-usage.html → `/ai-usage`
- creative-canvas.html → `/creative-canvas`
- audio-generation.html → `/audio-generation`
- tasks.html → `/tasks`
- team.html → `/team`
- invite.html → `/invite`
- deliverables.html → `/deliverables`
- submit.html → `/submit`
- user-feedback.html → `/user-feedback`
- privacy.html → `/privacy`
- terms.html → `/terms`
- content-policy.html → `/content-policy`
- 7个tools页面 (cover-gen/translation/upscale/subtitle-removal/breakdown/remake/viral-remake)

## 侧边栏规则

- 入口页(登录/注册/空间选择/场景选择)：**无侧边栏**
- 短剧场景内部：蓝色高亮+五菜单(工作台/剧本/图片/视频/资产)
- 电商场景内部：橙色高亮+四菜单(应用中心/商品修图/带货短片/资产)
- 媒体场景内部：绿色高亮+五菜单(工作台/文稿/配图/短片/资产)

## 弹窗串联

adaptations.html 包含4个串联弹窗：
1. newModal → 第一步(灵感/剧本/小说三选一)
2. inspoModal → 灵感创作详情
3. adaptModal → 选择剧本→上传/分集
4. novelModal → 选择小说→上传小说

弹窗间通过 `classList.remove/add('show')` 切换。
