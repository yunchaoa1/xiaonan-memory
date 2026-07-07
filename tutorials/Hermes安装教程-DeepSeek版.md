# Hermes 桌面版安装教程

> 适用：Windows 10/11 · 大脑：DeepSeek V4 Pro · 版本：2026年7月最新版
> 目标读者：从未接触过 AI Agent 的纯新手

---

## 第一步：注册 DeepSeek 获取 API Key

**1.1 打开浏览器，访问：**
```
https://platform.deepseek.com
```

**1.2 点击右上角「注册」**
- 输入手机号或邮箱
- 获取验证码并填写
- 设置密码（记住：你以后充值和管理 API 都要用到）

**1.3 登录后进入控制台**
- 左侧菜单栏点击「API Keys」
- 页面中间有一个「创建 API Key」按钮，点击

**1.4 创建 Key**
- 弹窗会让你给 Key 起个名字，随便填，比如 `hermes-desktop`
- 点击「创建」
- ⚠️ 此时屏幕会显示一串以 `sk-` 开头的字符，例如 `sk-MDBxxxxxxxxxxxxxxxxNcyq`
- **立刻复制保存到记事本！关掉弹窗后就再也看不到了！**

**1.5 充值（DeepSeek 是预付费的）**
- 左侧菜单点击「充值」
- 首次建议充 20-50 元就够了，够你用很久
- 支持微信/支付宝

---

## 第二步：下载安装 Hermes 桌面版

**2.1 打开浏览器，访问 Hermes 官网：**
```
https://hermes-agent.nousresearch.com
```

**2.2 点击首页的「Download」或「Get Started」按钮**
- 选择 Windows 版本
- 下载 `.exe` 安装文件（约 200-300MB）

**2.3 安装**
- 双击下载的 `.exe` 文件
- 安装路径建议选择 `D:\Hermes`（方便管理）
- 一路点「下一步」直到完成
- 桌面上会出现 Hermes 图标

**2.4 首次启动**
- 双击桌面 Hermes 图标
- 软件会自动在安装目录下生成一个 `config.yaml` 配置文件
- 第一次打开可能会有一个欢迎界面，先关掉

---

## 第三步：配置模型（最关键的一步）

**3.1 找到配置文件**
- 打开文件资源管理器
- 进入安装目录，默认是 `D:\Hermes`
- 找到 `config.yaml` 文件
- 右键 →「打开方式」→ 选择「记事本」

**3.2 修改配置**

把记事本里的内容**全部删掉**，粘贴以下内容：

```yaml
model:
  default: deepseek-chat
  provider: custom
  base_url: https://api.deepseek.com/v1

providers:
  custom:
    api_key: 把你第一步复制的Key粘贴到这里，注意保留引号
    api_base: https://api.deepseek.com/v1

auxiliary:
  vision:
    provider: custom
    model: deepseek-chat
    api_key: 和上面一样的Key，再粘贴一次

terminal:
  backend: local
  cwd: .
  timeout: 180

browser:
  inactivity_timeout: 120

agent:
  max_turns: 60
  verbose: false
```

⚠️ 注意：`api_key` 后面那串字符**必须带引号**，像这样：`api_key: "sk-xxxxx"`

**3.3 保存**
- 文件 → 保存（Ctrl+S）
- 关闭记事本

---

## 第四步：启动验证

**4.1 启动 Hermes**
- 双击桌面 Hermes 图标
- 等待加载完成（约10-20秒）

**4.2 测试对话**
- 在聊天框输入：`你好，你是谁？`
- 如果能收到回复，说明 DeepSeek 连接成功 ✅

**4.3 测试视觉模型（重要！）**
- 准备一张图片（随便什么图，比如桌面的截图）
- 把图片拖进 Hermes 的聊天框
- 输入：`描述一下这张图片里有什么`
- 如果能准确描述图片内容，说明视觉模型也配置成功 ✅

---

## 第五步：日常使用

**5.1 读文件**
- 把任何文件拖进聊天框，Hermes 会自己读
- 或者直接说「帮我读一下 D:\某个文件.txt」

**5.2 写文件**
- 直接说「帮我写一个 xxx.md 放在 D:\xxx 目录下」
- Hermes 会自动创建文件和目录

**5.3 上网搜索**
- 直接说「帮我搜一下 xxx」
- Hermes 会用内置浏览器搜索

**5.4 记忆系统**
- Hermes 会自动记住你说过的重要信息
- 比如「我叫张三，喜欢简洁回复」
- 下次新会话它也会记住

---

## 常见问题

| 问题 | 解决方法 |
|------|------|
| 启动后没反应 | 检查 `config.yaml` 里 `api_key` 有没有正确填写，Key 有没有过期 |
| 回复很慢 | 正常，DeepSeek 有时会比较慢，给点耐心 |
| 拖图片进去没反应 | 检查 `auxiliary.vision` 段是否配置正确，model 必须是 `deepseek-chat` |
| 报错 `401 Unauthorized` | API Key 填错了或过期了，去 DeepSeek 平台重新建一个 |
| 想换模型 | 把 `default` 换成 `deepseek-reasoner`（推理增强版） |

---

> 搞不定的话把报错截图发给凡哥，他帮你转给我。🦐
