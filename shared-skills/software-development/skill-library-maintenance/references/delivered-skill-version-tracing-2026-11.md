# 交付 skill 的版本溯源 · 实战记录（2026-11-04）

凡哥原话：「帮我找到之前给小李写的写作skill，就是那个改过台词密度的那一版」。
没有一份文件名写着"给小李的写作 skill"——靠"规则原文"才锁定唯一一份。

## 结论（当时给凡哥的答案）

| 位置 | 路径 | 版本 / 体积 | 日期 |
|---|---|---|---|
| 活文件（当前生效） | `D:\Hermes\skills\creative\novel-to-screenplay-opc-test\SKILL.md` | `version: 0.3.0-rc` / 17,036 字节 | 2026-09-21 19:05 |
| 交接包副本（diff 零差异） | `D:\Hermes\xiaonan-memory\opc-sim\交接包_OPC平台\01_节点Skill\novel-to-screenplay-opc-test\SKILL.md` | 同上 | 同上 |
| 当时发出去的包 | `D:\Documents\xwechat_files\<账号>\msg\file\2026-09\OPC节点Skill交接包-2026-09-24b.zip` 内同一路径 | 17,036 字节（zip 内 date 2026-09-28） | — |
| ⚠️ 旧包（别用） | `D:\Hermes\xiaonan-memory\opc-sim\OPC交接包_给平台同事.zip` | 内为 `novel-to-screenplay` **v0.2.0-rc 英文版**，8,240 字节 | zip 2026-09-07 |

## 判定"改过台词密度的那一版"靠的是条款原文

活文件 §「对白型铁律（凡哥 2026-09-08 定调）」里这几条是旧包没有的：

- 实测依据：台词密度 **177 字/分钟**、每 3.2 秒一句、单句均 12.3 字、语音覆盖 93.2%
- 每 3 秒一句台词、单次发言 ≤2 句；关键信息段必须拆成多人一问一答（禁一人连说 3 句以上）
- 每集有效台词 **300–350 字**
- **2026-09-08 修订：取消硬字数上限**——节奏看时间不看字数
- 最长无台词段 ≤10 秒

旧版（v0.2.0）整份是英文 OPC 契约，`grep 台词` **0 命中** → 直接判新旧，不用读全文。

## 搜索过程里踩的坑（都值得复现时避开）

1. **`rg ... 2>/dev/null` 静默失败**：本机没装 rg，命令返回空、退出码 0，把 stderr 吞了 →
   当场得出"`台词密度` 全库 0 结果"的**假阴性**。换成 `grep -rln` 才搜出 23 个文件。
   → 结论：**"找不到"之前先证明搜索真的执行了**。
2. **`search_files` 扫 `D:\Hermes` 全目录 timeout**：cache/cron 里几万个小文件，结果被截断。
   限定 `skills`、`xiaonan-memory`、`Documents` 后秒回。
3. **zip 中文名 GBK**：`unzip -l` 输出乱码 / `Binary file (standard input) matches`。
   用 python 还原并拿体积做证据：

   ```python
   import zipfile
   zf = zipfile.ZipFile(p)
   for i in zf.infolist():
       try: n = i.filename.encode('cp437').decode('gbk')
       except Exception: n = i.filename
       if 'novel-to-screenplay' in n:
           print(i.file_size, i.date_time, n)
   ```

4. **文件名不带版本**：`opc-sim\` 里的 `OPC交接包_给平台同事.zip` 看着像最新，其实是 9-07 的旧包。
   必须开包比字节数/正文，不能按文件名或 mtime 排。

## 汇报形态（凡哥认可的）

先说一句实话（"没有文件名写着他，能对上的是这份"）→ 三到四个绝对路径 + 版本/字节/日期 →
"改的是这几条"引原文 → 旧包警告 → **最后只问一句**"要不要单独打个干净的包"。
不擅自打包、不写说明书（问"找/在哪"就只给路径与证据）。
