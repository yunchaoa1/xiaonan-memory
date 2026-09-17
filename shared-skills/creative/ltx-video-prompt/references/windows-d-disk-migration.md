# Windows 用户文件夹重定向 D盘

## 已完成的重定向

| 系统文件夹 | 注册表键 | 目标路径 |
|------|------|------|
| Desktop | Desktop | D:\admin桌面 |
| Documents | Personal | D:\Documents |
| Pictures | My Pictures | D:\Pictures |
| Music | My Music | D:\Music |
| Videos | My Video | D:\Videos |
| Downloads | {374DE290-...} | D:\下载 |

## 注册表位置

两个位置都需要改（缺一个会导致"位置不可用"）：
```
HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders
HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders
```

## 正确方法

1. 先在D盘建好目标文件夹
2. `reg add` 或 PowerShell `Set-ItemProperty` 改上面两个位置
3. `taskkill /f /im explorer.exe && start explorer.exe` 重启资源管理器
4. 用 `(New-Object -ComObject Shell.Application).NameSpace('shell:Personal').Self.Path` 验证

## 已安装到 D:\Program Files 的软件

- ACE Studio
- Geek Uninstaller
- 金舟录屏
- v2rayN
- 7-Zip

## 软件数据文件夹

D:\AppData（规划中，未完成迁移）

## 未完成迁移的软件

微信、企业微信、WPS、剪映 —— 需在每个软件设置里手动改保存路径
