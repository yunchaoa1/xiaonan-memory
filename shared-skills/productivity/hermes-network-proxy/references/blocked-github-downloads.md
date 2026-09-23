# GitHub 被墙时：拿到官方安装包并自证完整性（2026-09-23 实测）

场景：要装一个只在 GitHub 发布的 Windows 软件（本次＝draw.io Desktop）。
本机网络环境：`github.com` 被挡；某些"看起来最官方"的通道照样走不通。下面是实测走通的配方。

## 一、先做分域探测（别对整站下结论）

```bash
for h in github.com api.github.com objects.githubusercontent.com apps.microsoft.com www.yworks.com; do
  printf "%s -> " "$h"
  curl -s -o /dev/null -w "%{http_code} (%{time_total}s)\n" --max-time 8 "https://$h"
done
```

实测结果（2026-09-23）：`github.com` → **000（超时）**；`api.github.com` → **200**；`objects.githubusercontent.com` → 404（＝能连）；`apps.microsoft.com` → 302；`www.yworks.com` → 200。

**结论：只被挡了主域**。API / 微软商店 / 第三方官网都通 → 换个通道就能拿货，不必先去折腾代理。

## 二、四条通道（按推荐序）

1. **微软商店源（Windows 桌面软件首选）**
   ```bash
   # 先搜（会同时给出 winget 源与 msstore 源两条，优先挑 msstore 那条）
   winget search <名字>
   # 再装（winget 不在 PATH 时用 $LOCALAPPDATA/Microsoft/WindowsApps/winget.exe）
   winget install <StoreProductId> --source msstore \
     --accept-package-agreements --accept-source-agreements --disable-interactivity
   ```
   实测：`winget install 9MVVSZK43QQW --source msstore …` → **已成功安装**（draw.io 31.4.5，约 80s，走 Store CDN）。`--disable-interactivity` 必加，否则可能停在交互提示；100MB+ 的下载放后台 + `notify=true`。
2. **镜像前缀**：`https://gh-proxy.com/<原 GitHub Release 直链>` —— 本次 139MB 安装包实测可下（HTTP 206）。`ghfast.top` 同样探通。**走镜像下载后必须核验（见第三节）**。
3. **发行方官网自有分发**（不走 GitHub 的那种）：如 `https://www.yworks.com/resources/yed/demo/yEd-<ver>.zip` → 200。
4. **代理**：只有确认代理内核在监听端口时才有用（见第四节）。

### ⚠️ 陷阱：winget 的默认源 ≠ 能下

`winget` 社区清单里的 URL **常常就是 GitHub Releases 直链** → 被墙时报：

```
InternetOpenUrl() failed. 0x80072efd : unknown error
```

本次 `winget install JGraph.Draw`（winget 源里的"官方包"）就是这样失败的——**"命令看起来最官方" ≠ "网络走得通"**。失败后直接换 `--source msstore`，别反复重试同一条。

## 三、下载件核验配方（走镜像/第三方通道时必做）

```bash
# ① 平台 API 给出 size 与 digest（sha256）
curl -s https://api.github.com/repos/<owner>/<repo>/releases/latest | python -c "
import sys,json; d=json.load(sys.stdin)
print('tag:', d['tag_name'], '| published:', d['published_at'], '| prerelease:', d['prerelease'])
[print(' ', a['name'], a['size'], a.get('digest'), a['browser_download_url']) for a in d['assets']]"

# ② 本地对比
sha256sum <下载的文件>

# ③ Windows 数字签名
powershell.exe -NoProfile -Command "Get-AuthenticodeSignature '<文件路径>' | Format-List Status,SignerCertificate"
```

**判定三连（全绿才算官方原件）**：`size 一致` + `sha256 与 API digest 一致` + `Status=Valid 且签名者＝发行方`。
本次三项全绿：146,762,496 bytes ／ sha256 `4140daba…37fc27`（与 API `digest` 完全一致）／ `CN=draw.io Ltd`（Microsoft ID Verified）。

> 签名证书的 `Not After` 可能已过期（本次 2026-09-10），**只要签名带有效时间戳、Status=Valid 就不必惊慌**。

**装完必须实测一次真实用途**再宣布成功（本次：让 draw.io 打开 D 盘本地 `.drawio` 文件 → 截图确认渲染成功 + 中文界面）。然后删掉已下载的安装包（清理铁律），保留上面的 sha256/签名记录即可。

## 四、代理排查（只读，不擅动凡哥的配置）

- 只看到 `clash-verge-service.exe`（服务）在跑 **≠ 代理可用**：服务负责提权，真正监听端口的是内核（mihomo / clash）。
- 查配置里的端口：
  ```bash
  grep -rn "mixed-port\|mixed_port\|socks-port\|^port" \
    "$APPDATA/io.github.clash-verge-rev.clash-verge-rev/"*.yaml
  ```
  本次读到 `verge_mixed_port: 7897` / socks 7898 / http 7899。
- 查是否真在听：
  ```bash
  netstat -ano | grep LISTENING | grep 127.0.0.1:7897
  curl -s -o /dev/null -w "%{http_code}\n" --max-time 10 --proxy http://127.0.0.1:7897 https://github.com
  ```
  本次：端口**未监听** → 代理路径 000（2s 内失败）。
- **纪律**：凡哥的代理**不擅自改、不擅自起**（环境级禁区）。代理不通 → 就走第一~三节通道；确实需要用代理时，先只读确认端口在听、再问凡哥。
