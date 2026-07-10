#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

info() { echo "[OK] $*"; }
warn() { echo "[WARN] $*"; }
error() { echo "[ERROR] $*" >&2; }

ensure_env() {
  if [[ ! -f "env/.env.dev" ]]; then
    if [[ -f "env/.env.dev.example" ]]; then
      warn "未找到 env/.env.dev，正在从示例复制..."
      cp "env/.env.dev.example" "env/.env.dev"
      warn "请编辑 env/.env.dev 后重新运行"
    else
      error "未找到 env/.env.dev"
      exit 1
    fi
  fi
}

sync_deps() {
  info "同步依赖 (uv sync)..."
  uv sync
}

start_dev() {
  ensure_env
  info "启动开发服务..."
  uv run main.py run --env=dev
}

revision() {
  ensure_env
  info "生成迁移脚本..."
  uv run main.py revision --env=dev
}

upgrade() {
  ensure_env
  info "应用迁移..."
  uv run main.py upgrade --env=dev
}

reset() {
  ensure_env
  warn "将删表重建并导入种子数据"
  uv run main.py reset --env=dev
}

export_req() {
  info "导出生产 requirements.txt..."
  uv export --no-dev -o requirements.txt
}

usage() {
  cat <<'EOF'
FastAPI Web Admin - uv 开发脚本

用法:
  ./run_linux.sh sync      安装/同步依赖
  ./run_linux.sh dev       启动开发服务
  ./run_linux.sh revision  生成迁移脚本
  ./run_linux.sh upgrade   应用迁移
  ./run_linux.sh reset     删表重建并导入种子
  ./run_linux.sh export    导出生产 requirements.txt
EOF
}

case "${1:-}" in
  sync) sync_deps ;;
  dev) start_dev ;;
  revision) revision ;;
  upgrade) upgrade ;;
  reset) reset ;;
  export) export_req ;;
  *)
    usage
    exit 1
    ;;
esac
