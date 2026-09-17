# SPA路由提取方法

## 问题

SPA（单页应用）所有路径返回相同HTML（200状态码）——无法通过HTTP状态区分真实页面和无效路径。

## 解法一：从JS bundle提取（最可靠）

```bash
# 1. 找到JS bundle入口
curl -sL "https://目标网站" | grep -oP 'src="([^"]+\.js)"'

# 2. 下载完整bundle
curl -sL "https://目标网站/完整路径.js" -o /tmp/bundle.js

# 3. 搜索React Router path:（或Vue Router的path:）
grep -oP 'path:\s*"[^"]*"' /tmp/bundle.js | sort -u

# 4. 同时搜索普通路径模式
grep -oP '"/[a-z][a-z0-9/-]*"' /tmp/bundle.js | sort -u | grep -v '/api/' | grep -v '/auth/'
```

## 解法二：Playwright渲染（需登录的站点）

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # 登录
    page.goto("https://目标网站/login")
    page.fill('input[type="text"]', "账号")
    page.fill('input[type="password"]', "密码")
    page.click('button:has-text("登录")')
    page.wait_for_timeout(3000)
    
    # 提取所有内部链接
    links = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('a[href]'))
            .map(a => a.getAttribute('href'))
            .filter(h => h && h.startsWith('/') && !h.startsWith('/api'));
    }""")
    
    print(set(links))
    browser.close()
```

## 解法三：使用指南对照

如果官方有使用指南文档，按指南的目录结构反推页面清单——指南中每个独立操作步骤通常对应一个页面。

## 安装Playwright

```bash
uv pip install playwright
python -m playwright install chromium
```
