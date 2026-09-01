# GPT Image 静态请求包（MODEL_BLOCKED）

本目录只落地一个**静态、未执行**的 GPT Image 请求包。主体为静态 eligible fixture：

- `asset_id`: `scene.village-old-locust-tree.v0.1`
- `asset_type`: `scene`
- 主体：村口老槐树场景主体
- eligibility：`eligible`（仅指静态 fixture 的请求编译资格，不代表已通过真实生成/QC/锁定）

## 官方请求边界

- HTTP method：`POST`
- 官方 endpoint：`https://api.openai.com/v1/images/generations`
- endpoint mode：`images.generations`
- `runtime_model_id`：当前为 `null`，状态为 `PENDING_CONTROLLED_AUTHORIZATION`

不会根据产品展示名、聊天文本或经验猜测/硬编码模型 ID。只有从受控运行时配置取得并经授权的实际 `runtime_model_id`，才能在执行前写入并按对应官方 schema 校验参数。

## 当前阻塞

状态：`MODEL_BLOCKED`

1. 缺少官方 OpenAI API key；
2. 未确认并授权 API 计费；
3. 未确认当前账户/项目的 GPT Image API 权限；
4. 受控 `runtime_model_id` 尚未授权。

因此本次：

- **未调用任何付费 API**；
- **未修改配置**；
- **未发送网络生成请求**；
- **未生成图片**；
- 无 request ID、输出文件、图片哈希或 usage 可记录。

## 文件

- `request_manifest.json`：静态请求意图、官方 endpoint、待授权 runtime model 字段与 preflight 状态。
- `blocked_result.json`：类型化 `MODEL_BLOCKED` 结果及解锁条件。
- `README.md`：边界与状态说明。

只有在 API key、计费、权限及受控 `runtime_model_id` 全部由授权方确认后，才可另行执行真实请求。执行后还必须记录实际模型 ID、request ID、返回元数据、图片字节校验、SHA-256 与 QC 结果；本静态包不声称具备这些产物。
