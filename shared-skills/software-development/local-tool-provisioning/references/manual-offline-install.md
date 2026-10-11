# 离线 / 手动安装配方：当安装器被 GitHub API 限流卡住时

> 2026-10-11 实战走通（Camoufox，1.31 GB 内核）。**思路可复用于任何用 GitHub release 发二进制的工具。**

## 什么时候用

工具自带的安装器（如 `camoufox fetch`）**只用 `api.github.com` 查版本**（匿名限额 60 次/小时/IP）。
一旦被限流 → 403 → 装不上，**但它的"查版本"以外每一步都能手工复现**。

## 通用五步

**① 从项目自己的配置里拿命名规则（不要猜文件名）**
```bash
grep -rn "releases/download\|{version}\|pattern:" <包目录>/*.yml <包目录>/*.py
# 实例：camoufox 的 repos.yml → pattern: "{name}-{version}-{build}-{os}.{arch}.zip"
```

**② 先 HEAD 验证再下载**（拿不到 content-length 就别开始下）
```bash
curl -sIL -m 25 "$U" | grep -iE "^(HTTP/|content-length)"
```
⚠️ **体积别信二手描述**：本次调研写"300-400MB"，**实际 1.31 GB，差 3 倍**。
大文件用 `aria2c -x8 -s8 --continue=true`（见 `aria2-downloads`）。

**③ 问出确切的目标路径 —— 别自己拼**
多数安装器**先 `mkdir` 再下载**，所以跑几秒掐掉就能看到它要哪个目录：
```bash
timeout 10 <installer> 2>&1 | tail -3 ; find <INSTALL_DIR> -maxdepth 3
```

**④ 找"标志文件"，缺了会被全删**（**最容易漏、最致命**）
```bash
grep -rn "rmtree\|_FLAG\|INSTALL_DIR" <包目录>
```
Camoufox 实例：`COMPAT_FLAG`（`.0.5_FLAG`）不存在时，目录非空即被判为"旧版不兼容数据" →
`shutil.rmtree` **整个删光重下**。**手装完必须建这个空文件。**（吃过一次：装好又消失）

**⑤ 校验和必须对上**
自己算下到的文件 sha256，与 `repo_cache.json` 里该版本的真值**逐字符比对**；
一致才证明镜像拿到的就是官方同一个文件，手装才可信。

## 收尾

- 手装完成后**回查目录还在**（有些命令带 `download_if_missing=True`，会把你的安装当"缺失"再删一次）
- 装完按六步链条回流：**技能 → 路由 → 总控台 → 同步**
