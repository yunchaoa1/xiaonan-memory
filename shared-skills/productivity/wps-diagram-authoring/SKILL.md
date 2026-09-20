---
name: wps-diagram-authoring
description: Use when 画/改拓扑图·流程图并要落到本地 WPS 可编辑文件。
version: 1.0.0
author: 小南
license: internal
metadata:
  hermes:
    tags: [wps, diagram, pptx, topology, windows, local]
    related_skills: [team-management-ops, dashboard-tree]
---

# 本地拓扑图 / 流程图（WPS 演示原生形状）

凡哥 2026-09-20：「我希望我们今后画拓扑图是**在本地完成**。」→ 项目拓扑图由小南在本地出图，**不依赖在线服务、不登录**。

## When to Use（何时加载）

- 凡哥说"画 / 改**拓扑图**""**流程图**""项目进展图"
- 要把**外部 AI（豆包 / 飞书）画的图接手到本地**
- 要给项目/团队出一张"能直接给人看"的进展图

## 1. 事实：WPS 没有本地流程图组件（先说结论，别去找"下载这个板块"）

- **桌面版 WPS 没有独立本地流程图/拓扑图板块。** 证据（实查）：`D:\Program Files\WPS Office\<版本>\office6\addons\` 里与图相关的只有 `kpromeprocesson`（＝WPS × ProcessOn **在线**版，**需会员**）、`kpromeworkarea`、`kpromewebapp`。
- WPS 官方给的**本地**画法：**演示 / 文字里的「插入 → 形状」**。
- → "去 WPS 官网下载拓扑图板块"这条**不存在**；凡哥问起就直接说清（他自己搜过"wps有拓扑图功能吗"）。

## 2. 落地形态：python-pptx 生成「原生形状」的 .pptx

| 项 | 值 |
|---|---|
| 生成器 | `D:\Hermes\scripts\gen_topology_pptx.py`（**改数据段重跑＝出图**，3 秒） |
| 输出 | `D:\Documents\我的文档\拓扑图\项目拓扑图_<YYYYMMDD>.pptx` |
| 依赖 | `pip install python-pptx`（本机已装 1.0.2） |

要点：
- 用 `MSO_SHAPE.ROUNDED_RECTANGLE`（卡片/节点）+ `MSO_SHAPE.RIGHT_ARROW`（箭头）画**真形状**，**绝不贴图片** —— 凡哥才能双击改字、拖框、连线。
- 去掉默认阴影：`shape.shadow.inherit = False`；卡片圆角 `shape.adjustments[0] = 0.08`。
- 版式、状态配色、图例、字号规范：`references/拓扑图版式与验证.md`。

## 3. 打开 + 验证（必做，别只看"生成成功"）

1. **打开**：`cmd /c start "" "<pptx>"` 在本机**打不开**（缺正确关联）→ 直接用 WPS 演示 exe：
   `cmd /c start "" "D:\Program Files\WPS Office\<版本>\office6\wpp.exe" "<pptx>"`
2. **定位窗口**：`computer_use action=list_windows` → 找标题＝文件名的 `wps.exe` 窗口，记 `pid` / `window_id`
3. **截窗口**：`computer_use action=capture mode=vision pid=<pid> window_id=<wid>`（read-only，不打扰凡哥）
4. **验版面**：把截图丢给 `vision_analyze` 问三件事 —— 右边界有没有被裁（**多半是视口缩放，不是图错**，看左侧缩略图确认整图完整）、有没有重叠压字、像不像能直接给人看的成品
5. **交付**：把截图 `.png` 一起发给凡哥（MEDIA），他一眼就能判断要不要调

## 4. 素材来源：读飞书 / 豆包那边的内容

- **需要登录的飞书文档（docx）**：外部抓取拿不到正文（curl 只拿到 passport 页；web_extract 也失败）→ 两条路：**① 请凡哥截图**（我有视觉，最快）② 读桌面飞书窗口（下条）。
- **读桌面飞书（Electron 应用）的文字**：`computer_use action=capture mode=ax app=飞书` —— 返回可交互元素 **＋ 整窗文字**，**不用截图**。元素多时回复被截断，**完整清单会落盘到** `D:\Hermes\cache\computer_use\elements_<id>.json` → 直接 `read_file` 读它拿全量文字（本次 150 条，含豆包全部对话）。
- **只读不出手**：凡哥让"了解进展"时**不要点击**；要点/要输入之前先跟他说一声。
- 非 Hermes 自己的密码/支付/订阅类按钮**一律不碰**（豆包订阅弹窗就交给凡哥自己点）。

## 5. 接手外部 AI 的图 → 必查三项（2026-09-20 实测三条全中）

1. **日期是否已过期**（图上写"第一阶段演示目标 2026-09-18"，而当天已是 09-20）
2. **状态口径是否自相矛盾**（① 标"✅ 已完成"却内含"⚠ 卡点"）
3. **节点是否有缺**（制剧工作流到"视频制作"为止，缺 配音 / 合成 / 成片导出）

→ 查到就整理成 **"待凡哥拍板"清单（3 条以内）**，**不自己改**；他拍板后再改脚本数据重跑。语气按 `working-with-fange`：只报差异，不评判对方。

## 6. 交接要登记（做一次就要落到总控台，否则过几天就不知道图归谁）

- `DASHBOARD.md`：记 **维护权归谁** + 文件位置 + 生成器路径（本次记在「10.13 拓扑图本地化」）
- 共享记忆 A 区（`集团\豆包工作记忆.md`）：写明**豆包不再画图、只写 B 区**
- 树形总控台对应节点同步（见 `dashboard-tree`）

## 7. 坑

- `start ""` 打不开 `.pptx` → 用 `wpp.exe` 全路径（§3.1）
- **手动拖形状＝不可复现** → 永远"改脚本重跑"，这才是"接手"的意义
- 给别人看/存档：WPS 演示 →「文件 → 输出为图片 / PDF」
- 可选项（凡哥没点头就别装）：**draw.io Desktop**（免费开源、离线、可导出 vsdx / svg）
- 脚本里数据段是唯一的改动点；改完**必须重新验证版面**（形状位置是硬坐标，加一个框就可能撞车）
