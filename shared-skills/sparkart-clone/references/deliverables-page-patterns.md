# 制作资料页 (progress.html) 交互模式

## 页面结构
- **路径**：adaptations → 查看制作资料 → progress.html
- **URL**：`/deliverables/{project-uuid}`
- **7个Tab**：总纲 | 分集大纲(0) | 剧本(1) | 分镜脚本(1) | 角色表(N) | 场景表(1) | 道具表(0)
- **Hero区**：←返回+项目名+"最终产物"徽章+"1集 分镜1/1"
- **AI提取提示条**："实体表通过AI智能提取…" + "重新抽取实体表"按钮
- **一键导出**按钮

## 角色表·卡片网格
- `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))`
- 卡片默认 `.char-card` 正常宽度；展开时 `.char-card.expanded` 用 `grid-column: 1/-1`

## 卡片展开/收起
```css
.char-card { cursor: pointer; }
.char-card.expanded { grid-column: 1 / -1; }
.char-hd { /* 头部：avatar + name + badge + arrow */ }
.char-body { display: none; }
.char-card.expanded .char-body { display: block; }
```
- JS `toggleCard(card, e)`：切换 `.expanded` 类 + 箭头文字 `›` ↔ `˅`
- 阻止表单元素点击冒泡（防止填写时误折叠）：`if(e.target.closest('input,textarea,button,label')) return`

## 编辑表单（展开后）
- 两列 grid：左列(名称/角色定位/性别/年龄段/身份/背景/描述)，右列(性格/外貌/别名)
- 底部：保存 + 删除按钮
- 保存按钮默认 `disabled` + `opacity:0.5`；任一字段有内容时启用
```js
body.addEventListener('input', () => {
  const hasContent = Array.from(inputs).some(el => el.value.trim());
  saveBtn.disabled = !hasContent;
});
```

## 搜索过滤
- `oninput="filterCards(this.value)"` → 遍历 `.char-card`，匹配 `.char-hd innerText`
- 清空输入框恢复全部展示
- 新增卡片自动可搜（共享 `.char-card` class）

## 新增卡片
- 点击"+ 新增" → `addCard()` 动态创建 `.char-card.expanded`
- 标题"未命名"（半透明），avatar 用 👤，箭头初始 `˅`（展开态）
- 所有字段空，保存按钮 disabled
- 删除按钮内联 `onclick` 移除卡片 + `updateCounts()`
- 计数动态更新：`totalCount`（角色表(N)）、`uncatCount`（未分类计数）
- 有"主角"徽章的卡片加 `has-badge-role` 类，不计入未分类

## 分镜图卡片（非角色实体）
- avatar 用"分"，indigo 配色，无 description/subtitle/badge
- 展开后表单同角色卡片，名称预填（如"分镜2首帧图"），其他字段空

## ⚠️ 内联 onclick 转义陷阱（致命·2026-07-23实战）

当用 `execute_code` + Python `str.replace()` 构建 HTML 时，**内联 `onclick` 属性中的单引号会触发 Python 字符串转义冲突**。例如：
```html
<!-- 这会失败：单引号冲突 -->
<button onclick="var c=this.closest('.char-card');c.remove();event.stopPropagation()">
```
**解决方案**：优先用 `addEventListener` 代替内联 `onclick`：
```js
// ✅ 正确方式
div.querySelector('.char-hd').addEventListener('click', function(e){
  if(e.target.closest('input,textarea,button,label')) return;
  div.classList.toggle('expanded');
});
```
- 简单的一次性交互（如 `onclick="filterCards(this.value)"`）可以保留内联——无嵌套引号
- 任何含嵌套引号的内联 onclick 必须改用 addEventListener
- 新增卡片在 `addCard()` 函数内注册所有事件监听器
