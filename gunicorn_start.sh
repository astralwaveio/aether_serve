#!/bin/bash

NAME="aetherserve"                                      # 应用名称
FLASKDIR=/opt/aetherserve                               # Flask 项目目录
VENVDIR=$FLASKDIR/.venv                                  # 虚拟环境目录
SOCKFILE=$FLASKDIR/aetherserve.sock                     # Gunicorn socket 文件
USER=root                                               # 运行 Gunicorn 的用户 (Nginx 通常用 www-data，但这里使用 root 作为示例)
GROUP=root                                              # 运行 Gunicorn 的组
NUM_WORKERS=4                                           # Gunicorn worker 数量 (通常 2 * CPU核心数 + 1)
FLASKAPP=app:app                                        # Flask 应用的启动点 (app.py 中的 app 实例)

echo "Starting $NAME as `whoami`"

# 激活虚拟环境
cd $FLASKDIR
source $VENVDIR/bin/activate

# 删除旧的 socket 文件
rm -f $SOCKFILE

# 启动 Gunicorn
exec $VENVDIR/bin/gunicorn ${FLASKAPP} \
  --worker-class gevent \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind=unix:$SOCKFILE \
  --log-level=info \
  --log-file=-
