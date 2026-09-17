# 个人版短剧场景 - 页面结构与URL

> 2026-07-23 从原站 `ai.sparkart.hk` 通过 cua-driver 逐页爬取AX树确认

## 进入路径
登录 → 选择个人版 → 场景选择页(`/personal-scene-select`) → 点击「短剧/漫画创作」

## 侧边栏结构（统一）
```
logo(XH) + 「星火智画」  
「短剧创作 · 切换」场景切换按钮  
🏠 工作台  
📄 剧本项目  
🖼️ 图片设计  
🎬 视频创作  
🧩 资产库  
———  
🪙 1683 胶卷余额  
凡哥不平凡 + 月卡 + 9.5折  
2026/08/09 到期  
「收起侧边栏」
```

## 5个核心页面

| 页面 | URL | 对应文件 | 特征 |
|------|-----|---------|------|
| 工作台 | `/dashboard` | dashboard.html | 剧本创作工作室 + 常用工具 + 创作入口 |
| 剧本项目 | `/adaptations` | adaptations.html | 6标签筛选 + 项目卡片 + 「查看制作资料」超链接 |
| 图片设计 | `/image-creation` | image-creation.html | 最近项目 + 其他项目网格 + 新建项目按钮 |
| 视频创作 | `/video-fusion` | video-fusion.html | 同图片设计结构 + 新建视频项目 |
| 资产库 | `/asset-library` | asset-library.html | 项目筛选 + 分类标签 + 资产卡片网格 |

## 已重建文件（2026-07-23）
- `adaptations.html` ✅
- `image-creation.html` ✅
- `video-fusion.html` ✅
- `asset-library.html` ✅
- `dashboard.html` ✅

## 旧版问题
原有克隆的侧边栏是早期凭截图做的，与原站完全不同。所有旧版以旧侧边栏为准的个人页需要逐步替换。
