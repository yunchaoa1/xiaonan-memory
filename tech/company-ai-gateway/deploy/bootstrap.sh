#!/usr/bin/env bash
# 公司 AI 网关 · 一键部署脚本（在云服务器上以 root 执行）
# 用法：把整个 deploy 目录传到服务器，然后  bash bootstrap.sh
set -euo pipefail

cd "$(dirname "$0")"

echo "=========================================="
echo " 公司 AI 网关部署 · New API"
echo "=========================================="

# ---------- 1. 检查系统 ----------
if [ "$(id -u)" -ne 0 ]; then
  echo "❌ 请用 root 运行：sudo bash bootstrap.sh"
  exit 1
fi

echo "→ 系统信息：$(lsb_release -ds 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2)"

# ---------- 2. 安装 Docker ----------
if ! command -v docker >/dev/null 2>&1; then
  echo "→ 安装 Docker（使用官方脚本）..."
  curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
  sh /tmp/get-docker.sh
  systemctl enable --now docker
else
  echo "→ Docker 已安装：$(docker --version)"
fi

# docker compose 插件检查
if ! docker compose version >/dev/null 2>&1; then
  echo "❌ docker compose 插件不可用，请检查 Docker 安装"
  exit 1
fi

# ---------- 3. 生成随机密码 ----------
if grep -q "__PG_PASS__" docker-compose.yml; then
  PG_PASS=$(openssl rand -hex 16)
  REDIS_PASS=$(openssl rand -hex 16)
  SESSION_SECRET=$(openssl rand -hex 32)

  sed -i "s/__PG_PASS__/${PG_PASS}/g" docker-compose.yml
  sed -i "s/__REDIS_PASS__/${REDIS_PASS}/g" docker-compose.yml
  sed -i "s/__SESSION_SECRET__/${SESSION_SECRET}/g" docker-compose.yml

  echo "→ 已生成随机数据库 / Redis / Session 密码"
  echo "   （凭据已写入 docker-compose.yml，请妥善保管该文件）"
else
  echo "→ 密码占位符已被替换过，跳过生成（沿用现有配置）"
fi

# ---------- 4. 启动服务 ----------
echo "→ 拉起容器（首次会拉镜像，可能要几分钟）..."
docker compose up -d

# ---------- 5. 等待就绪 ----------
echo "→ 等待网关就绪..."
for i in $(seq 1 30); do
  if curl -fsS http://localhost:3000/api/status >/dev/null 2>&1; then
    echo "✅ 网关已就绪"
    break
  fi
  sleep 3
  if [ "$i" -eq 30 ]; then
    echo "⚠️ 60 秒内未就绪，请查看日志：docker compose logs -f new-api"
  fi
done

# ---------- 6. 输出访问信息 ----------
PUBLIC_IP=$(curl -fsS --max-time 5 https://api.ipify.org 2>/dev/null || echo "<服务器公网IP>")

echo ""
echo "=========================================="
echo " 部署完成"
echo "=========================================="
echo " 控制台地址：http://${PUBLIC_IP}:3000"
echo " 默认管理员：root"
echo " 默认密码：  123456   ← ⚠️ 登录后立刻修改！"
echo ""
echo " ⚠️ 下一步（人工）："
echo "   1) 云控制台防火墙放行 TCP 3000"
echo "   2) 浏览器打开上面地址，用 root / 123456 登录"
echo "   3) 第一件事：改管理员密码"
echo "   4) 添加 DeepSeek 渠道（填公司 API key）"
echo "   5) 建 4 个用户 + 虚拟令牌 + 额度上限"
echo "=========================================="
echo ""
echo "常用命令："
echo "  查看日志： docker compose logs -f new-api"
echo "  重启：     docker compose restart"
echo "  停止：     docker compose down"
echo "  备份数据： tar czf newapi-backup-\$(date +%F).tar.gz data/ docker-compose.yml"
