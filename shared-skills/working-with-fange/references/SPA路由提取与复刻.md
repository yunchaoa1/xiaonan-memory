# SPA网站路由提取与全站复刻

## 适用场景
凡哥要求分析或复刻JS渲染的单页应用（React/Vue SPA）

## 步骤

### 1. 登录拿token
```bash
curl -s -X POST "https://target.com/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"identifier":"phone","password":"pwd"}' \
  -c cookies.txt
```
注意：API字段名可能是`identifier`而非`email`，根据报错调整。

### 2. 下载JS bundle
```bash
curl -sL "https://target.com" | grep -oP 'src="([^"]+\.js)"' 
curl -sL "https://target.com/assets/main-xxx.js" -o bundle.js
```

### 3. 提取路由表
```bash
grep -oP 'path:\s*"[^"]*"' bundle.js | sort -u
```
过滤规则：排除 `/api/` `/auth/` `/payment/` `/oss/` 等后端路径，只保留前端页面路由。

### 4. 验证路由真实性
SPA所有路由返回200（因为index.html兜底）→ HTTP状态码无法区分真伪。唯一验证方式：
- 用Playwright登录后逐页截图
- 或用JS bundle中的路由定义对照

### 5. 逐页建HTML
- 每个路由一个.html文件，命名与路由对应（`/dashboard/ecommerce` → `dashboard-ecommerce.html`）
- 共享样式文件 `common.css`

### 6. 全站链接扫描
```bash
grep -rn "href=\|onclick=.*href=" *.html | while read line; do
  target=$(echo "$line" | grep -oP "href=['\"]([^'\"]+)" | head -1)
  [ ! -f "$target" ] && echo "❌ $line"
done
```

## 教训

- strict 1:1 复制时，删掉所有非官方路由的页面。SPA里的弹窗/内嵌组件对应的是组件而非URL
- 文件名必须与路由严格对应——不能自作主张起中文别名
- **弹窗模式识别**：真实站点中新建项目→选择剧本/小说/灵感→都是弹窗串联，不是一个独立URL。`/adaptation` `/import-screenplay` `/new` 实际都是 `adaptations.html` 内的modal state
- **侧边栏出现时机**：不是所有内部页都有侧边栏。入口页（登陆/注册/空间选择/场景选择）无侧边栏，进入具体工作台后才出现
- **逐页截屏核对法**（最有效）：凡哥截图+源码→小南对照重建。不要批量生成后声称"完成"——逐页人工审核
- **进度追踪树**：建一个`progress.html`清单页，每核对完一页勾掉，凡哥能看到进度
- **批量生成的页面只是占位符**：用Python/Shell批量生成的页面结构和样式都是模板化的，必须逐页重写才能`1:1`
- **先列缺失再补**：从JS bundle提取完整路由表→和已有页面交叉对比→列出精确缺失清单→逐页补

## 逐页核对工作流（本次实战验证）

1. 凡哥打开目标页面 → 截全屏 + 右键查看网页源代码 → 发给小南
2. 小南对照截图重写HTML → 凡哥刷新检查
3. 每个页面的所有可点击入口都要追踪——弹窗/跳转/标签切换全部截到
4. 页面内有tab/弹窗/子入口的，每层都要截
5. 核对通过后在progress.html打勾
