#!/bin/bash

# AetherServe 应用名称
NAME="aetherserve"
# Flask 项目的根目录
FLASKDIR=/opt/aetherserve
# 虚拟环境的目录
VENVDIR=$FLASKDIR/.venv
# Gunicorn 用于与 Nginx 通信的 Unix socket 文件路径 (如果使用 TCP 端口，此变量将不再被 --bind 使用)
SOCKFILE=$FLASKDIR/aetherserve.sock
# 运行 Gunicorn 进程的用户 (通常与 Nginx 用户一致，以确保权限)
USER=root
# 运行 Gunicorn 进程的组
GROUP=root
# Gunicorn worker 进程数量 (推荐 2 * CPU核心数 + 1)
NUM_WORKERS=4
# Flask 应用的启动点：模块名:应用实例名 (例如 app.py 中的 'app' 实例)
# 假设 app.py 位于 /opt/aetherserve/app.py
FLASKAPP=app:app

# 自定义 Gunicorn 监听的 TCP 端口
# 如果您希望 Gunicorn 直接监听一个端口，请在这里设置。
# 例如，设置为 8000。
# 注意：如果 Nginx 仍然作为反向代理，Nginx 会监听 80/443 端口，
# 然后转发到这个 Gunicorn 监听的端口。
PORT=30280 # <-- 在这里自定义您希望 Gunicorn 监听的端口

echo "正在启动 $NAME，用户为 `whoami`"

# 切换到 Flask 项目目录
cd $FLASKDIR

# 激活虚拟环境
source $VENVDIR/bin/activate

# 删除旧的 socket 文件 (如果使用 TCP 端口，此行可以安全地移除，但保留也无害)
rm -f $SOCKFILE

# 启动 Gunicorn
# --worker-class sync 是默认的同步 worker，如果需要异步，可以改为 gevent 或 eventlet (需额外安装)
# --workers 指定 worker 数量
# --user 和 --group 指定运行用户和组
# --bind=0.0.0.0:$PORT 指定绑定到所有网络接口的指定 TCP 端口
# --log-level=info 设置日志级别
# --log-file=- 将日志输出到标准输出，Systemd 会捕获这些日志
exec $VENVDIR/bin/gunicorn ${FLASKAPP} \
  --worker-class sync \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind=0.0.0.0:$PORT \
  --log-level=info \
  --log-file=-
