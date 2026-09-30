# DeepSeek 开放平台 · 已核事实库

> 核实日期 2026-09-30。来源均为官方页面（api-docs.deepseek.com / platform.deepseek.com FAQ）。
> ⚠️ 平台的模型名、价格、限制会变 —— 用之前先按下面的"复核方法"再核一遍。

## 复核方法（比读本文件更可靠）

```bash
# 1) 官方文档站全部页面（页面少，一次就能核完）
curl -s https://api-docs.deepseek.com/sitemap.xml | grep -o '<loc>[^<]*</loc>' | sed 's/<[^>]*>//g'
```

重点页：
- `/zh-cn/` 首次调用 API（base_url / key / 模型名）
- `/zh-cn/quick_start/pricing` 模型与价格
- `/zh-cn/quick_start/rate_limit` 限速与隔离
- `/zh-cn/faq` 企业认证 / 充值 / 对公汇款 / 发票
- `/zh-cn/quick_start/agent_integrations/<tool>` Agent 工具接入（claude_code / codex / opencode / hermes / openclaw / qoder / reasonix / workbuddy）

> 第三方镜像站（如 apifox 镜像）内容可能滞后，**与 api-docs 正式页冲突时以 api-docs 为准**。

## 一、接入基础

| 项 | 值 |
|---|---|
| base_url（OpenAI 格式） | `https://api.deepseek.com` |
| base_url（Anthropic 格式） | `https://api.deepseek.com/anthropic` |
| 模型名 | `deepseek-flash`（旧名 `deepseek-v4-flash` 等仍可调，已下线并按 Flash 计费）、`deepseek-v4-pro` |
| 上下文 | 1M；输出最大 384K |
| 官方对接邮箱 | `api-service@deepseek.com` |

接口兼容 OpenAI / Anthropic SDK，也就是**任何能自定义 base_url 的工具都能被网关接管**。

## 二、并发与隔离（★ 企业方案的关键约束）

- **并发限制按账号计，与 API Key 无关**（原文）。默认：`deepseek-flash` 2500 / `deepseek-v4-pro` 500。
  → 推论：**给每人发一个 key 在官方侧分不出人、也限不住人。**
- 一个请求从发出到响应完成记为一个并发；超限返回 **HTTP 429**。
- 更高的并发需求 → 提交**账号扩容申请工单**，官方按实际业务需求匹配，**扩容不额外收费**。
  工单（飞书表单，官方限速页给的原链）：
  `https://trtgsjkv6r.feishu.cn/share/base/form/shrcnda9jNKvhyYr8xb843xLEzc`
- `user_id` 参数（同一账号下区分业务侧用户）提供三层隔离：**内容安全隔离 / KVCache 隔离（隐私）/ 调度隔离**；
  扩容后还会**按 user_id 单独限流**（每个 user_id 仍是 flash 2500 / pro 500）。
  格式 `[a-zA-Z0-9\-_]+`，≤512 字符，**不要塞隐私信息**。
  ⚠️ Agent 工具不会自动带这个参数 → 在 Agent 场景基本用不上，按人统计得靠网关。
- ⚠️ **口径冲突**：官方限速页说可提工单扩容；旧 FAQ 镜像页写"目前暂不支持针对单个账号提高并发上限"。
  **以 api-docs 限速页为准**，实操前再核一次。

## 三、官方没有的能力（已核 sitemap 全站 44 页）

- ❌ 团队 / 子账号 / 成员管理
- ❌ 按 API Key 查看用量
- ❌ 企业专属实例、专线、VPC 私连
- ❌ SLA 协议、合同价、专属技术支持通道的说明
- ❌ 私有化部署文档

→ 结论：**"按人统计"只能自建（网关这一层）**，别指望官方后台。

## 四、账号与财务

| 项 | 规则 |
|---|---|
| 认证类型 | 个人实名 / 企业实名。官方原文：**两者在权益和产品功能上目前没有区别**，差别在认证材料 |
| 企业实名 | ⚠️ **不可逆** —— "不可变更为个人认证或其他企业"。个人号不要直接改；确认主体，必要时**新注册** |
| 邮箱 | 部分邮箱域名被拒（提示"暂不支持该邮箱域名注册"）→ 换 QQ/163/Gmail 等 |
| 在线充值 | 实名后可用支付宝/微信，账单页看结果 |
| **对公汇款** | **仅企业用户**；企业实名后可获取**专属汇款账号**；⚠️ **汇款方开户名称必须与开放平台实名认证名称一致**；到账 10 分钟–1 小时自动入账 |
| 余额 | **充值余额不会过期**；赠送余额有有效期（账单页看） |
| 发票 | 账单页 `https://platform.deepseek.com/transactions` → 发票管理；**抬头须与实名认证信息一致**；周期约 7 个工作日 |

## 五、价格（截至 2026-09，¥ / 百万 tokens）

| | deepseek-flash | deepseek-v4-pro |
|---|---|---|
| 输入（缓存命中）空闲 / 高峰 | 0.02 / 0.04 | 0.15 / 0.30 |
| 输入（缓存未命中）空闲 / 高峰 | 1 / 2 | 4.5 / 9.0 |
| 输出 空闲 / 高峰 | 4 / 8 | 13.5 / 27.0 |
| 并发 | 2500 | 500 |

- **空闲时段 = 高峰价的 1/2**。高峰时段：北京时间**周一至周五 9:00–12:00、14:00–18:00**（不含法定节假日）；
  其余（含周末与节假日全天）为空闲。
- → 治理动作：把批量/离线任务**挪到空闲时段**，同样的活成本直接砍半。这是网关看板能直接看出来的事。
- 备注：官方曾公告 V4 Pro 有序下线、请求路由到 V4.1 Flash（以 pricing 页脚注为准，会变）。

## 六、给团队用的迁移口径

成员侧只需改两处：**base_url 指向网关** + **key 换成网关发的虚拟 key**。
模型名沿用 `deepseek-flash` / `deepseek-v4-pro`；请求体不用改（OpenAI 兼容）。
