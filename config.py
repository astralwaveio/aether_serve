import os
from dotenv import load_dotenv

# 从 .env 文件加载环境变量
load_dotenv()

class Config:
    """
    AetherServe 应用的配置类。
    """
    # 从环境变量中获取 SECRET_KEY，如果不存在则使用一个默认值。
    # 在生产环境中，强烈建议通过环境变量设置一个复杂且随机的密钥。
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'aether_serve_default_secret_key_change_this_in_production'

    # 文件服务器的根目录。
    # 必须从 .env 文件中获取，因为它通常是环境特定的。
    # 如果 .env 中未设置，则回退到当前脚本所在目录的上一级目录下的 'AetherServe_Files' 文件夹。
    # 强烈建议在 .env 中明确设置此路径。
    _default_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'AetherServe_Files'))
    FILE_SERVER_ROOT_DIR = os.environ.get('FILE_SERVER_ROOT_DIR') or _default_root

    # 允许预览的最大文件大小（字节）。
    # 超过此大小的文本文件将只显示部分内容并提供下载选项。
    MAX_PREVIEW_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

    # 可识别的文本文件扩展名列表，用于在线预览和语法高亮。
    # 此列表用作回退或初始过滤，但 python-magic 将用于更健壮的 MIME 类型检测。
    TEXT_FILE_EXTENSIONS = [
        '.txt', '.log', '.md', '.json', '.xml', '.html', '.css', '.js',
        '.py', '.java', '.php', '.c', '.cpp', '.h', '.sh', '.conf',
        '.ini', '.yml', '.yaml', '.sql', '.csv', '.tsv', '.bat', '.ps1',
        '.go', '.rb', '.pl', '.swift', '.kt', '.ts', '.jsx', '.tsx',
        '.vue', '.scss', '.less', '.sgmodule'
    ]

    # 可识别的图片文件扩展名列表，用于在线预览。
    IMAGE_FILE_EXTENSIONS = [
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'
    ]

    # 需要隐藏的文件或文件夹名称列表（支持通配符，如 '*.log' 或 'temp_*'）
    # 这些项将不会在目录列表中显示。
    # 示例：
    # HIDDEN_ITEMS = ['.git', '.DS_Store', '__pycache__', '*.pyc', 'temp_files', 'my_secret_folder']
    HIDDEN_ITEMS = [
        '.git',         # Git 版本控制目录
        '.gitignore',   # Git 忽略文件
        '.env',         # 环境变量文件
        '__pycache__',  # Python 编译缓存目录
        '*.pyc',        # Python 编译文件
        'venv',         # Python 虚拟环境目录
        'gunicorn_start.sh', # Gunicorn 启动脚本
        'aetherserve.sock', # Gunicorn socket 文件
        'config.py',    # 配置文件
        'app.py',       # 主应用文件
        'utils',        # 工具目录
        'templates',    # 模板目录
        'static',       # 静态文件目录
        'requirements.txt', # 依赖文件
        'README.md',    # README 文件
        'pyproject.toml', # 项目配置
        'dist'          # 打包输出目录
    ]

    # 确保根目录存在，如果不存在则创建
    if not os.path.exists(FILE_SERVER_ROOT_DIR):
        try:
            os.makedirs(FILE_SERVER_ROOT_DIR)
            print(f"Created FILE_SERVER_ROOT_DIR: {FILE_SERVER_ROOT_DIR}")
        except OSError as e:
            print(f"Error creating FILE_SERVER_ROOT_DIR {FILE_SERVER_ROOT_DIR}: {e}")
            # 如果创建失败，可能需要更严格的错误处理或退出
