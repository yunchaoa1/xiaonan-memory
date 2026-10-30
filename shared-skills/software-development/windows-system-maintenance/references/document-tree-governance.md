# 文档目录树治理 · 实战配方（2026-10-30 我的文档整理）

凡哥原话：「把 Documents 这个文件夹里的东西全部整理一遍，把类别分好，设计一套有序的文件夹级别，
**以后框架就不要动，就像树一样有规律的增长**，现在太乱了」。

本次结果：**110 项移动全部成功、0 失败**；根目录从 94 个散文件 → 0；60+ 处路径引用同步、0 残留。

---

## 0. 第一步永远是「量」——不要凭眼睛判断乱在哪

```python
# 只读扫描：每个顶层目录的文件数 / 总大小 / 最近修改时间
import os, time
BASE = r"D:\Documents"
for name in sorted(os.listdir(BASE)):
    p = os.path.join(BASE, name)
    if os.path.isdir(p):
        nf = sz = 0; mt = 0
        for root, _, files in os.walk(p):
            for f in files:
                fp = os.path.join(root, f)
                nf += 1; sz += os.path.getsize(fp); mt = max(mt, os.path.getmtime(fp))
        print(f"DIR {name:24} {nf:6} 个 {sz/1048576:8.1f}MB 最近 {time.strftime('%Y-%m-%d', time.localtime(mt)) if mt else '-'}")
    else:
        print(f"FILE {name:24} 1 个 {os.path.getsize(p)/1024:.0f}KB")
```

**2026-10-30 实测（可直接对照，别当现状）**

| 目录 | 文件数 | 大小 | 判断 |
|---|---|---|---|
| `xwechat_files` | 6,397 | **5G** | 微信聊天文件 → **绝不整理** |
| `WXWork` | 11,999 | 1G | 企业微信 → **绝不整理** |
| `_隔离_20261020` / `_卸载备份_20261020` | 11 / 21 | 152M | 可归档 |
| **`我的文档`** | **265** | **44M** | ✅ 真正要理的 |
| `WPS` / `WeChat` / `剪映项目` / `录屏` / `My Music` / `WinRAR` 等空壳 | 0 | 0 | 软件默认目录，别动 |

**结论一句话给凡哥**：6G 里 5.9G 是微信/企微缓存（动了丢聊天记录），真正乱的是 `我的文档` 里 94 个散文件。

---

## 1. 出树（一级 8 个，永不变）

```
我的文档\
├─ 01_项目\      一个项目一个文件夹；项目内部结构由项目自己定
├─ 02_团队\      考核与绩效\ 会议记录\ 招聘\
├─ 03_汇报与方案\ 呈林总\ 周报与汇总\
├─ 04_规范与工具\ 提示词规范\ 报销与财务\ 蒸馏\
├─ 05_个人\      健康护肤\ 塔罗\
├─ 06_图表\      思维导图\ 拓扑图\
├─ 07_素材\      不属于具体项目的音视频/安装包
└─ 99_归档\      旧版本\ 重复文件\ 待分类\ + 整理日志
```

- **项目并列不套娃**：凡哥明确「十二时辰是单独一个项目，南溟岛是独立的」→ 不要按「IP 下面挂作品」硬套。
  拿不准的归属**问一句**（问两个人的事就分两条消息，按他的「一次只问一个」）。
- 树根写 `目录规范.md`：三条判断顺序 + 铁律（一级不改名不新增）+ 本次留痕 + 「不归这里管的软件缓存清单」。

---

## 2. 迁移脚本的两个关键设计

**① DRY 开关**：`DRY=1` 只打印 `旧 → 新` 全量映射，`DRY=0` 才真搬。

**② 规则表驱动**，不要在一个 if 里堆：
```python
DIR_PLAN = [("电视短剧TV版", "01_项目/电视短剧TV版"), ...]      # 整个目录搬
FILE_RULES = [                                                 # 散文件按顺序匹配
    (lambda n, e: n.startswith("十二时辰_第一卷_") and e == ".mp3", "01_项目/十二时辰/音频"),
    (lambda n, e: n.startswith("十二时辰_第一章_"),                "99_归档/十二时辰_剧本提取旧版"),
    ...
]
# 都不匹配 → 99_归档/待分类（本次只有 1 个：新建文件夹.zip）
```
- **移动而非复制**：`shutil.move`，省空间、不留双份。
- **同名冲突**自动加 `_dup` 后缀，绝不覆盖。
- 每步写日志：`[[旧路径, 新路径, 是否目录], ...]` → `99_归档\整理日志_<YYYYmmdd_HHMM>.json`。

脚本位置：`D:\Hermes\scripts\organize_documents.py`（可直接改 `BASE` 与两张表复用）。

---

## 3. 搬完的三件收尾（漏了就翻车）

### ① 扫引用：写死的绝对路径会全断
```python
log = json.load(open("整理日志_xxx.json"))
pairs = [(sp, dp) for sp, dp, isdir in log] + [(sp.replace("\\","/"), dp.replace("\\","/")) for sp, dp, isdir in log]
# 对 D:\Hermes\scripts、D:\Hermes\skills、xiaonan-memory（含 shared-skills / 集团 / DASHBOARD.md）、树内 .md/.txt/.json 逐个 str.replace
```
- **一定要同时替换 `\` 和 `/` 两种写法**（脚本里 raw string 是反斜杠，md 里常是正斜杠）。
- 修完**再扫一遍确认 0 残留**才回话——「已改」不算，扫过才算。
- 本次命中 60+ 处：转写脚本、思维导图生成、考核表生成、会议纪要管线、多家技能 references。
- 脚本：`D:\Hermes\scripts\fix_paths_after_organize.py`（读日志自动生成替换对）。

### ② 去重：md5 比对，别按文件名猜
本次「新建文件夹」里 17 个 md 与正文**内容完全相同** → 进 `99_归档\重复文件\`；
只要有一份不同就 `_旧版` 后缀留在正文旁，不丢内容。

### ③ 拍平嵌套
`02_团队\会议记录\会议记录\`、`01_项目\电视短剧TV版\电视短剧TV版\` 这类搬出来的双层 → 上移一层再删空壳。

---

## 4. 工具坑（当天各踩一次）

- **长脚本别内联进 `execute_code`**：100+ 行含大量中文串的脚本会被截断，报
  `SyntaxError: unterminated string literal` / `'(' was never closed`。
  → 一律 `write_file` 落到 `D:\Hermes\scripts\xxx.py` 再 `python` 跑。
- **Python 字典/字符串里用全角「」代替英文引号**，避免中文内容里的引号把字符串截断。
- 中文路径 + Git Bash：`git -c core.quotepath=false`；`ls` 路径用 `/d/Documents/...`，
  给原生程序（python/git）的路径用 `D:/Documents/...`。

---

## 5. 别动清单（这类任务永久适用）

| 路径 | 原因 |
|---|---|
| `D:\Documents\xwechat_files` | 微信聊天文件+收到的文件，动了丢记录 |
| `D:\Documents\WXWork` | 企业微信同上 |
| `D:\Documents\WPS` / `WeChat` / `剪映项目` / `录屏` | 软件默认目录，软件自己会用 |
| `C:\Users\<user>\Documents\xwechat_files` 等 | 旧账号的同类缓存，先问再动 |

一句话规则：**目录里全是 `data/`、`cache/`、`Backup/`、`msg*`、`*.db` 这类命名 → 是软件的地盘，不是他的资料。**
