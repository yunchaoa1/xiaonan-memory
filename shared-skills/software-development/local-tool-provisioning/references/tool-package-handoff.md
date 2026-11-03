# 交付包复检清单（收件人视角）· 2026-11-02 实战

场景：凡哥「给我一个直接能发给小唐的包，里面包含如何使用」→ 我打了
`视频转写工具_给小唐.zip`（6 文件 / 13.4K）→ 凡哥追问「**你确认你给小唐打的这个包裹没有问题吗？**」
→ 按收件人视角复检，**查出 6 处真错**，全部修好复测通过。

结论先写在这：**自己从包目录里跑通 ≠ 交付包没问题。** 包目录 = 我的机器、我的 PATH、我的 venv、
我的盘符布局。收件人那边这四样全不一样。

---

## 一、复检七步（每次打包完默认跑）

在全新目录做，别复用上一轮的测试目录。

```
① 干净解压   powershell -NoProfile -Command "Expand-Archive -Path '<zip>' -DestinationPath '<新目录>' -Force"
             然后 os.listdir 看中文文件名有没有乱码
② 环境自检   在解压目录里跑 环境自检.py，看它给的修复命令是否可直接复制执行
③ 主路径     单文件（真任务）
④ 另一路径   批量目录
⑤ 用户路径   拖拽 run.bat（等价于双击 / 拖文件）
⑥ 错误路径   无音轨素材 / 中文带空格路径 / 缺依赖的 python / PATH 里没 ffmpeg
⑦ 产物校验   结构化输出逐条验格式（本次：srt 时间戳正则 \d\d:\d\d:\d\d,\d{3}）
```

判据：**任何一步的输出看不懂、或落到非预期位置，就还没交付。**

---

## 二、六个 bug：症状 → 根因 → 修法

### 1. 缓存目录写死盘符
- 症状：对方机器没有 `D:` 盘 → 第一次抽音轨就崩。
- 原代码：`CACHE = r"D:/Hermes/cache/audio"`
- 改成：`CACHE = os.path.join(tempfile.gettempdir(), "video_to_text_cache")`
- 同类：默认输出目录也**不能**写死；应 `out_dir = out_dir or os.path.dirname(src)`（源文件旁边）。

### 2. run.bat 取错参数
- 症状：拖拽后输出落到奇怪位置。
- 原：`--out "%~dp2out"` —— `%2` 只有一个参数时根本不存在。
- 改：
  ```bat
  @echo off
  chcp 65001 >nul
  python "%~dp0video_to_text.py" "%~1" --out "%~dp1out"
  pause
  ```
  `%~dp1` = 拖进来的那个文件的目录 → 输出落在视频旁边的 `out\`。
- 另：**bat 内容全 ASCII**，中文写进 bat 十次有八次乱码。

### 3. 裸 Traceback 甩给用户
- 症状：缺 ffmpeg → `FileNotFoundError` 一大段；无音轨视频 → `CalledProcessError` 一大段。
- 改：`subprocess.run(..., capture_output=True)`，自己判 returncode，抛 `SystemExit("中文人话")`；
  无音轨要单独识别 `"does not contain any stream" in stderr`。
- 实测输出：
  - `[错误] 找不到 ffmpeg。请先装 ffmpeg 并加入 PATH（见使用说明第三节）。`
  - `[错误] 这个文件里没有音轨，转不出文字：无声视频.mp4`

### 4. 多 python 装错环境（最容易让人卡死的一条）
- 症状：`ModuleNotFoundError: No module named 'faster_whisper'`，而对方坚信自己装过了 —— 他装到了另一个 python。
- 改：
  ```python
  except ImportError:
      raise SystemExit(
          "[错误] 当前这个 python 里没装转写库。\n"
          f"       现在用的 python 是：{sys.executable}\n"
          f"       装一下：\"{sys.executable}\" -m pip install faster-whisper\n"
          "       （装过还报这个，说明装到了另一个 python 里——用上面这条重装即可）")
  ```
- 自检脚本里也要**打印 `sys.executable`**（本次实测：`python` 在 execute_code 的 subprocess 里指向
  `C:\Users\bobby\AppData\Roaming\uv\python\...`，在 terminal 里指向 Hermes venv —— **两个环境**）。

### 5. 只有 .md 说明书
- 症状：老记事本打开乱码。
- 改：同内容再出一份 `使用说明.txt`，`encoding="utf-8-sig"`（带 BOM）＋ `newline="\r\n"`。

### 6. 说明书只写好处
- 改：单独一节「坦白说清楚：它做不到什么」，列硬边界：
  分不出谁在说话 / 不认画面里的文字 / 音乐噪杂素材差 / 方言掉准确率 / 无显卡明显变慢 / 长视频没压测。
- 价值：让对方**跑之前**就知道边界，省掉「这样对不对 / 为什么不行」的往返。

---

## 三、复测矩阵（最终版全绿）

| 项 | 结果 |
|---|---|
| 环境自检（解压副本） | ✅ 五项全过 |
| 单文件 · 中文＋空格路径 | ✅ 30s 视频 → 14s，15 段 |
| 批量目录 | ✅ 2 个文件逐个转，互不影响 |
| run.bat 拖拽 | ✅ 输出落 `源目录\out\` |
| 无音轨视频 | ✅ 中文提示，退出码 1 |
| 缺 faster-whisper（换 python） | ✅ 中文提示 + 精确安装命令 |
| 缺 ffmpeg（PATH 里抽掉） | ✅ 中文提示 |
| srt 时间戳 | ✅ 30/30 格式正确 |
| 中文文件名经 Expand-Archive | ✅ 无乱码 |

---

## 四、两条容易误判的假警报

1. **srt 时间戳「格式错」其实是打印被截断**：`print(srt[:300])` 把 `00:00:16,980` 截成 `00:00:16,98`，
   看着像 bug。→ **校验结构化产物要用正则扫全量，别看截断的预览**。
2. **`环境自检` 报「没有可用显卡」可能是判据错了**：whisper 系走 **ctranslate2 的 CUDA**，不是 torch。
   正确判据 `ctranslate2.get_cuda_device_count()`（本次先用 torch 误报，改后 ✅ 1 张卡）。

---

## 五、给凡哥的交付话术（照这个格式说）

1. **一个 zip 的完整绝对路径** ＋ 大小
2. 里面有什么（一行一项，不逐文件丢进聊天）
3. 我**实测过的数字**（不是估算）
4. **一条他需要提前知道的现实问题**（本次＝模型 2.9G，让对方拷目录别自己下）
5. 被问「确认没问题吗」时：**先去复检，再回答**；查出问题就直说「原来那个确实有问题，查出 N 处，已修好复测」——
   不要嘴硬，也不要只报好消息。
