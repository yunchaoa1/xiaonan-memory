# 星火智画复刻项目

> 日期：2026-07-21
> 状态：34页HTML/CSS全站复刻完成

## 项目路径
`D:\SDkecheng\sparkart-clone\`

## 技术栈
纯静态HTML+CSS，无框架。共享样式 `common.css`，其余页面各自内联样式。

## 页面列表（34页）

### 入口流程（5页）
- `index.html` - SPARK AI着陆页
- `login.html` - 登录
- `register.html` - 注册
- `workspace-select.html` - 工作空间选择
- `scene-select.html` - 场景选择

### 短剧/漫剧场景（12页）
- `dashboard.html` - 工作台
- `adaptations.html` - 剧本项目列表
- `script-create-modes.html` - 剧本五大选择
- `inspiration.html` - 灵感创作
- `adaptation.html` - 剧本改编
- `novel-split.html` - 小说切分
- `script-editor.html` - 剧本编辑器
- `storyboard.html` - 分镜设计器
- `production-materials.html` - 制作资料详情
- `image-creation.html` - 图片项目列表
- `image-generator.html` - 图片生成器
- `video-fusion.html` - 视频项目列表
- `video-editor.html` - 视频编辑器
- `ai-video-tools.html` - AI视频工具

### 角色/场景/资产（5页）
- `character-designer.html` - 角色设计器
- `scene-designer.html` - 场景设计器
- `avatar-library.html` - 虚拟人像库
- `assets.html` - 资产库

### 电商/新媒体（2页）
- `ecommerce-dashboard.html` - 电商工作台
- `socialmedia-dashboard.html` - 新媒体工作台

### 账户系统（4页）
- `profile.html` - 个人中心
- `pricing.html` - 订阅方案
- `project-settings.html` - 项目设置

### 团队版（5页）
- `team-upgrade.html` - 团队版开通
- `enterprise-center.html` - 企业中心
- `team-members.html` - 人员库
- `seat-management.html` - 席位管理
- `usage-stats.html` - 用量统计
- `team-settings.html` - 团队设置

## 设计规范
- 深色主题：`#0c0b13` 底色，`rgba(255,255,255,0.02)` 卡片底色
- 边框：`rgba(255,255,255,0.05)` 标准，hover到 `0.15`
- 主色调：金棕 `#d4b050` / `#8b7a5e`，蓝色 `#8aafff`
- 场景色：短剧=蓝 `#6a9fff`，电商=橙 `#f0a050`，新媒体=绿 `#5cd890`

## 待确认
- 网站实际页面数：JS渲染SPA，无法爬取。根据两份使用指南反推约36页
