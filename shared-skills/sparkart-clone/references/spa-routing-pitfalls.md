# SPA 路由陷阱 & cua-driver 背景模式限制

## SPA 路由拦截问题

原站 `ai.sparkart.hk` 和 `team.sparkart.hk` 是 React SPA。客户端路由拦截浏览器 URL 修改。

### 症状
- 用 `set_value(address bar, 'ai.sparkart.hk/workspace-select')` + `key('return')` 后，地址栏显示新 URL 但页面内容不变（仍显示先前页面或显示商品套图替代页）
- 多个不同 URL（`deliverables`, `product-images`, `creative-canvas`, `workspace-select` 等）在 SPA 中可能全部渲染同一组件

### 唯一可靠导航方法
**通过侧边栏点击。** 不要拼 URL 导航。流程：
1. 从当前页面点侧边栏导航链接
2. `wait(seconds=1-2)` 等待 React 重新渲染
3. `capture` 获取新页面 AX 树

### 团队版进入路径
```
workspace-select → 点「进入团队版」→ 场景选择页 → 点 AI影视「进入场景」
→ 团队仪表盘（含侧边栏全部导航）
```

## cua-driver 背景模式限制

### 键盘快捷键被阻止
背景模式下这些快捷键全部返回 error：
- `ctrl+l` — 聚焦地址栏
- `ctrl+a` — 全选
- `ctrl+s` — 保存
- `ctrl+c` — 复制

### 替代方案
| 操作 | 不可用 | 替代 |
|------|--------|------|
| 聚焦地址栏 | `key('ctrl+l')` | `click(element=地址栏)` 然后 `set_value` |
| 输入 URL | `type(text='URL')` | `set_value(element=地址栏, value='URL')` |
| 导航 | 地址栏输入 | 侧边栏点击（最可靠） |
| 全选 | `key('ctrl+a')` | 用 `set_value` 直接覆盖 |

### set_value 优先于 type
`type()` 在非前台 Chrome 窗口不可靠（文本可能未送达输入框）。`set_value()` 直接设 UIA ValuePattern，不需要窗口在前台。
