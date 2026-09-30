#!/usr/bin/env bash
# 多人 LLM 网关 · 一键部署（在云服务器上以 root 执行）
# 用法：把 docker-compose.yml 和本脚本放同一目录，然后  bash bootstrap.sh
#
# 做四件事：① 装 Docker ② 生成随机密码写回 compose ③ 拉起容器 ④ 等就绪并打印访问信息
set -euo pipefail

cd "$(dirname "$0")"
COMPOSE_FILE="docker-compose.yml"

echo "=========================================="
echo " 多人 LLM 网关 · 一键部署"
echo "=========================================="

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "❌ 找不到 $COMPOSE_FILE，请与本脚本放在同一目录"; exit 1
fi

# ---------- ① Docker ----------
if ! command -v docker >/dev/null 2>&1; then
  echo "[1/4] 安装 Docker ..."
  curl -fsSL https://get.docker.com | sh
  systemctl enable --now docker
else
  echo "[1/4] Docker 已安装，跳过"
fi

# docker compose（v2 插件）
if ! docker compose version >/dev/null 2>&1; then
  echo "      安装 docker compose 插件 ..."
  apt-get update -qq && apt-get install -y -qq docker-compose-plugin || true
fi

# ---------- ② 随机密码 ----------
echo "[2/4] 生成随机密码 ..."
if grep -q '__PG_PASS__' "$COMPOSE_FILE"; then
  PG_PASS="$(openssl rand -hex 16)"
  REDIS_PASS="$(openssl rand -hex 16)"
  SESSION_SECRET="$(openssl rand -hex 32)"

  # 用 | 作分隔符，避免密码里的 / 破坏 sed
  sed -i "s|__PG_PASS__|${PG_PASS}|g"       "$COMPOSE_FILE"
  sed -i "s|__REDIS_PASS__|${REDIS_PASS}|g" "$COMPOSE_FILE"
  sed -i "s|__SESSION_SECRET__|${SESSION_SECRET}|g" "$COMPOSE_FILE"

  chmod 600 "$COMPOSE_FILE"
  echo "      ✅ 已写入随机密码（文件权限已收紧为 600）"
  echo "      ⚠️ 请立刻把 $COMPOSE_FILE 备份到安全位置 —— 密码只在这里"
else
  echo "      已生成过密码（未发现占位符），跳过"
fi

# ---------- ③ 启动 ----------
echo "[3/4] 启动容器 ..."
docker compose up -d

# ---------- ④ 等待就绪 ----------
echo "[4/4] 等待服务就绪 ..."
for i in $(seq 1 60); do
  if curl -fsS http://localhost:3000/api/status >/dev/null 2>&1; then
    echo "      ✅ 网关已就绪（等待 ${i} 秒）"
    break
  fi
  sleep 2
  [ "$i" -eq 60 ] && echo "      ⚠️ 超时，请看下面日志排查"
done

echo
docker compose ps
echo
echo "------------------------------------------"
echo " 下一步（务必都做）："
echo " 1. ⚠️ 在【云厂商控制台】的防火墙里放行 TCP 3000（不是在这台服务器里）"
echo " 2. 浏览器打开  http://<公网IP>:3000"
echo " 3. 用默认账号 root / 123456 首次登录，⚠️ 第一件事改管理员密码"
echo " 4. 添加上游渠道（填真实 key）→ 点『测试』确认通"
echo " 5. 给每个人建账号 + 令牌 + 配额，登记谁是哪把 key"
echo " 6. 端到端验收：用虚拟 key 打网关，再去后台日志核对是谁、扣了多少"
echo "------------------------------------------"
echo " 常用命令："
echo "   查看日志   docker compose logs -f new-api"
echo "   重启       docker compose restart"
echo "   备份       tar czf newapi-backup-\$(date +%F).tar.gz data/ $COMPOSE_FILE"
