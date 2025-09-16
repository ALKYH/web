#!/bin/bash

# MinIO服务管理脚本
# 用于启动、停止和检查MinIO服务状态

set -e

# 配置变量
MINIO_DATA_DIR="/data/minio"
MINIO_PORT="9000"
MINIO_CONSOLE_PORT="9001"
MINIO_BINARY="/usr/local/bin/minio"
MC_BINARY="/usr/local/bin/mc"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查MinIO是否已安装
check_minio_installed() {
    if [ ! -f "$MINIO_BINARY" ]; then
        log_error "MinIO binary not found at $MINIO_BINARY"
        log_error "Please install MinIO first:"
        log_error "  wget https://dl.min.io/server/minio/release/linux-amd64/minio -O $MINIO_BINARY"
        log_error "  chmod +x $MINIO_BINARY"
        exit 1
    fi
}

# 检查MinIO是否正在运行
check_minio_running() {
    if pgrep -f "minio server" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# 获取MinIO进程ID
get_minio_pid() {
    pgrep -f "minio server" || echo ""
}

# 启动MinIO服务
start_minio() {
    log_info "Starting MinIO service..."

    if check_minio_running; then
        log_warn "MinIO is already running (PID: $(get_minio_pid))"
        return 0
    fi

    # 确保数据目录存在
    mkdir -p "$MINIO_DATA_DIR"

    # 启动MinIO服务
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY no_proxy
    nohup "$MINIO_BINARY" server "$MINIO_DATA_DIR" --console-address ":$MINIO_CONSOLE_PORT" > /var/log/minio.log 2>&1 &

    # 等待服务启动
    log_info "Waiting for MinIO to start..."
    sleep 5

    if check_minio_running; then
        log_info "MinIO started successfully (PID: $(get_minio_pid))"
        log_info "MinIO Server: http://localhost:$MINIO_PORT"
        log_info "MinIO Console: http://localhost:$MINIO_CONSOLE_PORT"
        log_info "Access Key: minioadmin"
        log_info "Secret Key: minioadmin"
    else
        log_error "Failed to start MinIO"
        exit 1
    fi
}

# 停止MinIO服务
stop_minio() {
    log_info "Stopping MinIO service..."

    if ! check_minio_running; then
        log_warn "MinIO is not running"
        return 0
    fi

    local pid=$(get_minio_pid)
    if [ -n "$pid" ]; then
        kill "$pid"
        log_info "MinIO stopped (PID: $pid)"
    else
        log_error "Could not find MinIO process"
        exit 1
    fi

    # 等待进程完全停止
    sleep 2
    if check_minio_running; then
        log_warn "MinIO is still running, force killing..."
        kill -9 "$pid" 2>/dev/null || true
    fi
}

# 重启MinIO服务
restart_minio() {
    log_info "Restarting MinIO service..."
    stop_minio
    sleep 2
    start_minio
}

# 检查MinIO状态
status_minio() {
    if check_minio_running; then
        local pid=$(get_minio_pid)
        log_info "MinIO is running (PID: $pid)"
        log_info "MinIO Server: http://localhost:$MINIO_PORT"
        log_info "MinIO Console: http://localhost:$MINIO_CONSOLE_PORT"
    else
        log_info "MinIO is not running"
    fi
}

# 初始化存储桶
init_buckets() {
    log_info "Initializing MinIO buckets..."

    if ! check_minio_running; then
        log_error "MinIO is not running. Please start MinIO first."
        exit 1
    fi

    # 配置MinIO客户端别名
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY no_proxy
    "$MC_BINARY" alias set local "http://localhost:$MINIO_PORT" minioadmin minioadmin

    # 创建存储桶
    "$MC_BINARY" mb local/avatars 2>/dev/null || log_warn "Bucket 'avatars' may already exist"
    "$MC_BINARY" mb local/documents 2>/dev/null || log_warn "Bucket 'documents' may already exist"
    "$MC_BINARY" mb local/general 2>/dev/null || log_warn "Bucket 'general' may already exist"

    log_info "Buckets initialized successfully"
    log_info "Available buckets:"
    "$MC_BINARY" ls local/
}

# 显示帮助信息
show_help() {
    echo "MinIO Service Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start MinIO service"
    echo "  stop      Stop MinIO service"
    echo "  restart   Restart MinIO service"
    echo "  status    Show MinIO service status"
    echo "  init      Initialize MinIO buckets"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start    # Start MinIO service"
    echo "  $0 stop     # Stop MinIO service"
    echo "  $0 status   # Check MinIO status"
    echo "  $0 init     # Initialize buckets"
}

# 主函数
main() {
    check_minio_installed

    case "${1:-help}" in
        start)
            start_minio
            ;;
        stop)
            stop_minio
            ;;
        restart)
            restart_minio
            ;;
        status)
            status_minio
            ;;
        init)
            init_buckets
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
