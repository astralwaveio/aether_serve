```markdown
# AetherServe

AetherServe 是一个轻量级、美观且功能丰富的 HTTP 文件服务器，专为快速、安全、只读的文件共享而设计。它提供无缝的文件浏览、多种文件类型（包括代码和图片）的在线预览、便捷的内容复制和高效的文件搜索功能，无需用户认证和文件上传。

---

## ✨ 功能特性

- **直观的文件/文件夹浏览**
  - 清晰、响应式的列表展示文件和目录。
  - 支持递归浏览，带“返回上一级”和面包屑导航。
  - 文件与文件夹通过不同图标和样式区分。

- **高级文本文件预览**
  - 支持 `.txt`, `.log`, `.md`, `.json`, `.xml`, `.html`, `.css`, `.js`, `.py`, `.java`, `.php`, `.c`, `.cpp`, `.h`, `.sh`, `.conf`, `.ini`, `.yml`, `.yaml`, `.sql`, `.csv`, `.tsv`, `.bat`, `.ps1`, `.go`, `.rb`, `.pl`, `.swift`, `.kt`, `.ts`, `.jsx`, `.tsx`, `.vue`, `.scss`, `.less`, `.sgmodule` 等多种文本格式。
  - 内置语法高亮（Syntax Highlighting），提升代码和配置文件可读性。
  - 智能截断大文件预览，避免内存溢出，并提供完整下载选项。

- **图片文件预览**
  - 支持 `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.svg`, `.webp`, `.ico` 等常见图片格式。

- **便捷的内容复制**
  - 一键复制文件/文件夹的完整可访问 URL（含域名和 HTTPS）。
  - 文本文件预览页可一键复制全部内容。

- **灵活的文件下载**
  - 所有文件均可直接下载。
  - 不支持在线预览的文件仅通过“下载”按钮获取，避免误触。

- **强大的文件搜索**
  - 当前目录实时搜索：输入关键词实时过滤当前目录下的文件和文件夹。
  - 全局搜索：在根目录及所有子目录中快速定位目标文件。

- **安全与稳定**
  - 内置严格的目录穿越（Directory Traversal）防护，确保访问安全。
  - 不提供认证和上传功能，进一步降低安全风险。

- **现代化用户界面**
  - 基于 Bootstrap 5，界面清爽、响应式，适配桌面、平板和移动设备。
  - 导航栏高度优化，用户体验一致。

---

## 🛠️ 技术栈

- **后端**：Python 3.x, Flask
- **前端**：HTML5, CSS3 (Bootstrap 5), JavaScript (Vanilla JS, Prism.js 用于语法高亮, Font Awesome 用于图标)
- **依赖管理**：pip, python-dotenv（环境变量管理）, python-magic（文件类型识别）

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/astralwaveio/aether_serve.git
cd aether_serve
```

### 2. 配置环境

编辑项目根目录下的 `.env` 文件，设置 `FILE_SERVER_ROOT_DIR` 为你希望服务的文件目录绝对路径。

示例 `.env` 文件内容：

```ini
SECRET_KEY=your_very_secret_key_for_AetherServe_development_CHANGE_ME_IN_PROD
FILE_SERVER_ROOT_DIR=/tmp/AetherServe_Files # <-- 务必修改为实际路径！
```

确保该目录存在且有读取权限。

### 3. 安装依赖

建议使用虚拟环境：

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# .\venv\Scripts\activate # Windows PowerShell

pip install -r requirements.txt
```

#### 注意：python-magic 的系统依赖

- **macOS**：`brew install libmagic`
- **Debian/Ubuntu**：`sudo apt-get update && sudo apt-get install libmagic1`
- **CentOS/Fedora**：`sudo yum install file-devel` 或 `sudo dnf install file-devel`
- **Windows**：建议使用 WSL，或尝试 `pip install python-magic-bin`，或手动下载 libmagic DLL 并放入 PATH。

### 4. 运行 AetherServe

```bash
python app.py
```

默认启动在 [http://127.0.0.1:5000](http://127.0.0.1:5000)。

---

## 🖥️ 使用说明

- **浏览文件**：主页展示 `FILE_SERVER_ROOT_DIR` 下的文件和文件夹，点击文件夹进入子目录。
- **返回上一级**：顶部“返回上一级”按钮或面包屑导航。
- **预览文本文件**：点击支持的文本文件（如 `.txt`, `.py`, `.json` 等）可在线预览，自动语法高亮。
- **预览图片**：点击图片文件（如 `.jpg`, `.png` 等）直接显示图片。
- **复制路径/内容**：
  - 列表页每个条目旁有“复制路径”按钮，复制完整可访问 URL。
  - 文本文件预览页有“复制内容”按钮，复制全部内容。
- **下载文件**：列表和预览页均有“下载”按钮。不可预览文件仅可通过“下载”按钮获取。
- **当前目录搜索**：右上角输入关键词实时过滤当前目录。
- **全局搜索**：导航栏搜索框可全局查找文件和文件夹。

---

## 🚀 部署指南

### 1. 生产环境部署（推荐 Gunicorn + Nginx + Systemd）

#### 1.1. 准备服务器

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git nginx -y
sudo apt install libmagic1 -y
```

#### 1.2. 项目部署

