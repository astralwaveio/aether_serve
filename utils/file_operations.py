import os
import stat
from datetime import datetime
from flask import current_app
import magic # Import the python-magic library

def _get_absolute_path(relative_path):
    """
    将相对路径转换为相对于 FILE_SERVER_ROOT_DIR 的绝对路径。
    并进行目录穿越安全检查。
    """
    root_dir = current_app.config['FILE_SERVER_ROOT_DIR']
    # 确保相对路径是安全的，防止目录穿越
    # os.path.normpath 规范化路径，处理 ../ 等
    # os.path.join 安全地拼接路径
    absolute_path = os.path.normpath(os.path.join(root_dir, relative_path))

    # 关键安全检查：确保生成的绝对路径仍然在根目录下
    # os.path.commonpath 返回两个路径的共同前缀
    # 如果共同前缀不是根目录本身，则说明尝试穿越
    if not os.path.commonpath([root_dir, absolute_path]) == root_dir:
        raise ValueError("Attempted directory traversal detected!")

    return absolute_path

def list_directory(relative_path):
    """
    列出指定相对路径下的文件和文件夹。
    返回一个包含文件/文件夹信息的列表。
    """
    try:
        absolute_path = _get_absolute_path(relative_path)
        if not os.path.isdir(absolute_path):
            raise FileNotFoundError(f"Directory not found: {relative_path}")

        items = []
        for item_name in os.listdir(absolute_path):
            item_path = os.path.join(absolute_path, item_name)
            item_relative_path = os.path.join(relative_path, item_name)
            try:
                # 获取文件状态信息，避免多次调用 os.path.isdir/isfile
                item_stat = os.stat(item_path)
                is_dir = stat.S_ISDIR(item_stat.st_mode)
                size = item_stat.st_size if not is_dir else 0  # 文件夹大小通常显示为0或不显示
                modified_time = datetime.fromtimestamp(item_stat.st_mtime)

                items.append({
                    'name': item_name,
                    'path': item_relative_path, # 用于前端链接
                    'is_dir': is_dir,
                    'size': size,
                    'modified_time': modified_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'is_text': is_text_file(item_relative_path) if not is_dir else False, # 新增：是否为文本文件
                    'is_image': is_image_file(item_relative_path) if not is_dir else False # 新增：是否为图片文件
                })
            except OSError:
                # 忽略无法访问的文件或目录（例如权限问题）
                continue

        # 优先显示文件夹，然后按名称排序
        items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        return items

    except ValueError as e:
        # 目录穿越攻击
        current_app.logger.warning(f"Security alert: {e} for path {relative_path}")
        raise FileNotFoundError("Invalid path or access denied.")
    except FileNotFoundError:
        raise
    except Exception as e:
        current_app.logger.error(f"Error listing directory {relative_path}: {e}")
        raise Exception("Failed to list directory.")

def read_text_file(relative_path):
    """
    读取指定相对路径的文本文件内容。
    处理大文件截断和安全检查。
    """
    try:
        absolute_path = _get_absolute_path(relative_path)
        if not os.path.isfile(absolute_path):
            raise FileNotFoundError(f"File not found: {relative_path}")

        file_size = os.path.getsize(absolute_path)
        max_preview_size = current_app.config['MAX_PREVIEW_FILE_SIZE']
        is_truncated = False
        content = ""

        # 检查文件是否是可预览的文本文件类型
        if not is_text_file(relative_path): # 使用新的 is_text_file
            return "", False # 不是可预览的文本文件

        # 处理大文件
        if file_size > max_preview_size:
            is_truncated = True
            # 读取文件开头的一部分
            with open(absolute_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(max_preview_size) # 读取指定字节数
        else:
            # 读取整个文件
            with open(absolute_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

        return content, is_truncated

    except ValueError as e:
        current_app.logger.warning(f"Security alert: {e} for path {relative_path}")
        raise FileNotFoundError("Invalid path or access denied.")
    except FileNotFoundError:
        raise
    except Exception as e:
        current_app.logger.error(f"Error reading file {relative_path}: {e}")
        raise Exception("Failed to read file.")

def get_file_info(relative_path):
    """
    获取单个文件或文件夹的详细信息。
    """
    try:
        absolute_path = _get_absolute_path(relative_path)
        if not os.path.exists(absolute_path):
            raise FileNotFoundError(f"Path not found: {relative_path}")

        item_stat = os.stat(absolute_path)
        is_dir = stat.S_ISDIR(item_stat.st_mode)
        size = item_stat.st_size if not is_dir else 0
        modified_time = datetime.fromtimestamp(item_stat.st_mtime)

        return {
            'name': os.path.basename(relative_path),
            'path': relative_path,
            'is_dir': is_dir,
            'size': size,
            'modified_time': modified_time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except ValueError as e:
        current_app.logger.warning(f"Security alert: {e} for path {relative_path}")
        raise FileNotFoundError("Invalid path or access denied.")
    except FileNotFoundError:
        raise
    except Exception as e:
        current_app.logger.error(f"Error getting info for {relative_path}: {e}")
        raise Exception("Failed to get file info.")

def _get_mime_type(absolute_path):
    """
    使用 python-magic 获取文件的 MIME 类型。
    """
    try:
        return magic.Magic(mime=True).from_file(absolute_path)
    except Exception as e:
        current_app.logger.debug(f"python-magic failed for {absolute_path}: {e}")
        return None

def is_text_file(relative_path):
    """
    判断文件是否是可预览的文本文件。
    优先使用 python-magic 进行 MIME 类型检测，如果失败或不是明确的文本类型，则回退到扩展名检查。
    """
    absolute_path = _get_absolute_path(relative_path)

    if not os.path.isfile(absolute_path):
        return False # 不是文件，所以不是文本文件。

    mime_type = _get_mime_type(absolute_path)
    if mime_type:
        # 常见文本 MIME 类型
        if mime_type.startswith('text/') or \
           mime_type in ['application/json', 'application/javascript', 'application/xml',
                         'application/x-sh', 'application/x-python', 'application/x-php',
                         'application/x-java', 'application/sql', 'application/yaml',
                         'application/x-yaml', 'application/x-perl', 'application/x-ruby',
                         'application/x-go', 'application/x-swift', 'application/typescript',
                         'application/x-powershell', 'application/x-bat', 'application/csv',
                         'application/vnd.ms-excel', # 对于某些CSV/TSV文件，可能被识别为excel
                        ]:
            return True

    # 回退到扩展名检查
    file_extension = os.path.splitext(relative_path)[1].lower()
    return file_extension in current_app.config['TEXT_FILE_EXTENSIONS']

def is_image_file(relative_path):
    """
    判断文件是否是可预览的图片文件。
    优先使用 python-magic 进行 MIME 类型检测，如果失败或不是明确的图片类型，则回退到扩展名检查。
    """
    absolute_path = _get_absolute_path(relative_path)

    if not os.path.isfile(absolute_path):
        return False # 不是文件，所以不是图片文件。

    mime_type = _get_mime_type(absolute_path)
    if mime_type:
        # 常见图片 MIME 类型
        if mime_type.startswith('image/'):
            return True

    # 回退到扩展名检查
    file_extension = os.path.splitext(relative_path)[1].lower()
    return file_extension in current_app.config['IMAGE_FILE_EXTENSIONS']
