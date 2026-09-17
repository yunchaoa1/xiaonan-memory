# 云电脑(智算云扉 waas) H3 ComfyUI 干净环境重建案例 2026-09-09

完整闭环：旧定制镜像(ComfyUI_v0.30.1-支持MiniMax H3) 有低频杂音 → 凡哥拍板弃旧镜像 → 在基础 pytorch 镜像从 0 复刻本地验证组合 → **8s 一采音频干净，凡哥亲验通过 ✓**。

## 凡哥决策（防再走弯路）
「我只相信我们之前验证过的东西，不想走新的路线……系统不同，电脑从本地换成了云电脑……把之前解决的那套方案直接放在云电脑上，唯一不一样就是 linux 系统。」→ 结论：**1:1 复刻本地验证组合，只换 OS**，不做任何"改进"。

## 平台事实（智算云扉 waas.aigate.cc = AI Cote，docs.aigate.cc）
- `/home/waas` = 独立持久数据盘（重启/换镜像都保留）——**环境、venv、ComfyUI 全放这里**
- `/root`、`/etc` = 系统盘镜像层；实例重启保留可写层，但**平台 entrypoint 每次开机用模板覆盖 `/etc/waas-script/process-compose.yml`**（文件时间戳回到镜像制作日）→ 改它做开机自启会被还原（实测失败，勿再试）
- 开机链：PID1 = `docker-init -- bash -c … wget file-server entrypoint.sh | bash & … sleep infinity` → entrypoint（平台动态下发）→ `process-compose --no-server --tui=false up -f /etc/waas-script/process-compose.yml`（SSH/JupyterLab/VSCode/WebOS 都是它的子进程）
- 官方开机自启机制 = 《容器启动项目指南》(docs.aigate.cc/bestPractice/containerStartupProjectGuide)：start.sh 放 `/etc/waas-script` + 改入口命令 + **保存镜像** + 提客服（脚本名/镜像名/保存时间），客服改完"容器创建时自动执行"
- `/etc/waas-script/start.sh` 钩子（旧镜像有此文件被直接执行；新镜像 entrypoint 是否也执行它 = **待验证实验**，2026-09-09 已创建测试脚本未回验）
- 生图/推理模型也能用共享 `/datasets`（waas 公模库，只读），但 H3 模型直接复用旧数据 `/home/waas/ComfyUI/models`

## 铁律（凡哥 2026-09-09 纠正："别瞎猜"）
**云平台/托管环境机制先查平台官方文档再动手**（docs.aigate.cc），不要拿通用 ComfyUI/Linux 经验脑补平台行为——平台模板覆盖、自启机制、数据盘语义都只有文档+实测说了算。参考图/工作流/UI 类问题同样先核官方 skill/文档再答复。

## 环境搭建完整命令链（已验证成功）
前提：新实例框架选 **pytorch 2.8.0 + CUDA 12.8 + Python 3.12 + ubuntu2204**（RTX 5090 Blackwell 需 cu128），开放 HTTP 8188，按时计费。

```bash
# 1. clone ComfyUI v0.30.0（分离头 b1693ecb）
mkdir -p /home/waas/h3-0300 && cd /home/waas/h3-0300
git clone --depth 1 --branch v0.30.0 https://github.com/Comfy-Org/ComfyUI.git ComfyUI

# 2. venv 复用预装 torch（--system-site-packages 继承 /root/miniconda3 的 cu128 全家）
/root/miniconda3/bin/python -m venv --system-site-packages /home/waas/h3-0300/venv
/home/waas/h3-0300/venv/bin/pip install --upgrade pip
/home/waas/h3-0300/venv/bin/pip install -r /home/waas/h3-0300/ComfyUI/requirements.txt

# 3. 5 插件锁本地验证版
cd /home/waas/h3-0300/ComfyUI/custom_nodes
git clone https://github.com/HELPMEEADICE/TE-Speed-MiniMaxH3-OSS.git && git -C TE-Speed-MiniMaxH3-OSS checkout c1dacf4
git clone https://github.com/kijai/ComfyUI-SolAttn_triton.git && git -C ComfyUI-SolAttn_triton checkout 0e334dc
git clone https://github.com/AIMixer/ComfyUI_MiniMaxH3_Director.git && git -C ComfyUI_MiniMaxH3_Director checkout a148812
git clone https://github.com/shuaixn/ComfyUI-MiniMaxH3DualClockSampler.git && git -C ComfyUI-MiniMaxH3DualClockSampler checkout 986f8e9
git clone https://github.com/kijai/ComfyUI-KJNodes.git

# 4. 插件依赖（kjnodes/director 有 requirements.txt；triton 3.4.0 已在 base 继承，无需装）
cd /home/waas/h3-0300/ComfyUI/custom_nodes && for d in */; do if [ -f "$d/requirements.txt" ]; then echo "=== $d ==="; /home/waas/h3-0300/venv/bin/pip install -r "$d/requirements.txt"; fi; done

# 5. 模型软链到共享盘（关键：先删 ComfyUI 自建空目录，否则 ln -s 静默失败）
rm -rf /home/waas/h3-0300/ComfyUI/models /home/waas/h3-0300/ComfyUI/output
ln -s /home/waas/ComfyUI/models /home/waas/h3-0300/ComfyUI/models
ln -s /home/waas/ComfyUI/output /home/waas/h3-0300/ComfyUI/output
# 验证：ls -la 要显示 models -> /home/waas/ComfyUI/models（带箭头）

# 6. 启动（前台测一次看日志，再转 nohup）
cd /home/waas/h3-0300/ComfyUI && unset PYTHONPATH && nohup /home/waas/h3-0300/venv/bin/python main.py --port 8188 --listen 0.0.0.0 --disable-auto-launch > /home/waas/h3-0300/comfyui.log 2>&1 &
```
日志健康标志：5 插件 Import times 全列出、`MiniMax H3 Director HTTP routes registered`、`To see the GUI go to: http://0.0.0.0:8188`。

## 坑清单（每坑都实踩过）
1. **torchaudio 陷阱**：requirements.txt 无版本限制 → 装到最新 2.11.0（cu13 编译）→ 启动崩 `OSError: libcudart.so.13: cannot open shared object file`。修：`pip uninstall -y torchaudio` 后装配套 cu128 版：
   `/home/waas/h3-0300/venv/bin/pip install torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu128`
2. **models 软链被空目录挡**：ComfyUI 首启自建空 models/（内含 put_xxx_here 占位），此时 `ln -s` 静默失败（2>/dev/null 吞错），模型库空空如也。必须先 `rm -rf` 再 `ln -s`，并用 `ls -la` 看箭头验证。
3. **工作流不出现在浏览器面板**：example_workflows 在插件目录，浏览器只扫 `ComfyUI/user/default/workflows/` → 复制过去：
   `cp <插件>/example_workflows/minimax_h3_director_r2v.json /home/waas/h3-0300/ComfyUI/user/default/workflows/`
4. **开机不自启**：手动 nohup 的进程平台不托管。进程级方案：改 process-compose.yml（被模板还原，废）；官方正路=客服"容器启动项目"（保存镜像+工单）。

## 测试判据（对齐主 SKILL 频谱法）
8s 一采 r2v（前 3.5s 无台词 + 台词 + 收尾），无台词段低频安静、人声清晰 = 通过。一次只变一个变量。
