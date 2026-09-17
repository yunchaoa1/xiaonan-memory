# SPA网站1:1复刻流程

> 2026-07-22 星火智画实战总结

## 铁律

1. **每页截图+源码验证后才写代码**。不允许脑补UI元素。
2. **先建进度树**(`progress.html`)，逐页勾，不跳过。
3. **先建结构再补深层**。入口页→列表页→编辑页→弹窗→设置页→工具页→法律页。
4. **同一组件复用**（如图片生成器），不同场景换侧边栏即可。
5. **每种场景侧边栏不同**——电商、短剧、新媒体的菜单和主题色各自独立。

## 流程

1. 提取JS源码路由表 (`grep -oP 'path:"[^"]*"' bundle.js`)
2. 建`progress.html`清单，每页一个checkbox
3. 从首页开始，逐页：用户截图+源代码→小南重写HTML
4. 每写完一页，勾掉`progress.html`对应条目
5. 每写完一页，检查所有链接`onclick`/`href`是否指向存在的文件

## 三类页面模式

### A. 列表页（adaptations/image-creation/video-fusion）
侧边栏+标题+新建按钮+筛选标签+卡片网格(最近项目大卡+其他小卡)

### B. 编辑器页（image-generator/video-editor）
侧边栏+顶部返回栏+左栏/中栏/右栏三栏+底栏输入区

### C. 弹窗模式（adaptations的4个modal）
按钮触发overlay显示/隐藏，弹窗之间可切换

## 已踩坑
- .html文件名必须与路由路径一致(assets→asset-library)
- 批量生成模板后全部作废——浪费时间
- personal-scene-select和scene-selection是同一页面不同路由
- 电商资产库是集合制，短剧资产库是项目制——完全不同
