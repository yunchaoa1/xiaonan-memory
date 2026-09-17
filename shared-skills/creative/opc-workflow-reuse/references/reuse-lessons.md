# OPC复用与效率教训

## 用户标准

用户希望OPC Skill工作首先可测试，避免把Skill任务扩大成平台工程。已验证的创作规则和回归成果必须保留；未完成能力优先借成熟产品/开源项目的最小机制，再用OPC规则补齐。

## 推荐流程

1. 先锁定当前交付物和截止时间。
2. 盘点现有文件与真实证据，不按代理摘要判定完成。
3. 对每项能力分类：KEEP、BORROW、ADAPT、DEFER、REJECT。
4. 只侦察缺失能力，不寻找万能替代品。
5. 对候选核验许可证、维护状态、可运行证据和具体可移植模块。
6. 只创建一个小候选Skill，先不覆盖原版。
7. 独立对照原版，确认没有删掉已验证硬规则。
8. 通过后再替换正式Skill并运行健康检查。
9. 使用固定样例做最小联调，分别报告结构、模型运行、媒体QC和商业发布状态。

## 已验证的组合方向

- 写作：Show Me The Story的自动闭环思路＋Novel OS的StoryState/确定性连续性。
- 剧本解析：Fountain与screenplay-tools。
- 资产分类：ScriptBreak/OSF的production分类，保留OPC自己的identity/state/transition。
- 分镜：OpenTimelineIO时间数学与交换结构，Kitsu关系只作概念参考。
- GPT Image：OpenAI官方调用与Character Anchor思路；原生横屏3840x2160已实测。
- H3：官方模板和AIMixer Director的方言/分组边界；真实视频需单独验证。

## 纠偏

前期曾把成熟方案研究扩大成解析器、时间线、资产注册、Runner、状态机和API工程，导致效率低。以后这些默认DEFER，只有当前Skill确实需要且已有失败证据时才新增。

## 验收边界

固定文件存在、JSON/OTIO可解析、字段齐全，不等于模型生成成功。原生4K必须回读模型实际像素，插值放大不算原生4K。视频未运行就保持NOT_RUN，不写成PASS。

代理返回completed不是证据。遇到503/524/超时，逐文件核验并把缺失任务缩小到一个文件或一至三镜。
