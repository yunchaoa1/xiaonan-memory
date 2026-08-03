# 🏗️ 工作总控台

> 小南 2026-07-17 更新 · 每次工作变动同步

---

## 一、齐白兰虚拟偶像 · 出道宣言vlog

| 镜号 | 状态 | 提示词模板 |
|:---:|:---:|------|
| 镜1 · 远景→中景 | ✅ 定稿 | `镜1-出场-定稿模板.md` |
| 镜2 · 中景 | ✅ 定稿 | `镜2-共情-定稿模板.md` |
| 镜3 · 中景 | 🔜 待测试 | 歪头问题已清除，最新版用"嘴角翘起小弧度" |
| 镜4-7 · 中景 | 🔜 待出 | — |

声线：清纯甜美，20岁少女的清透声线，略带娇羞但是保持兴奋。
格式：齐白兰说：{台词} / Qi Bailan speaks: {台词}

---

## 二、LTX 2.3 提示词体系

### 铁律（实测定稿·18条）
①中文可用②全正向禁否定词③近音只换实测：虚拟→须你/别走→停一下/Oi→哦诶④参考图=角色名——性别年龄发型穿搭⑤单人声明⑥眼部约束(额头平滑眼皮半垂)⑦幻觉防范(路人甲+瞪眼抬头纹)⑧台词{}包裹，声线不加括号⑨不写设备操作/剪辑术语/拟型词⑩固定镜头+极简背景⑪凡哥说"镜N"→先采访再输出

### LTX官方指南
提示词长+详细(非精简) | 台词分段+中间插动作 | CFG=2-5默认3禁>7 | 结构：主动作→细节→环境→镜头 | ≤200词

### 避坑实测
✅固定镜头/转椅旋转/Oi拉长调/声线一句写完/背景极简/台词{}无引号/情绪拆物理动作
❌手持晃动/秒数标记/椅子半圈/戳手指/瞪眼抬头纹/抽象词/偶像→偶想(脑补)/Pocket3前置镜头

---

## 三、提示词管线

凡哥说"出提示词"→自动触发：prompt-interview(先问10项)→prompt-master-pipeline(八站)→ltx-video-prompt(弗雷法+模板)→词库(19情绪×265近义词)→避坑→自检(逐字扫描14项)

---

## 四、技能体系

| 类别 | 技能 | 触发 |
|------|------|------|
| 提示词 | prompt-interview | 说"给我镜N提示词" |
| 提示词 | prompt-master-pipeline | 说"写提示词" |
| 提示词 | ltx-video-prompt | LTX相关 |
| 提示词 | prompt-dictionary | 抽象情绪→查词库 |
| 镜头 | shot-language | 说"出分镜/选镜头" |
| 镜头 | seedance-camera/motion/lighting | Seedance相关 |
| Seedance | seedance-director+28技能 | 说"Seedance" |
| 技术 | comfyui-update | 说"更新ComfyUI" |
| 聊天 | barnum-effect | 说"帮我回复" |

---

## 五、南溟岛57角色IP

37正派+1龙+19反派=57人。六界六阶。心魔是世界bug。
文件：`南溟岛世界观·凡哥定稿.md` + `world/` + `heart-demons/`
短剧素材：齐白兰 × 齐镇海《爷爷忘了》已整理为 Word/Markdown，保存到 `D:\Documents\我的文档\齐白兰_齐镇海_爷爷忘了_短剧故事.docx`

---

## 六、知识库

| 库 | 用途 |
|------|------|
| psychology-kb/ | 心理学wiki(37篇)+迷上我(20章) |
| heart-demons/ | 57条心魔谱系 |
| director-kb/ | 导演思维五层 |
| prompts/dictionary/ | 情绪词库(19情绪×265近义词)+镜头逻辑+避坑词库 |

---

## 七、技术环境

ComfyUI v0.27 · RTX 5080 16GB · CUDA 13.0 · torch 2.13.0+cu130 · 端口18188
更新方式：git + uv venv + uv sync
Hermes：OpenAI Codex OAuth · gpt-5.6-sol 主模型；视觉设为 auto 跟随主模型，原生像素识图已验证；gpt-5.5 保留回滚，DeepSeek 保留备用，Agnes 废弃不用
翻墙：v2rayN v7.12.7 · mixed:10808 · TUN 已开；Codex 当前可直连，失败再设 HTTP(S)_PROXY=127.0.0.1:10808
双Agent同步：家+公司Git仓库；cron 已切到 openai-codex/gpt-5.5，但自动触发依赖 gateway/cron scheduler 运行

---

> 📅 最后更新：2026-08-03 · 小南（Hermes）· gpt-5.6-sol 主脑/原生视觉已验证
