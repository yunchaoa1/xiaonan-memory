---
name: website-cloning
description: 完整复刻网站——从爬取路由表到逐页克隆UI和功能。凡哥说"复刻XX网站"时加载。
---

# 网站复刻工作流

## 阶段一：发现所有页面

### SPA（单页应用）路由提取

SPA所有路径返回200——不能靠HTTP状态码判断。从JS源码提取：

```bash
# 1. 下载HTML找JS bundle路径
curl -sL "https://目标网站" | grep -oP 'src="([^"]+\.js)"'

# 2. 下载JS bundle
curl -sL "https://目标网站/xxx.js" -o /tmp/bundle.js

# 3. 提取路由表
grep -oP '(path:\s*"[^"]*"|"/[a-z][a-z0-9/-]*")' /tmp/bundle.js | sort -u
```

### Playwright JS渲染（SPA需要登录时）

```bash
uv pip install playwright
python -m playwright install chromium
```

然后编写Python脚本登录+导航+提取所有`<a>`链接。

## 核心铁律（今天踩坑总结）

1. **只有凡哥提供的源码+截图才是真相**——JS路由表只能告诉你有哪些URL，不能告诉你页面长什么样
2. **不许脑补**——侧边栏菜单/按钮/弹窗的内容必须来自实际截图，不能靠记忆或推断
3. **每个页面有子状态**——弹窗、标签页、空状态、加载态，全部要截图验证
4. **不同场景分类完全不同**——短剧/电商/新媒体的侧边栏、内部页面、资产库结构都不一样
5. **批量模板就是垃圾**——每页必须逐一验证，不能用循环生成
6. **用凡哥的Chrome操作**——`computer_use` 直接操控桌面浏览器，截取JS渲染后的真实页面

## 凡哥复刻模式：逐页验证法

```
凡哥在浏览器里导航 → 截全屏 + 右键"查看网页源代码"
  → 小南对照截图 + 源码重写HTML
  → 凡哥刷新确认 → ✅ 打勾下一页
```

- 用 `progress.html` 追踪进度（✅ 已对图 / ☐ 待核对）
- 每个页面先问："这页有什么标签/弹窗/空状态？"全部列出来再动手
- 新建按钮后的页面、列表中的详情页、不同Tab的内容——全部要截

## 阶段二：项目结构

```
项目根/
├── index.html          # 着陆页
├── login.html          # 登录
├── register.html       # 注册
├── common.css          # 共享样式
├── dashboard.html      # 主控台
└── ...                 # 其余页面
```

## 阶段三：逐页对照

拿到完整路由表后，每页：
1. 导航到该页面（或用Playwright截图）
2. 对比克隆版本 vs 原始版本
3. 补缺：布局/颜色/间距/交互状态/空状态
4. 标记 ✅ 完成

## 阶段四：交叉验证

用官方使用指南/文档对照功能清单——指南里提到的每个功能入口都必须是可点击的页面。

## 参考资料

- `references/sparkart-routes.md` — 星火智画实际路由表（从JS bundle提取）
- `references/spa-extraction.md` — SPA路由提取完整方法

- 凡哥讨厌脑补：每页必须有原始截图或路由证据
- 先建框架后补细节——22-34-40页是正常迭代过程
- common.css避免重复样式代码
- 暗色主题：`background:#0c0b13; color:#e8e8f0`
- 侧边栏统一280px宽度
