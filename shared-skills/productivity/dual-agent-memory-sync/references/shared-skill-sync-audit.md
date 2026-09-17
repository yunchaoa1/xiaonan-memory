# 共享技能同步审计清单

用于任何“两个Agent通过Git共享技能”的环境。目标是分别验证：文件存在、Git同步、运行时安装、目标端加载，避免把四件事混为一谈。

## 一、画出三层路径

先记录，不猜：

| 层 | 当前端 | 另一端 |
|---|---|---|
| Agent实际技能根目录 |  |  |
| Git共享技能源目录 |  |  |
| 安装／镜像目标目录 |  |  |

如果Git共享源就是运行技能目录，也要明确写出；如果不是，必须存在安装或镜像步骤。

## 二、验证Git追踪

对每个共享技能文件检查：

```bash
git check-ignore -v path/to/SKILL.md
git ls-files --error-unmatch path/to/SKILL.md
git status --short -- path/to/SKILL.md
```

判断：

- `check-ignore`命中：文件被排除，不会自然进入提交；
- `ls-files`失败：文件未被Git追踪；
- `status`无输出不能单独证明已追踪，它也可能被忽略；
- 目录中存在文件不等于远端仓库存在文件。

再检查最近提交是否实际包含技能文件：

```bash
git log --name-status -5 -- path/to/shared-skills
```

## 三、验证自动任务范围

检查拉取和推送任务：

- `workdir`是否指向正确Git仓库；
- 提交命令是否覆盖共享技能目录；
- `.gitignore`是否让`git add -A`仍然跳过技能；
- 任务是只提交，还是也完成运行时安装；
- 失败时是否真实报告，不把“无变更”误报为“已同步”。

## 四、建立单一真相源

推荐：

```text
Git仓库/shared-skills/       唯一编辑源
        ↓ install/mirror
当前端Agent技能目录          运行副本
        ↓ git push/pull
另一端Git仓库/shared-skills/
        ↓ install/mirror
另一端Agent技能目录          运行副本
```

规则：

- 只在`shared-skills/`编辑；
- 运行副本不独立修改；
- 只同步自建技能；
- Bundled、Hub安装和插件技能由各自安装机制维护；
- 用Markdown索引记录技能名、版本、状态和目标端适配情况。

## 五、验证安装／镜像

安装动作完成后检查：

- 目标目录包含`SKILL.md`及references/templates/scripts；
- 文件数量和关键文件摘要一致；
- 旧版被新版替换，没有并存两个同名技能；
- 目标Agent能列出并明确加载该技能；
- 当前会话有缓存时，执行重载或开启新会话验证。

## 六、跨Agent差异

不同Agent可能：

- 使用不同技能根目录；
- 支持不同frontmatter字段；
- 不自动识别`related_skills`；
- 需要重启、重载或专用安装命令；
- 对符号链接／目录联接支持不同。

因此先实查另一端规范，再写适配器。不要把Hermes路径直接复制成OpenClaw或其他Agent路径。

## 七、验收结果格式

```text
共享源：已追踪／被忽略／未追踪
远端：存在／不存在／版本落后
当前端运行时：已加载／只存在文件／不可见
另一端运行时：已加载／只存在文件／不可见
自动提交：覆盖／未覆盖
自动安装：存在／不存在
单一真相源：是／否
阻塞项：...
```

只有“Git已追踪＋远端已包含＋目标端已安装＋Agent已加载”四项都通过，才可报告技能同步完成。
