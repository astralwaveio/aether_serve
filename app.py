import argparse
import os
import sys

from flask import Flask, render_template, request, send_from_directory, abort

from config import Config
# 导入文件操作和搜索工具模块
from utils import file_operations, search_utils

# 创建 Flask 应用实例
app = Flask(__name__)
# 从 Config 类加载配置
app.config.from_object(Config)


@app.errorhandler(404)
def page_not_found(e):
    """
    自定义 404 错误页面处理。
    """
    return render_template('error.html', error_code=404, error_message="文件或目录未找到。"), 404


@app.errorhandler(403)
def forbidden(e):
    """
    自定义 403 错误页面处理。
    """
    return render_template('error.html', error_code=403, error_message="禁止访问。"), 403


@app.errorhandler(500)
def internal_server_error(e):
    """
    自定义 500 错误页面处理。
    """
    return render_template('error.html', error_code=500, error_message="服务器内部错误。"), 500


@app.route('/')
@app.route('/browse/')
@app.route('/browse/<path:sub_path>')
def browse(sub_path=''):
    """
    浏览文件和文件夹的路由。
    根据 sub_path 显示对应目录的内容。
    """
    try:
        # 规范化路径，移除开头的斜杠，防止 os.path.join 出现问题
        current_path = sub_path.strip('/')
        items = file_operations.list_directory(current_path)

        # 构建面包屑导航
        breadcrumbs = []
        if current_path:
            parts = current_path.split('/')
            for i in range(len(parts)):
                path_segment = '/'.join(parts[:i + 1])
                breadcrumbs.append({'name': parts[i], 'path': path_segment})

        # 返回上一级目录的路径
        parent_path = os.path.dirname(current_path)
        if parent_path == '/':  # 根目录的上一级是空字符串
            parent_path = ''

        return render_template(
            'index.html',
            current_path=current_path,
            items=items,
            breadcrumbs=breadcrumbs,
            parent_path=parent_path,
            base_url=request.url_root  # 传递 base_url 到模板，用于复制完整路径
        )
    except FileNotFoundError:
        # 如果文件或目录未找到，返回 404 错误
        abort(404)
    except ValueError:
        # 如果检测到目录穿越尝试，返回 403 错误
        abort(403)
    except Exception as e:
        # 记录其他未知错误并返回 500 错误
        app.logger.error(f"浏览路由错误，路径: {sub_path}: {e}")
        abort(500)


@app.route('/preview/<path:file_path>')
def preview(file_path):
    """
    预览文件（文本或图片）的路由。
    根据文件类型渲染不同的预览模板。
    """
    try:
        # 规范化文件路径
        file_path = file_path.strip('/')

        # 获取文件信息，用于显示文件名和大小
        file_info = file_operations.get_file_info(file_path)

        # 判断文件类型并渲染相应模板
        if file_operations.is_text_file(file_path):
            content, is_truncated = file_operations.read_text_file(file_path)
            return render_template(
                'preview.html',
                file_path=file_path,
                file_name=file_info['name'],
                file_size=file_info['size'],
                content=content,
                is_truncated=is_truncated,
                base_url=request.url_root  # 传递 base_url 到模板
            )
        elif file_operations.is_image_file(file_path):
            # 图片文件直接渲染图片预览模板
            return render_template(
                'image_preview.html',
                file_path=file_path,
                file_name=file_info['name'],
                file_size=file_info['size'],
                base_url=request.url_root  # 传递 base_url 到模板
            )
        else:
            # 既不是文本也不是图片，则尝试下载
            return download_file(file_path)

    except FileNotFoundError:
        # 文件未找到，返回 404 错误
        abort(404)
    except ValueError:
        # 目录穿越尝试，返回 403 错误
        abort(403)
    except Exception as e:
        # 记录其他未知错误并返回 500 错误
        app.logger.error(f"预览路由错误，文件: {file_path}: {e}")
        abort(500)


