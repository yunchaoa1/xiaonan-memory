# 🌳 工作总控树 · 操作指南

> 给家里小南 — 这棵树是我们俩共享的唯一真相源

---

## 一、树在哪里

| 项目 | 路径 |
|------|------|
| 树文件 | `D:\SDkechengz\dashboard-tree.html` |
| Git仓库 | `D:\Hermes\xiaonan-memory` |
| 凡哥打开方式 | 浏览器打开 `D:\SDkechengz\dashboard-tree.html` |

---

## 二、树的结构

树的数据在 HTML 文件里的 `DATA` 对象中（JavaScript 部分）。结构是：

```javascript
{
  label: "节点名字",
  icon: "🎯",           // emoji图标
  status: "done",       // done | progress | blocked | pending
  count: "57/57",       // 可选，进度数字
  info: "补充说明",      // 可选，灰色小字
  link: "文件路径.md",   // 可选，点击叶子打开的详情文件
  children: [...]       // 子节点
}
```

### 状态含义

| status | 显示 | 含义 |
|:---:|:---:|------|
| done | ✅ 完成 | 彻底搞定，不会再变 |
| progress | 🔜 进行中 | 正在做，或部分完成 |
| blocked | ⚠️ 卡住 | 被某个问题卡住了 |
| pending | ○ 待办 | 还没开始 |

---

## 三、如何更新树

### 方法A：直接改 HTML（推荐）

1. 用文本编辑器打开 `D:\SDkechengz\dashboard-tree.html`
2. 找到 `const DATA = {` 这一行
3. 找到你要改的节点，修改 `status`、`count`、`info` 等字段
4. 保存
5. git commit + push

### 方法B：让公司小南帮你改

在公司小南的 Hermes 对话里说："把 XXX 节点的状态改成 done"，它会自己改。

---

## 四、添加新节点

在对应父节点的 `children` 数组里加一条：

```javascript
{label:"新任务名称",icon:"📌",status:"pending",info:"备注"}
```

叶子节点可以加 `link` 指向对应的 md 文件：

```javascript
{label:"某文档",icon:"📄",status:"done",link:"南溟岛世界观大纲.md"}
```

---

## 五、每天同步流程

### 上班时

```
1. git pull origin main
2. 浏览器打开 dashboard-tree.html 看最新状态
3. 知道今天要做什么
```

### 下班时

```
1. 修改树上对应节点的状态（完成→done，新开始→progress）
2. git add -A && git commit -m "日期: 树的更新说明" && git push
```

---

## 六、当前树的状态（2026-06-30 晚间）

| 模块 | 状态 | 关键待办 |
|------|:---:|------|
| 心魔谱系 | ✅ 完成 | — |
| 世界观体系 | ✅ 完成 | 已对齐凡哥定稿 |
| 38角色 | 🔜 进行中 | 穿越共鸣逐人确认、成长故事、六阶定位 |
| 19反派 | ○ 待办 | 市县对应、心魔组合、反派故事 |
| 世界历史 | ○ 待办 | 各时期角色分配、心魔推演 |
| 穿越剧本 | ○ 待办 | 38人各自触发方式、时间错位 |
| 技术管线 | ✅ 完成 | — |
| 个人发展 | 🔜 进行中 | 学英语在推进 |

---

## 七、注意事项

- **树是唯一真相源**：树上的状态就是项目真实状态，不要依赖日志碎片
- **改完就同步**：改完树立刻 git push，让我（公司小南）能 pull 到
- **叶子的 link 路径**：相对于 git 仓库根目录 `D:\Hermes\xiaonan-memory\`
- **凡哥能看**：他直接在浏览器刷新就能看到最新状态

---

> 🦐 有问题在公司小南的日志里留言，或者直接改树的节点加备注
