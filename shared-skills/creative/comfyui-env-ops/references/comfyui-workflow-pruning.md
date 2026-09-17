# ComfyUI 瘦身：把整套装成「只跑一个工作流」（2026-09-15 本机实测）

## 何时用
凡哥说「**本机只跑这一个工作流了**，除了它用到的都删掉」「保留 Manager，其余插件包全删」这类指令时。

## 顺序铁律：先算清 → 停用 → 重启复验 → 才删除

删插件包是**不可逆方向**的操作，而**漏留一个包 = 工作流节点缺失、直接跑不动**。三步走，不许跳：

1. 用工作流的节点类型反查所需包，得出**保留清单**
2. 其余包**改名加 `.disabled`**（先不删）→ 重启 → 双重复验
3. 复验通过后才 `rm -rf`。模型侧可跳过第 2 步（模型不参与导入，缺了只在执行期报错）

## 官方停用机制：目录名加 `.disabled`

`nodes.py` 里：`if module_path.endswith(".disabled"): continue` —— **改名即停用，秒级可还原**，比移动到 `_disabled_plugins/` 更贴官方、且不破坏原路径。`__pycache__` 不用管。

```bash
for d in $(ls <ComfyUI>/custom_nodes); do
  case " $KEEP " in *" $d "*) echo "保留 $d";; *) mv "<ComfyUI>/custom_nodes/$d" "<ComfyUI>/custom_nodes/$d.disabled";; esac
done
```

## 算「工作流需要哪些包」

1. 抽工作流**全部**节点 type（含子图 `definitions.subgraphs[].nodes`）
2. 每个 type 去 `custom_nodes/*/**/*.py` 找提供者（搜类名字面量）
3. 找不到的 → 查 `comfy_extras/` 与根目录（官方核心，不用管）

⚠️ **两条反向陷阱（本次都踩到，任一都会导致删错包）**：

- **动态注册的包 grep 不到**：`Any Switch (rgthree)` 不在 rgthree 的任何 `.py` 字面量里（名字动态拼接）→ 全仓 grep 0 命中 → 会被误判成「不需要」而删掉 rgthree。
- **前端 JS 节点永远不在服务端列表**：`Fast Bypasser (rgthree)` / `Fast Groups Bypasser (rgthree)` 只在 `src_web/**/*.ts` 注册 → `/object_info` 里没有 → 又会被误判成「缺件」。

**结论：`grep 源码` 与 `/object_info 差集` 各漏一半，两个都要跑；任一侧可疑就按「宁可留着」处理，并把该包点名写进报告让凡哥确认。** `rgthree-comfy` 本次正是靠这条保下来的（凡哥打开工作流时那几个开关要能正常显示）。

## 复验（两步都过才算成功）

```bash
cd <ComfyUI> && ./.venv/Scripts/python.exe main.py --quick-test-for-ci > ci.log 2>&1
grep -c "IMPORT FAILED" ci.log          # 期望 0
# 重启实例（带云端同款启动参数）后：
curl -s http://127.0.0.1:<端口>/object_info -o oi_after.json
python scripts/audit_workflow_missing_nodes.py <工作流>.json
```

判读：**注册节点总数大幅下降属正常**（本次 3211 → 1904，瘦 1307 类）；只看两个数字 —— **「工作流节点 0 缺」+「模型 0 缺」**。

## 模型侧：删之前必须重扫一遍（本节最值钱）

扫工作流的模型引用，**必须同时扫 `widgets_values_named`（按名）与 `widgets_values`（按位），且不能只挑「加载器类节点」** —— 模型名会出现在**任意节点的 optional 输入**里。

**实例（本次真踩）**：`taeh3.safetensors`（TAE 轻量预览解码器，**9,791,388 字节**，HF `GuangyuanSD/minimax_h3_video_vae_int8_convrot` → `models/vae_approx/`）是 `ModelPreviewOverrideKJ` 的**可选输入** `tiny_vae`（KJNodes 1.4.9；tooltip 原文 *"Tiny VAE decoder from models/vae_approx for true-RGB previews"*）。
- 工作流里那一格填的是 `taeh3.safetensors` 而**不是 `none`** → **属必需**；缺了采样中途预览走不通
- 但「只扫 loader 类节点」的脚本查不到它 → 我给出了「10 处引用全就位」的**错误结论**，被凡哥自己发现并反问

**纪律**：判「必需 / 可选」的依据是**工作流里那一格的实际取值**，不是节点类别；值等于 `none` / 空 才是真可选。验收口径写成 `引用 N 个模型 / 缺 0 个`。

## 目录名对齐 vs 删除的相互坑

- 用 `ln`（**硬链接**）给模型造别名目录（如 `MiniMax-H3/`）后，**同一真身有 2 个路径**（`stat -c%h` = 2）→ 删除时**两个路径都要删**，否则文件根本不消失（本次 hybrid 模型即 2 链接）。
- 报磁盘收益按 `df` 实测值说，**别把硬链接重复计数**（本次预估 89.8 GiB、实释 ~70 GB）。

## 收尾：删除件必须留回源信息

每个删掉的模型/包都把**回源信息**（HF 仓库 + 精确字节，或 GitHub repo）写进 DASHBOARD —— 恢复 = 一条下载/克隆命令。本次删的 4 个主模型：
`hybrid_fl2va_ref2va_b25-49-int8` → `smhfacct/Minimax-H3-fl2va-ref2va-hybrid-models`｜`fl2va_pruned_w4a8_mixed` → `Kijai/MiniMax-H3-experimental`｜两个 `*_pruned_int8_convrot` → `Comfy-Org/MiniMax-H3`。

## 与其他节的衔接

- 换主模型（如融合版 → Singularity）= **改工作流加载器取值**，按 SKILL.md「破坏性收尾与回答口径 ②」先点矛盾再动手
- 瘦身完把新工作流副本放进 `user/default/workflows/`，原件保留不动
