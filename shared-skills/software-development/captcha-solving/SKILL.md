---
name: captcha-solving
description: 遇验证码/滑块/人机验证时用。ddddocr识别+反检测不触发+云服务兜底。
version: 1.0.0
author: 小南
license: internal
metadata:
  hermes:
    tags: [验证码, 滑块, 人机验证, ddddocr, Turnstile, 反检测]
    related_skills: [camoufox-antidetect, local-web-capabilities, local-tool-provisioning]
---

# 验证码处理（2026-10-11 建）

## When to Use（何时加载）

- 凡哥说「**验证码 / 滑块 / 人机验证 / 过不去 / 一直弹验证 / 不是人**」
- 抓取时被**验证码或人机验证**拦住（`camoufox-antidetect` 也过不去时）
- 提到 **Turnstile / reCAPTCHA / hCaptcha / 极验 / 滑块拼图 / 点选**
- 需要**判断某类验证码到底能不能自动过**


> **起因**：凡哥拿一条抖音视频问我「博主说有绕过验证码的方法，你是不是没学到」。
> **我当时答"开源界无解" —— 错的**。社区有成熟方案，而且工具我早就有（Scrapling 自带 Camoufox + Turnstile 求解）。
> 教训：**别把"某类难"说成"全部无解"**；也别只信单一调研源。

## 先分清：三种「过验证码」根本不是一回事

| 类型 | 本质 | 难度 | 我们的手段 |
|---|---|---|---|
| **① 不触发**（优先） | 让站点不把你当机器人 → **根本不弹** | 中 | **Camoufox** / **Scrapling.StealthyFetcher** ✓ 已有 |
| **② 本地识别**（真破解） | 弹出来了 → 自己算出来 | 图形/滑块/点选可做 | **ddddocr** ✓ 2026-10-11 装 |
| **③ 云端代解**（付费） | 花钱让云服务替你过 | 简单 | Browser Use Cloud / Browserless（**未采用**） |

**博主所说的"云端隔离浏览器轻松突破验证码" = 第③类付费服务，不是开源算法。**

## ① 不触发（能用就用这个）

- **Camoufox**（详见 `camoufox-antidetect`）：定制 Firefox，指纹在 **C++ 层**伪造
- **Scrapling 0.4.15**（**本机已装**）的 `StealthyFetcher` —— **Camoufox 后端 + 自动 Turnstile 能力**，`scrapling.fetchers` 里可直接用
- **决定性变量常是出口 IP**：机房 IP 基本必弹；住宅 IP 好很多。代理没开时很多站必弹

## ② 本地识别：ddddocr（2026-10-11 装，实测可跑）

```python
import ddddocr

# 字符验证码
ocr = ddddocr.DdddOcr(show_ad=False)
print(ocr.classification(open("captcha.png", "rb").read()))

# 滑块缺口：传入 滑块图 + 背景图 → 返回缺口 x 坐标
det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
with open("slider.png", "rb") as f1, open("bg.jpg", "rb") as f2:
    print(det.slide_match(f1.read(), f2.read(), simple_target=True))

# 点选（目标检测）
det2 = ddddocr.DdddOcr(det=True, show_ad=False)
print(det2.detection(open("click.png", "rb").read()))   # 返回候选框坐标
```

**本机实测**：自造字符图 **3/3 识别正确**（自造图简单，只证明可运行）。
**社区数据**（第三方报道，**未在本机真实站点实测**）：字符 ~92%、滑块 ~87%。
**能力清单**（`dir()` 实测）：`classification` / `detection` / `slide_match` / `slide_comparison` / `use_gpu`。

## ③ 云端代解（未采用，但要了解）

以 Browser Use Cloud 为例（**官方文档为证**）：
- 卖点：`Stealth Browsers — Anti-detect, CAPTCHA solving, proxies in 195+ countries`，**$0.02 / 浏览器小时**
- **官方自己写着**：*"Results depend on the site and challenge; **no browser configuration guarantees that every CAPTCHA can be avoided or solved.**"*
- 同类：Browserless（URL 加 `solveCaptchas=true`）、按次计费的打码平台

→ **免费路够用就不买云**（凡哥口径）。

## 边界（诚实说，别过度承诺）

| 类型 | 能不能 | 说明 |
|---|---|---|
| 图形字符 / 滑块 / 点选 | ✅ **本地可识别** | ddddocr；真实站点成功率需实测 |
| Cloudflare Turnstile / JS Challenge | ✅ 有不触发/半自动方案 | Scrapling StealthyFetcher、FlareSolverr(90.38%)、Byparr(92.16%，Camoufox 后端) |
| **行为风控**（无感验证、轨迹分析） | ⚠️ 识别无用 | 只能靠"不触发"（真浏览器 + 好 IP + 人性化操作） |
| **短信验证码** | ❌ | 只能接码平台（付费） |
| **极验/顶象等企业级** | ⚠️ 难度高 | 可能仍需付费 |

## ⚠️ 安全纪律（2026-10-11 调研警告）

GitHub 上存在**仿冒 / 同名高星仓库**（疑似 SEO 农场刷星，例：`CloakHQ/CloakBrowser`、`jo-inc/camofox-browser`）。
**只装官方仓库**，绝不装来路不明的同名包。
参考项（**未核实来源，暂不采用**）：`waguriagentic/captcha-solver`（258★，本地自建验证码 sidecar，覆盖 Turnstile/reCAPTCHA/hCaptcha/AWS WAF/阿里云滑块等 10+ 种，基于 CloakBrowser + cv2）——要用先核实依赖来源。

## 相关技能
- `camoufox-antidetect` —— "不触发"那条路的引擎
- `local-web-capabilities` —— 抓取能力总览与选择
- `local-tool-provisioning` —— 装工具的六步落地链条