@app.route('/download/<path:file_path>')
def download_file(file_path):
    """
    下载文件的路由。
    强制浏览器下载指定文件。
    """
    try:
        # 规范化文件路径
        file_path = file_path.strip('/')
        absolute_file_path = file_operations._get_absolute_path(file_path)

        if not os.path.isfile(absolute_file_path):
            # 如果不是文件或文件不存在，返回 404 错误
            abort(404)

        # send_from_directory 用于从指定目录发送文件
        # os.path.dirname(absolute_file_path) 是文件所在的目录
        # os.path.basename(absolute_file_path) 是文件名
        return send_from_directory(
            os.path.dirname(absolute_file_path),
            os.path.basename(absolute_file_path),
            as_attachment=True  # 强制下载
        )
    except FileNotFoundError:
        # 文件未找到，返回 404 错误
        abort(404)
    except ValueError:
        # 目录穿越尝试，返回 403 错误
        abort(403)
    except Exception as e:
        # 记录其他未知错误并返回 500 错误
        app.logger.error(f"下载路由错误，文件: {file_path}: {e}")
        abort(500)


@app.route('/serve_image/<path:image_path>')
def serve_image(image_path):
    """
    专门用于直接提供图片文件，不强制下载。
    浏览器可以直接显示图片。
    """
    try:
        image_path = image_path.strip('/')
        absolute_image_path = file_operations._get_absolute_path(image_path)

        if not os.path.isfile(absolute_image_path):
            # 如果不是文件或文件不存在，返回 404 错误
            abort(404)

        # send_from_directory 会自动处理 MIME 类型
        return send_from_directory(
            os.path.dirname(absolute_image_path),
            os.path.basename(absolute_image_path),
            as_attachment=False  # 不强制下载
        )
    except FileNotFoundError:
        # 图片未找到，返回 404 错误
        abort(404)
    except ValueError:
        # 目录穿越尝试，返回 403 错误
        abort(403)
    except Exception as e:
        # 记录其他未知错误并返回 500 错误
        app.logger.error(f"图片服务路由错误，图片: {image_path}: {e}")
        abort(500)


@app.route('/search')
def search():
    """
    全局搜索文件的路由。
    根据查询关键词在文件服务根目录下搜索文件和文件夹。
    """
    query = request.args.get('query', '').strip()
    results = []
    if query:
        try:
            results = search_utils.search_files_globally(query)
        except Exception as e:
            # 记录搜索错误
            app.logger.error(f"全局搜索错误，查询: '{query}': {e}")
            # 可以选择返回一个错误信息给用户，或者直接返回空结果
            results = []

    return render_template('search_results.html', query=query, results=results,
                           base_url=request.url_root)  # 传递 base_url 到模板


# 启动服务器的主函数，供 pipx 或其他脚本调用
def run_server(host='0.0.0.0', port=5000, root_dir=None):
    """
    启动 AetherServe Flask 应用程序。
    此函数旨在作为 pipx 或其他脚本的入口点。

    参数:
        host (str): 绑定的 IP 地址。默认为 '0.0.0.0' (所有接口)。
        port (int): 监听的端口号。默认为 5000。
        root_dir (str, optional): 文件服务根目录的绝对路径。
                                  如果提供，将覆盖 .env 文件中的设置。
    """
    # 如果通过命令行提供了 root_dir，则覆盖配置中的值
    if root_dir:
        app.config['FILE_SERVER_ROOT_DIR'] = os.path.abspath(root_dir)
        print(f"使用指定的根目录: {app.config['FILE_SERVER_ROOT_DIR']}")

    # 在启动应用前，确保根目录存在
    if not os.path.exists(app.config['FILE_SERVER_ROOT_DIR']):
        try:
            os.makedirs(app.config['FILE_SERVER_ROOT_DIR'])
            print(f"已创建文件服务根目录: {app.config['FILE_SERVER_ROOT_DIR']}")
        except OSError as e:
            print(f"创建文件服务根目录 {app.config['FILE_SERVER_ROOT_DIR']} 失败: {e}")
            sys.exit(1)  # 如果目录创建失败，则退出程序

    print(f"AetherServe 正在 {host}:{port} 启动，文件根目录为: {app.config['FILE_SERVER_ROOT_DIR']}...")
    app.run(debug=True, host=host, port=port)  # 使用传递的 host 和 port 启动应用


# 保留原有的 if __name__ == '__main__': 块，以支持直接运行 app.py 进行开发测试
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='运行 AetherServe HTTP 文件服务器。')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='要绑定的主机 IP 地址。默认为 0.0.0.0 (所有接口)。')
    parser.add_argument('--port', type=int, default=5000,
                        help='要监听的端口号。默认为 5000。')
    parser.add_argument('--root-dir', type=str,
                        help='文件服务根目录的绝对路径。将覆盖 .env 文件中的设置。')
    args = parser.parse_args()

    run_server(host=args.host, port=args.port, root_dir=args.root_dir)  # 将解析到的参数传递给 run_server
