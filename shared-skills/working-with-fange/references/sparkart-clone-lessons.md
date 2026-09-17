# 星火智画克隆项目 · 全流程教训

## 铁律（凡哥多次强调）

1. **1:1复刻，不脑补页面**：从JS源码提取实际路由表→只建存在的页面→删除多余的
2. **路径严格一致**：文件名与官方路由完全对应（`asset-library`不是`assets`）
3. **截图驱动设计**：截原站4张核心页→提取配色/字号/间距/倒角→统一应用到所有页面
4. **批量操作后必须验证**：grep检查断链、检查卡片onclick、检查侧边栏统一

## 技术方法

### 提取SPA路由表
```bash
# 下载JS bundle
curl -sL "https://domain/assets/index-XXXX.js" > bundle.js
# 提取path: 路由
grep -oP 'path:\s*"[^"]*"' bundle.js | sort -u
```

### 统一注入侧边栏
Python脚本批量：删除旧`<aside>`→插入标准sidebar→检查active页面→加chat-bubble

### 统一CSS
common.css覆盖：sidebar(240px)/nav-item/btn-primary(紫渐变)/card/filter-tabs/tool-card/badge/chat-bubble

## 踩坑记录

| 坑 | 后果 | 修复 |
|:---|------|------|
| 脑补页面数量 | 建了56页，多了18个不存在的路由 | 从JS bundle提取真实路由，删到40页 |
| 文件名不对 | assets.html应为asset-library.html | 严格对齐官方路径名 |
| 卡片缺onclick | 三张场景卡点了没反应 | 逐页补onclick |
| 删除文件后链接断裂 | 24页删除后大量404 | grep全站扫描断链修复 |
| CSS不匹配 | 手工写的样式和原站差异大 | 截图后重写common.css |
| SPA所有路径返回200 | 无法用HTTP状态码判断页面存在 | 改用JS bundle提取路由 |
| 批量sed逃逸失败 | shell特殊字符被解析 | 改用Python批量操作 |