```bash
sudo mkdir -p /var/www/aetherserve
sudo chown -R your_user:your_group /var/www/aetherserve
cd /var/www/aetherserve
sudo git clone https://github.com/astralwaveio/aether_serve.git .
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

编辑 `.env` 文件，设置强随机的 `SECRET_KEY` 和实际的 `FILE_SERVER_ROOT_DIR`：

```ini
SECRET_KEY=YOUR_GENERATED_RANDOM_SECRET_KEY_HERE
FILE_SERVER_ROOT_DIR=/mnt/my_aetherserve_data
```

确保目录存在且 `www-data` 用户有读取权限：

```bash
sudo mkdir -p /mnt/my_aetherserve_data
sudo chown -R www-data:www-data /mnt/my_aetherserve_data
```

#### 1.3. Gunicorn 启动脚本

`/var/www/aetherserve/gunicorn_start.sh`：

```bash
#!/bin/bash

NAME="aetherserve"
FLASKDIR=/var/www/aetherserve
VENVDIR=$FLASKDIR/venv
SOCKFILE=$FLASKDIR/aetherserve.sock
USER=www-data
GROUP=www-data
NUM_WORKERS=3
FLASKAPP=app:app

echo "Starting $NAME as `whoami`"

cd $FLASKDIR
source $VENVDIR/bin/activate

rm -f $SOCKFILE

exec $VENVDIR/bin/gunicorn ${FLASKAPP} \
  --worker-class sync \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind=unix:$SOCKFILE \
  --log-level=info \
  --log-file=-
```

赋予执行权限：

```bash
sudo chmod +x /var/www/aetherserve/gunicorn_start.sh
```

#### 1.4. Systemd 服务

`/etc/systemd/system/aetherserve.service`：

```ini
[Unit]
Description=Gunicorn instance to serve AetherServe
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/aetherserve
ExecStart=/bin/bash /var/www/aetherserve/gunicorn_start.sh
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

操作流程：

```bash
sudo systemctl daemon-reload
sudo systemctl start aetherserve
sudo systemctl status aetherserve
sudo systemctl enable aetherserve
```

#### 1.5. Nginx 配置

`/etc/nginx/sites-available/aetherserve`：

```nginx
server {
    listen 80;
    server_name your_domain.com;

    client_max_body_size 100M;

    location /static {
        alias /var/www/aetherserve/static;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location / {
        proxy_pass http://unix:/var/www/aetherserve/aetherserve.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    error_page 404 /404.html;
    location = /404.html {
        root /var/www/aetherserve/templates;
        internal;
    }
}
```

激活配置并重启 Nginx：

```bash
sudo ln -s /etc/nginx/sites-available/aetherserve /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

#### 1.6. 配置 HTTPS（强烈推荐）

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your_domain.com
```

#### 1.7. 防火墙设置

```bash
sudo ufw allow 'Nginx HTTP'
sudo ufw allow 'Nginx HTTPS'
sudo ufw enable
```

---

### 2. 使用 pipx 进行本地安装和开发

#### 2.1. 项目结构调整

```
aether_serve/
├── aetherserve/
│   ├── __init__.py
│   └── app.py
├── config.py
├── static/
├── templates/
├── utils/
├── .env
├── .gitignore
├── requirements.txt
├── README.md
└── pyproject.toml
```

`aetherserve/app.py` 示例（需包含 `run_server` 启动函数）：

```python
# ... Flask 应用实例 app 的创建 ...

def run_server():
    """
    启动 AetherServe Flask 应用（供 pipx 或脚本调用）。
    """
    if not os.path.exists(app.config['FILE_SERVER_ROOT_DIR']):
        try:
            os.makedirs(app.config['FILE_SERVER_ROOT_DIR'])
            print(f"Created FILE_SERVER_ROOT_DIR: {app.config['FILE_SERVER_ROOT_DIR']}")
        except OSError as e:
            print(f"Error creating FILE_SERVER_ROOT_DIR {app.config['FILE_SERVER_ROOT_DIR']}: {e}")
            import sys
            sys.exit(1)

    print("Starting AetherServe...")
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    run_server()
```

`pyproject.toml` 示例：

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "aetherserve"
version = "0.1.0"
authors = [
  { name="astralwaveio", email="your@example.com" }
]
description = "A clean and simple HTTP file server."
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "Flask==2.3.2",
    "python-dotenv==1.0.0",
    "python-magic==0.4.27"
]
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Environment :: Web Environment",
    "Framework :: Flask",
    "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    "Topic :: System :: Filesystems",
]

[project.urls]
Homepage = "https://github.com/astralwaveio/aether_serve"
"Bug Tracker" = "https://github.com/astralwaveio/aether_serve/issues"

[project.scripts]
aetherserve = "aetherserve.app:run_server"
```

#### 2.2. 安装 pipx

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

#### 2.3. 打包项目

```bash
python3 -m build
```

#### 2.4. 使用 pipx 安装 AetherServe

- 本地安装：

  ```bash
  pipx install .  # 在项目根目录
  ```

- 从 PyPI 安装（如已发布）：

  ```bash
  pipx install aetherserve
  ```

#### 2.5. 运行 AetherServe

```bash
aetherserve
```

---

### ⚠️ pipx 局限性

- 仅适合本地开发或个人工具，不推荐生产环境。
- 默认前台运行，关闭终端即停止。
- 使用 Flask 内置开发服务器，不具备生产级性能与安全。
- 需手动管理 `.env` 配置。

---

## 总结

- **生产部署**：强烈建议使用 Gunicorn + Nginx + Systemd，具备高稳定性、性能和易管理性。
- **本地开发/个人工具**：pipx 便捷易用，但有局限。

希望本指南能帮助你顺利部署和使用 AetherServe！
```
