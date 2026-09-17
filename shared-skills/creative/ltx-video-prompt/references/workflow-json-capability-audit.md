# LTX工作流JSON能力核查

## 目的

工作流文件名、教程标题和README可能写“全能参考”“导演”“合流”，不能据此判断节点是否真实存在。结论必须来自JSON节点类型与连线。

## 核查方法

1. 解析工作流JSON的 `nodes` 与 `links`。
2. 列出节点 `type`、`title`、`widgets_values`。
3. MSR路线至少应见到：`LiconMSR`、`LTXICLoRALoaderModelOnly`、`LTXAddVideoICLoRAGuide` 或对应MSR LoRA文件。
4. 导演台路线至少应见到：`LTXDirector`、`LTXDirectorGuide`、`LTXDirectorCropGuides`。
5. 自定义音频路线检查：`LTXVAudioVAEEncode/Decode`、音频加载、AV latent合并/分离。
6. 声称MSR＋导演台合流时，同一份JSON必须同时出现MSR与Director两组节点，并检查两组是否实际连入采样链；只在文件名中同时出现不算。
7. 记录节点数、连线数、模型文件、LoRA版本、输入参考节点、音频路径和输出节点。
8. 对全部工作流目录做扫描，统计MSR-only、Director-only、Both，避免只检查一个文件。

## 判断模板

- 已验证MSR：是/否；证据节点：
- 已验证Director：是/否；证据节点：
- 已验证自定义音频：是/否；证据节点：
- 已验证合流：是/否；同一JSON中的两组节点与连线路径：
- 模型与LoRA：
- 分辨率/帧数/音频长度：
- 结论：可直接测试／需补节点／仅文件名声称／无法读取。

## 易错点

- “MSR＋V2全能参考＋自定义音频”不等于“MSR＋导演台”。
- 工作流里有孤立节点不等于能力已接通；需要核对links。
- 热修复版和原版可能节点ID不同，应按type而非ID判断。
- 重复安装的custom_nodes可能产生多份同名示例，先按内容哈希或绝对路径去重。
- 本机暂未安装某模型只能记为当前资源状态，不能写成工具永久不支持。
