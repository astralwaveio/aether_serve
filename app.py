import os
from flask import Flask, render_template, request, send_from_directory, abort, jsonify
from config import Config
from utils import file_operations, search_utils

# 创建 Flask 应用实例
app = Flask(__name__)
# 从 Config 类加载配置
app.config.from_object(Config)


@app.errorhandler(404)
def page_not_found(e):
    """
    自定义 404 错误页面。
    """
    return render_template('error.html', error_code=404, error_message="文件或目录未找到。"), 404


@app.errorhandler(403)
def forbidden(e):
    """
    自定义 403 错误页面。
    """
    return render_template('error.html', error_code=403, error_message="禁止访问。"), 403


@app.errorhandler(500)
def internal_server_error(e):
    """
    自定义 500 错误页面。
    """
    return render_template('error.html', error_code=500, error_message="服务器内部错误。"), 500


@app.route('/')
@app.route('/browse/')
@app.route('/browse/<path:sub_path>')
def browse(sub_path=''):
    """
    浏览文件和文件夹的路由。
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
            base_url=request.url_root  # 传递 base_url 到模板
        )
    except FileNotFoundError:
        abort(404)  # 文件或目录未找到
    except ValueError:
        abort(403)  # 目录穿越尝试
    except Exception as e:
        app.logger.error(f"Error in browse route for path {sub_path}: {e}")
        abort(500)  # 服务器内部错误


@app.route('/preview/<path:file_path>')
def preview(file_path):
    """
    预览文件（文本或图片）的路由。
    """
    try:
        # 规范化路径
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
        abort(404)
    except ValueError:
        abort(403)
    except Exception as e:
        app.logger.error(f"Error in preview route for file {file_path}: {e}")
        abort(500)


@app.route('/download/<path:file_path>')
def download_file(file_path):
    """
    下载文件的路由。
    """
    try:
        # 规范化路径
        file_path = file_path.strip('/')
        absolute_file_path = file_operations._get_absolute_path(file_path)

        if not os.path.isfile(absolute_file_path):
            abort(404)

        # os.path.dirname(absolute_file_path) 是文件所在的目录
        # os.path.basename(absolute_file_path) 是文件名
        return send_from_directory(
            os.path.dirname(absolute_file_path),
            os.path.basename(absolute_file_path),
            as_attachment=True  # 强制下载
        )
    except FileNotFoundError:
        abort(404)
    except ValueError:
        abort(403)
    except Exception as e:
        app.logger.error(f"Error in download route for file {file_path}: {e}")
        abort(500)


@app.route('/serve_image/<path:image_path>')
def serve_image(image_path):
    """
    专门用于直接提供图片文件，不强制下载。
    """
    try:
        image_path = image_path.strip('/')
        absolute_image_path = file_operations._get_absolute_path(image_path)

        if not os.path.isfile(absolute_image_path):
            abort(404)

        # send_from_directory 会自动处理 MIME 类型
        return send_from_directory(
            os.path.dirname(absolute_image_path),
            os.path.basename(absolute_image_path),
            as_attachment=False  # 不强制下载
        )
    except FileNotFoundError:
        abort(404)
    except ValueError:
        abort(403)
    except Exception as e:
        app.logger.error(f"Error serving image {image_path}: {e}")
        abort(500)


@app.route('/search')
def search():
    """
    全局搜索文件的路由。
    """
    query = request.args.get('query', '').strip()
    results = []
    if query:
        try:
            results = search_utils.search_files_globally(query)
        except Exception as e:
            app.logger.error(f"Error during global search for query '{query}': {e}")
            # 可以选择返回一个错误信息给用户，或者直接返回空结果
            results = []

    return render_template('search_results.html', query=query, results=results,
                           base_url=request.url_root)  # 传递 base_url 到模板


# 如果直接运行此文件，则启动 Flask 开发服务器
if __name__ == '__main__':
    # 在启动应用前，确保根目录存在
    if not os.path.exists(app.config['FILE_SERVER_ROOT_DIR']):
        try:
            os.makedirs(app.config['FILE_SERVER_ROOT_DIR'])
            print(f"Created FILE_SERVER_ROOT_DIR: {app.config['FILE_SERVER_ROOT_DIR']}")
        except OSError as e:
            print(f"Error creating FILE_SERVER_ROOT_DIR {app.config['FILE_SERVER_ROOT_DIR']}: {e}")
            # 如果创建失败，可能需要更严格的错误处理或退出
            import sys

            sys.exit(1)  # 退出程序

    app.run(debug=True, host='0.0.0.0', port=5000)
