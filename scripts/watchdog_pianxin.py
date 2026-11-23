# -*- coding: utf-8 -*-
"""看门狗：检查跑片进度，脚本死了就重启，全完成就报一声。
输出空 = 一切正常不打扰；有输出 = 需要人看。
"""
import io, json, os, subprocess, sys, time

import psutil

STATE = r"D:/Hermes/cache/emotion/run_state.json"
SCRIPT = r"D:/Hermes/cache/emotion/run_all_cg.py"
PY = r"D:/Hermes/hermes-agent/venv/Scripts/python.exe"
LOCK = r"D:/Hermes/cache/emotion/run_all.lock"
DONE_FLAG = r"D:/Hermes/cache/emotion/all_done.flag"


def runner_pids():
    """在跑的 run_all_cg 实例（不含本进程）。
    小南 2026-11-23 改：旧版用 wmic 查命令行，本机 Win11 已无 wmic → 永远返回空
    → 每 tick 都判「进程不在了」→ 无限重启，当晚堆到 21 个实例、RAM 只剩 1.7GB。"""
    me = os.getpid()
    pids = []
    for p in psutil.process_iter(["pid", "cmdline"]):
        try:
            if p.info["pid"] == me:
                continue
            if "run_all_cg" in " ".join(p.info.get("cmdline") or []):
                pids.append(p.info["pid"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return pids


def running():
    return bool(runner_pids())


def live_lock_holder():
    """锁文件记的 PID 且确实活着 → 返回 PID；否则 None"""
    if not os.path.exists(LOCK):
        return None
    try:
        raw = io.open(LOCK, encoding="utf-8").read().strip()
        pid = int("".join(ch for ch in raw.split("PID=")[-1] if ch.isdigit()))
    except Exception:
        return None
    return pid if pid in runner_pids() else None


def state():
    if os.path.exists(STATE):
        try:
            return json.load(io.open(STATE, encoding="utf-8"))
        except Exception:
            pass
    return {"done": [], "failed": []}


def main():
    s = state()
    done = sorted(s.get("done", []))
    failed = s.get("failed", [])

    # 全跑完
    if len(done) >= 20:
        if not os.path.exists(DONE_FLAG):
            io.open(DONE_FLAG, "w").write(time.strftime("%Y-%m-%d %H:%M:%S"))
            print(f"《偏心》20 段全部跑完 ✅\n成功 {len(done)} 段，失败 {failed or '无'}\n输出目录：D:/SDkecheng/ComfyUI/output/（文件名 G01~G20 开头）")
        return

    # 有实例在跑 / 锁还活 → 不打扰、不再起新的（旧版缺的就是这道闸）
    if runner_pids() or live_lock_holder():
        return

    # 真没人跑 → 清掉陈旧锁，起一个（必须脱离父进程：不经 cmd.exe、自带句柄）
    if os.path.exists(LOCK):
        try:
            os.remove(LOCK)
        except Exception:
            pass
    _env = {k: v for k, v in os.environ.items()
            if k.upper() not in ("PYTHONPATH", "PYTHONHOME")}
    _logf = io.open(r"D:/Hermes/cache/run_daemon.log", "a", encoding="utf-8", errors="replace")
    subprocess.Popen([PY, "run_all_cg.py"], cwd=r"D:/Hermes/cache/emotion",
                     stdout=_logf, stderr=subprocess.STDOUT, env=_env, close_fds=True,
                     creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP)
    print(f"跑片守护进程不在了，已重启一个实例。当前进度 {len(done)}/20，失败 {failed or '无'}")
    return
    # 正常运行 → 不说话


if __name__ == "__main__":
    main()
