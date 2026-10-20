# .NET 运行时清理实证（2026-10-20，凡哥机）

> 这份是踩坑全记录。结论一句话：**别用 msiexec 卸 .NET，用微软官方 dotnet-core-uninstall；
> 提权前先 dry-run；删完量目录。**

## 1. 现场

- 32GB 内存，`C:\Program Files\dotnet\shared` 共 **1160MB**
- 装了 8 代运行时：`Microsoft.NETCore.App` 3.1.32 / 5.0.17 / 6.0.11 / 6.0.16 / 7.0.20 / 8.0.6 / 8.0.21 / 9.0.4
  ＋ `Microsoft.WindowsDesktop.App` 3.0.3 / 3.1.32 / 5.0.17 / 6.0.11 / 7.0.20 / 8.0.6 / 9.0.4
- ARP 里 **42 条**记录，实为 **16 个运行时**（同一产品在 64/32 位视图各注册一条，还有 `{ABC}` / `{abc}` 双 GUID）
- 机器上**没有 .NET SDK**（`dotnet --list-sdks` 空）、**没有 Visual Studio**（`C:\Program Files\Microsoft Visual Studio` 是空壳）
  → 这些旧运行时是历史安装残留，不是开发工具依赖

## 2. 失败路径：msiexec 假成功（别重走）

```powershell
# 从注册表抓 DisplayName 匹配的条目，逐条静默卸载
Get-ItemProperty $keys | Where DisplayName -match 'Runtime - (...)' |
  ForEach-Object { Start-Process msiexec -ArgumentList "/X$($_.PSChildName) /qn /norestart" -Wait }
```

结果：**成功 23 / 跳过 13 / 失败 0**，然后

```
清理后 dotnet 目录: 1160 MB  (回收 0 MB)
dotnet --list-runtimes → 13 个旧运行时全在
ARP 条目 → 全在
```

**原因**：.NET 运行时（dotnet-runtime-x.y.z-win-x64.exe 这类 Burn bundle）的文件由 bundle / 共享组件持有，
卸载内部 MSI product 不会删 shared framework 目录。**所以退出码 0 在这里毫无意义。**

同一坑也可能出现在别的 Bundle 型安装器上（VS Installer 生态）。通用守则：
**任何卸载，验"目标目录实际大小 + 程序自带清单"，不能只看退出码。**

## 3. 正解：微软官方 dotnet-core-uninstall

### 安装
```
下载 github[.]com/dotnet/cli-lab/releases/latest 的 dotnet-core-uninstall.msi（约 25MB）
msiexec /i dotnet-core-uninstall.msi /qn /norestart      # 需管理员
→ C:\Program Files (x86)\dotnet-core-uninstall\dotnet-core-uninstall.exe
```

### 用法
```bash
EXE="/c/Program Files (x86)/dotnet-core-uninstall/dotnet-core-uninstall.exe"

"$EXE" list                                            # 列出"它管得了"的版本
"$EXE" remove --help                                   # 看全部开关，别凭记忆写

# 试跑（不需要管理员！）
"$EXE" dry-run --all-below 8.0.6 --runtime
"$EXE" dry-run --all-below 8.0.6 --windows-desktop-runtime
"$EXE" dry-run 9.0.4 --windows-desktop-runtime

# 真删（需要管理员，-y 免交互）
"$EXE" remove --all-below 8.0.6 --runtime -y
"$EXE" remove --all-below 8.0.6 --windows-desktop-runtime -y
"$EXE" remove 9.0.4 --windows-desktop-runtime -y
```

### 三个参数坑（我全踩了，每个都让凡哥多点了一次 UAC）

| 写错 | 报错 | 正确 |
|---|---|---|
| `--desktop` | 被当成位置参数，报 "Do not use a version before an option" | `--windows-desktop-runtime` |
| `--runtime --windows-desktop-runtime` 同时给 | "You must specify exactly one of: ..." | 拆成两条命令分别跑 |
| `--all-but 8.0.6 8.0.21` | "Do not use a version before an option: --all-but" | 用 `--all-below <版本>`，或 `remove <版本> ...` |

`--all-below <VERSION>` = 删低于该版本的，该版本本身保留。`--force` 会强删"可能被 VS 使用"的版本（没 VS 时一般用不上）。

### 结果

```
清理前: 1160 MB   →   清理后: 230 MB   (实际回收 930 MB)
剩余: Microsoft.NETCore.App 8.0.6 / 8.0.21，Microsoft.WindowsDesktop.App 8.0.6
C 盘可用: 33.7 GB → 36.6 GB
```

实际回收（930MB）比术前按 `EstimatedSize` 预判的（约 590MB）还多——因为连带清掉了孤儿目录。
**这条也说明：预估永远只能当参考，结果要实测。**

## 4. 直接放弃的部分

`list` 显示 5 个 Core Runtime（3.1.32 / 5.0.17 / 6.0.11 / 7.0.20 / 9.0.4，约 341MB）**不在工具管辖范围**。
剩下两条路都不划算：
- 手动删 `shared\Microsoft.NETCore.App\<ver>` 目录 → 目录能删，但 ARP 条目残留会让以后装 .NET 的安装器误判"已装"
- 连 ARP 一起清 → 要写 HKLM，收益 341MB

**结论：留着。** 凡哥要的是 C 盘变干净，不是把每一 MB 抠到底；为 341MB 动 HKLM 是坏交易。

## 5. 复用到别的机器上

1. `dotnet --list-runtimes` / `dotnet --list-sdks` 先看清有什么
2. 查有没有 VS / SDK：有的话这些运行时是依赖，**先问再动**
3. `dotnet-core-uninstall list` 看工具能管哪些
4. 全部参数先 `dry-run`（不提权）确认
5. 一次提权跑完，日志落 `D:\Temp\`
6. 验：目录大小 + `--list-runtimes`
