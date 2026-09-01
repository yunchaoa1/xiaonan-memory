# 05 MiniMax H3 三镜提示词测试包

本目录把 `03_storyboard_timeline/opc_shots.json` 的三镜编译成 H3 提示词与素材绑定契约。它用于测试节点交接，不代表视频已经生成。

## 状态

- Package：`NOT_RUN`
- 每镜运行：`NOT_RUN`
- 素材绑定：`ASSET_BINDING_PENDING`
- 模型ID：`RUNTIME_UNVERIFIED`
- 视频输出：无

## 方言边界

目标族为 MiniMax H3，结构同时声明 cloud API、ComfyUI Partner、Native Nodes 与 AIMixer Director；本样本选择 `aimixer_director` 作为待执行方言。业务层使用稳定 asset ID，执行适配器才允许把它映射为 Director 的引用槽位，不能让 `<Picture N>` 顺序成为状态真源。

## 放行条件

角色、场景、道具必须各自存在唯一锁版记录；运行时模型和后端必须核验；提交后必须验证媒体可解码、时长、分辨率、fps、音轨、黑帧/静帧、音画同步与人工镜头QC。
