# 案例：风行漫剧频道页（对标分析）· 2026-10-13

**目标页**：`www.fun[.]tv/channel/cartoon`（风行网漫剧频道）
**任务**：凡哥指定为「浪浪椰发布平台（漫剧 APP）」的对标页，要摸清结构做产品需求。

---

## 各层级实测结果

| 手段 | 结果 |
|---|---|
| `web_extract` | ⚠️ 只回来**页脚**（联系我们 / 合作专区 / 隐私协议 / 权利声明 / ICP 备案 / 视听许可证号）——正文全是 JS 渲染，静态抽取拿不到 |
| `browser_exec`（两次，不同 session） | ⚠️ daemon 未起来：`daemon <name> didn't come up -- check ~/.config/browser-harness/tmp/bu-<name>.log` |
| `open_preview` + `read_preview` | ⚠️ 预览窗打开成功，但 `read_preview` 报 "No preview tab is open, or the read timed out." |
| `drive_preview elements` | ⚠️ 超时："The action timed out, or no GUI window answered." |
| **`agent-browser`** | ✅ **走通**，三份全拿到 |
| **截图 → `vision_analyze`** | ✅ 走通，布局信息只有这一步能拿到 |

---

## agent-browser 实际执行的命令

```bash
# ① BIN：先列目录（引号+glob 一行流会失败，见下）
ls -d D:/Hermes/hermes-agent/node_modules/.agent-browser-*/
# → D:/Hermes/hermes-agent/node_modules/.agent-browser-xbGs7Fy5/
BIN="D:/Hermes/hermes-agent/node_modules/.agent-browser-xbGs7Fy5/bin/agent-browser.js"

mkdir -p /d/Hermes/cache/fun
node "$BIN" open "https://www.fun.tv/channel/cartoon"
node "$BIN" get title                  # → 漫剧频道-漫剧大全-在线观看-风行网
node "$BIN" snapshot -i -c             # 结构
node "$BIN" screenshot --full "D:/Hermes/cache/fun/cartoon_full.png"   # 750KB
node "$BIN" screenshot "D:/Hermes/cache/fun/cartoon_top.png"
node "$BIN" eval "document.body.innerText.substring(0,2500)"           # 文案
```

**失败的那一行（留作反例）**：

```bash
export BIN="$(ls -d D:/Hermes/hermes-agent/node_modules/.agent-browser-*/bin/agent-browser.js 2>/dev/null | head -1)"
# → Error: Cannot find module 'D:\Hermes\hermes-agent\node_modules\.agent-browser-xbGs7Fy5\bin\agent-browser.js*'
```

glob 未展开 → 变量里是**字面 `*`**。**必须先 `ls -d` 看目录名，再用真实路径。**

（`agent-browser` 要求真 tty：`terminal(background=true, pty=true)` + `process(action='wait')` 读输出；不能管道给 head/grep。）

---

## 抓到的页面结构（Web 端 · 实测）

| 区块 | 内容 |
|---|---|
| 顶部导航 | 首页 / 电视剧 / 电影 / VIP / 新时代 / **漫剧** / 少儿 + 筛选 + 搜索 + 会员/下载/历史/登录 |
| **Hero 首屏** | 左文字（剧名 + 一句话简介 + 标签「动态漫·古代言情·全53集·VIP·7.8分」+ **立即播放**按钮）+ 右大幅人物剧照 |
| Hero 下方 | **一排小海报轮播 6 张**（VIP 角标 + 剧名） |
| 题材筛选 | **横向胶囊按钮 12 类**：古言权谋 / 末世科幻 / 逆袭爽文 / 虐恋情感 / 青春校园 / 仙侠玄幻 / 性别反转 / 纯爱专区 / 宫斗宅斗 / 古代言情 / 民国风云 / 末世求生（最右有收起箭头） |
| **人气强档** | **大卡片横排**（大幅封面 + VIP 角标 + 底部一句话简介）+ 右下角音乐按钮 |
| 完结精选 | 封面网格（12 部：封面 + 标题 + 一句话简介） |
| **该页没有** | 评论区 / 弹幕 / 排行榜数字（→ 正是客户要"升级"的地方） |

**⚠️ 关键教训**：`snapshot` 和 `innerText` 都**看不出"人气强档是横排大卡片"**——这是**看截图**确认的。布局问题以截图为权威。

---

## 本次任务的口径沉淀（凡哥）

- 对标只对**漫剧**，且"会议功能要完善"
- 成品形态：**手机端软件 → 竖屏手机布局**
- 首页自上而下：**推荐剧（可左右滑动，背景=光标选中漫剧封面放大）→ 人气排行（靠前的剧带该剧热度最高评论）→ 底部导航**；首页要有**显眼合作入口**
- 开发策略：**先对标一个做出来，再一步步改**（不做大而全）
