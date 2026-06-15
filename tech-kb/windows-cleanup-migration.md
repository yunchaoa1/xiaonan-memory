# Windows C盘瘦身 & 软件搬家完整操作手册

> 日期：2026-06-15 | 系统：Windows 11 Home China ×64 | Build 26200  
> 目标：C盘仅存系统+虚拟内存，其余全部迁移D盘

---

## 一、前置准备

1. **备份数据**：重要文件先复制到U盘/网盘
2. **创建目录**：D盘提前建好目标目录（Temp、Desktop、Documents、Downloads、Pictures、Program Files）
3. **关闭程序**：操作前关闭所有应用

---

## 二、用户文件夹迁移（桌面/文档/下载/图片）

### ✅ 正确方法：Windows UI法

**右键文件夹 → 属性 → "位置"选项卡 → 点击"移动" → 选D盘路径 → 应用 → 确认移动文件**

- 桌面 → `D:\Desktop`
- 文档 → `D:\Documents`
- 下载 → `D:\Downloads`
- 图片 → `D:\Pictures`

### ❌ 禁止：手动改注册表法

直接修改 `HKCU\...\User Shell Folders` 的 Desktop 值会导致**文件重复显示**。
原因：Windows 有两组注册表键（User Shell Folders 模板 + Shell Folders 缓存），UI法会自动同步两组键，手动改只改了一组。

**两个必需同步的注册表位置：**
```
HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders  ← 模板
HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders      ← 缓存
```

---

## 三、临时文件路径迁移

### 用户级（无需管理员）
```cmd
setx TEMP "D:\Temp"
setx TMP "D:\Temp"
```

### 系统级（需管理员）
```cmd
setx /M TEMP "D:\Temp"
setx /M TMP "D:\Temp"
```

---

## 四、默认软件安装路径（需管理员）

修改注册表使新软件默认装D盘：
```cmd
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion" /v ProgramFilesDir /t REG_SZ /d "D:\Program Files" /f
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion" /v "ProgramFilesDir (x86)" /t REG_SZ /d "D:\Program Files (x86)" /f
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion" /v ProgramW6432Dir /t REG_SZ /d "D:\Program Files" /f
```

⚠️ **副作用**：C盘已装程序的快捷方式会因 `%ProgramFiles%` 变量变化而失效。
✅ **解决**：对C盘旧程序创建Junction链接（C→D透明桥接）。

---

## 五、Program Files 搬家（robocopy + Junction）

### 5.1 搬家原理

```
真实数据：D:\Program Files\XXX
透明隧道：C:\Program Files\XXX → (Junction) → D:\Program Files\XXX
```

这样无论通过C盘路径还是D盘路径访问，都指向D盘的真实文件。

### 5.2 能搬 vs 不能搬

| 可搬（用户软件） | 不可搬（系统/驱动） |
|-----------------|-------------------|
| Office、VS、NVIDIA、企业微信等 | Windows Defender/PS/NT |
| Google、Kingsoft、NetEase等 | dotnet、Common Files |
| 已Junction的旧程序 | ASUS驱动（内核级） |
| | Notepad++（右键扩展占用） |
| | OBS（虚拟摄像头驱动） |
| | Tailscale（网络驱动） |

### 5.3 搬家脚本核心逻辑

```bat
:: 停服务 → 移文件 → 删原目录 → 建Junction → 恢复服务
net stop "服务名"
robocopy "C:\Program Files\XXX" "D:\Program Files\XXX" /E /COPYALL /R:0 /W:0
rmdir /s /q "C:\Program Files\XXX"
mklink /J "C:\Program Files\XXX" "D:\Program Files\XXX"
net start "服务名"
```

### 5.4 ⚠️ 重要教训

**如果 D:\Program Files\XXX 已存在，必须先合并再创建Junction！**
- 错误做法：D已有同名目录 → 直接删C → 创建Junction → **C盘特有数据丢失**（如微信）
- 正确做法：先 robocopy 合并 → 再删除+Junction

### 5.5 搬不动的处理

| 类型 | 原因 | 方案 |
|------|------|------|
| 驱动级（ASUS） | 内核启动加载 | 留C盘不动 |
| 右键扩展（Notepad++） | DLL被Explorer锁定 | 卸载→重装到D盘 |
| 虚拟设备（OBS） | 虚拟摄像头驱动 | 卸载→重装到D盘 |
| 网络驱动（Tailscale） | 网络栈锁定 | 卸载→重装到D盘 |
| 系统钩子（ByteDance） | 后台常驻 | 卸载→重装到D盘 |

---

## 六、WSL/Ubuntu 搬家

```cmd
:: 1. 关闭WSL
wsl --shutdown

:: 2. 导出备份
wsl --export Ubuntu D:\wsl-backup\ubuntu.tar

:: 3. 注销旧的
wsl --unregister Ubuntu

:: 4. 导入到D盘
wsl --import Ubuntu D:\WSL\Ubuntu D:\wsl-backup\ubuntu.tar

:: 5. 修复默认用户
wsl -d Ubuntu -u root -- sh -c "echo '[user]' >> /etc/wsl.conf && echo 'default=adminneit' >> /etc/wsl.conf"

:: 6. 重启WSL并重启OpenClaw Gateway
wsl -d Ubuntu
```

⚠️ `C:\Program Files\WSL\wsl.exe` 是启动器（几MB），Ubuntu数据在 `D:\WSL\Ubuntu\`，二者分开。

---

## 七、全盘清理

```cmd
:: Windows临时文件
del /q /f /s "C:\Windows\Temp\*"

:: 用户临时文件
del /q /f /s "C:\Users\用户名\AppData\Local\Temp\*"

:: Windows更新缓存（需先停服务）
net stop wuauserv
del /q /f /s "C:\Windows\SoftwareDistribution\Download\*"
net start wuauserv

:: 缩略图缓存
del /q /f "C:\Users\用户名\AppData\Local\Microsoft\Windows\Explorer\thumbcache_*"

:: 回收站
rd /s /q "C:\$Recycle.Bin"

:: 旧的用户文件夹残留（确认已迁移后）
rd /s /q "C:\Users\用户名\Desktop"
rd /s /q "C:\Users\用户名\Documents"
rd /s /q "C:\Users\用户名\Downloads"
```

---

## 八、最终效果

| 盘符 | 总容量 | 占用 | 剩余 |
|------|--------|------|------|
| C盘 | 299GB | 209GB | 90GB |
| D盘 | 624GB | 462GB | 163GB |

**C盘内容：** Windows系统 + 虚拟内存 + 华硕驱动 + 几个搬不动的小程序  
**D盘内容：** 全部用户数据 + 程序 + WSL

---

## 九、操作铁律（总结）

1. **用户文件夹迁移 → 用UI方法，不手动改注册表**
2. **搬不动的程序 → 卸载重装，不硬搬**
3. **Junction创建前 → 检查目标是否已有数据，先合并**
4. **用完的脚本 → 立刻删除**
5. **不确定的事 → 先查教程，不脑补**
