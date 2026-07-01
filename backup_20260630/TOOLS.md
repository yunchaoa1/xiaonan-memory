# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## 翻墙代理（查外网用）

- Windows 代理地址：`http://172.26.112.1:7890`
- 使用方式：`curl -x http://172.26.112.1:7890` 或 `export https_proxy=http://172.26.112.1:7890`
- 注意：只在需要查 HuggingFace/GitHub/Google 等外网时用

## Windows AI Toolkit

见 `skills/comfyui-wsl/windows-aitk-rules.md` — 所有 Windows 侧操作必须遵循该规则文件。

核心：所有装 D 盘、AI Toolkit 和 ComfyUI 环境彻底隔离、通过 cmd.exe 操控 Windows。

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## Related

- [Agent workspace](/concepts/agent-workspace)

## Windows 路径速查

- 💻 **桌面：** `D:\Desktop`（不是 C 盘！用户文件夹已迁到 D 盘）
- 📁 **临时文件：** `D:\temp\`
- 🎬 **ComfyUI：** `D:\SDkecheng\ComfyUI\`
- 🐍 **Python：** `D:\Python312\python.exe`
