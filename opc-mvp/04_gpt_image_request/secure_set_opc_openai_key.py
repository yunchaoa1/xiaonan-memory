from __future__ import annotations

import getpass
from pathlib import Path

ENV_PATH = Path(r"D:\Hermes\.env")
KEY_NAME = "OPC_OPENAI_API_KEY"

secret = getpass.getpass("请粘贴 OpenAI 官方 API Key（输入不回显），然后按 Enter：")
if not secret.strip():
    raise SystemExit("未输入密钥，配置未改动。")
if "\n" in secret or "\r" in secret:
    raise SystemExit("密钥包含非法换行，配置未改动。")

text = ENV_PATH.read_text(encoding="utf-8") if ENV_PATH.exists() else ""
lines = text.splitlines()
out = []
replaced = False
for line in lines:
    if line.startswith(KEY_NAME + "="):
        if not replaced:
            out.append(f"{KEY_NAME}={secret}")
            replaced = True
    else:
        out.append(line)
if not replaced:
    out.append(f"{KEY_NAME}={secret}")
ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
ENV_PATH.write_text("\n".join(out).rstrip("\n") + "\n", encoding="utf-8")
print("OPC_OPENAI_API_KEY 已安全写入 D:\\Hermes\\.env（密钥未显示）。")
