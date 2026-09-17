---
name: creative-project-structure
description: Organize large creative projects (world-building, IP design, character rosters) with split-file architecture + HTML tree dashboard + git sync. Covers sensitive-topic avoidance for Chinese creative content.（中文触发：组织大型创作项目结构（世界观、IP设计、角色名册、文件拆分）时加载）
platforms: [windows, linux, macos]
---

# Creative Project Structure

For large creative projects (50+ characters, complex world-building, multi-era timelines). Replaces monolithic markdown files with a split-file tree + interactive HTML dashboard.

## When to use

- World-building for IP/fiction/game design
- Large character rosters (20+ characters) with complex relationships
- Projects where the user frequently corrects/refines world rules
- Multi-era timelines with cross-era character relationships

## Architecture

```
project-root/
├── dashboard-tree.html          ← Interactive HTML tree (click to open files)
├── world/                       ← World rules (one file per topic)
│   ├── 六界.md                  ← Dimension system
│   ├── 六阶.md                  ← Leveling system
│   ├── 心魔机制.md              ← Antagonist mechanism
│   ├── 渡者频道.md              ← Communication channel
│   ├── 穿越机制.md              ← Crossing-over rules
│   ├── 38角色总表.md            ← Character roster
│   ├── 关系网.md                ← Relationship map
│   ├── 反派体系.md              ← Villain framework
│   └── 世界历史.md              ← World history timeline
├── tech/                        ← Technical pipeline docs
├── heart-demons/                ← Split by volume (not one 4000-line file)
│   ├── 卷一_欲之魔.md
│   ├── 卷二_情之魔.md
│   ├── 卷三_见之魔.md
│   └── 卷四_行之魔.md
├── characters/                  ← One file per character
├── characters/
│   └── 齐白兰_成长故事.md       ← Character growth narratives (separate from prompts)
├── prompts/                     ← AI video/image prompt templates
│   ├── README.md                ← Index by date/character/scene
│   └── 齐白兰_卧室自拍_面试练习生.md
├── tutorials/                   ← Deliverable tutorials/docs
│   └── Hermes安装教程-DeepSeek版.md
├── skills/                      ← Custom skill knowledge base
│   └── video-to-skill/
│       └── README.md            ← Cangjie distillation workflow
└── backup_YYYYMMDD/             ← Full backup before splitting
```

## Core principles

### 1. Split early, not late
Don't wait for files to grow to 4000+ lines. When a single file covers multiple independent topics, split immediately.

### 2. One file = one answer
Each file answers exactly one question. "What are the six realms?" → `world/六界.md`. Not "What is the entire world system?" → one giant file.

### 3. HTML tree as the index
The `dashboard-tree.html` is the entry point. It shows the full project structure with clickable links. Users open it in browser, click any leaf, see exactly that topic.

### 4. Iterative correction = instant update
When the user corrects a world rule, update the specific file AND the tree immediately. Do NOT batch corrections for later.

### 5. Git = end-of-day only
Daytime: edit local files. End of day: cp tree to git repo → commit → push. This avoids mid-day noise and keeps the remote clean.

## The Dashboard Tree

Built as a single self-contained HTML file. Key features:
- Dark theme, Chinese-optimized font stack
- Click parent nodes → expand/collapse children
- Click leaf nodes with `file:` links → open the corresponding md file via `file:///` protocol
- Color-coded status: ✅ done / 🔜 in progress / ⚠️ blocked / ○ pending
- Data is a JavaScript `DATA` object — easy to edit programmatically

### Tree update pattern
```javascript
// Change a status:
{label:"某个任务",icon:"📌",status:"done"}  // was "progress"

// Add a new leaf:
{label:"新任务",icon:"🎯",status:"pending",info:"备注"}

// Add a file link:
{label:"文档名",icon:"📄",status:"done",file:"world/某文件.md"}
```

### Three locations
| Location | Path | Maintainer |
|----------|------|:---:|
| Local working | User-specified (e.g. `D:\SDkechengz\`) | Daytime edits |
| Git repo | `project-root/dashboard-tree.html` | End-of-day sync |
| Home copy | Home machine path | Pull on startup |

## Sensitive topics (Chinese creative content)

When designing content set in China (especially historical/fantasy), avoid:

### 🚫 Never touch
- **近现代革命历史**: Revolutionary history (1911-1949, including 琼崖革命, 红色娘子军, 解放海南)
- **民族起义/冲突**: Ethnic uprisings (白沙起义, 苗族起义, any ethnic conflict)
- **日军侵琼/殖民历史**: Japanese occupation, colonial atrocities (石碌铁矿, 八所港劳工)
- **宗教**: Any religious figure/event as plot driver
- **领土争端**: South China Sea territorial disputes
- **政府/政党**: Any government or party figure/event

### ✅ Safe alternatives
- **民间传说**: Folklore (鹿回头, 黎母创世, 七仙岭仙女)
- **自然现象**: Typhoons, earthquakes, river course changes
- **民俗文化**: 三月三情歌, 人偶戏, 琼剧, 疍家渔排
- **文人轶事**: 海瑞, 苏东坡 (personal stories, not political)
- **濒危物种**: Hainan gibbon, red tree crab
- **饮食之争**: Which town makes the best roast suckling pig

## Pitfalls

- **Don't make the tree too deep**: 3-4 levels max. Beyond that, split into separate subtrees.
- **Don't auto-push tree to git**: Daytime edits stay local. Only push at end of day.
- **Don't merge unrelated corrections**: Each fix = one commit with clear message. "修正: X" not "修了好几个东西".
- **Don't skip backup before splitting**: Always `cp -r` the full project before restructuring.
- **Don't use the same landmark for hero AND villain in the same city**: Each city gets 2 heroes (different landmarks) + 1 villain (third angle: folklore, natural phenomenon, cultural practice).

## Git workflow

```
Daytime:  edit local files + local tree → do NOT git push
End of day: cp tree to repo → git add -A → commit → push
Home startup: git pull → cp tree to local → open browser
```

## Related references

- `references/hermes-tts-chinese.md` — TTS Chinese voice configuration fix (Edge TTS nested config path)

