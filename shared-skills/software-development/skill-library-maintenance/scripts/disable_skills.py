# -*- coding: utf-8 -*-
"""批量停用技能：向 D:\\Hermes\\config.yaml 的 skills.disabled 追加技能名。

用法：编辑下方 TO_DISABLE 列表后运行。
注意：patch 工具会拒绝修改 Hermes 配置文件，必须用脚本直接改。
"""
path = r"D:\Hermes\config.yaml"

TO_DISABLE = [
    # "example-skill-a",
    # "example-skill-b",
]

with open(path, encoding="utf-8") as f:
    text = f.read()

added = 0
for name in TO_DISABLE:
    line = f"    - {name}\n"
    if line not in text:
        # 插到 disabled: 块末尾（找最后一个 "    - " 行）
        lines = text.split("\n")
        last_idx = None
        for i, l in enumerate(lines):
            if l.startswith("    - "):
                last_idx = i
        if last_idx is None:
            raise SystemExit("未找到 skills.disabled 块")
        lines.insert(last_idx + 1, line.rstrip("\n"))
        text = "\n".join(lines)
        added += 1

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)

print(f"added {added} skills to disabled, total - entries: {text.count('    - ')}")
