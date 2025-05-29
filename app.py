import argparse
import os
import sys

from flask import Flask, render_template, request, send_from_directory, abort

from config import Config
from utils import file_operations, search_utils

app = Flask(__name__)
app.config.from_object(Config)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message="文件或目录未找到。"), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error_code=403, error_message="禁止访问。"), 403


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, error_message="服务器内部错误。"), 500


@app.route('/')
@app.route('/browse/')
@app.route('/browse/<path:sub_path>')
def browse(sub_path=''):
    try:
        current_path = sub_path.strip('/')
        items = file_operations.list_directory(current_path)

        breadcrumbs = []
        if current_path:
            parts = current_path.split('/')
            for i in range(len(parts)):
                path_segment = '/'.join(parts[:i + 1])
                breadcrumbs.append({'name': parts[i], 'path': path_segment})

        parent_path = os.path.dirname(current_path)
        if parent_path == '/':
            parent_path = ''

        return render_template(
            'index.html',
            current_path=current_path,
            items=items,
            breadcrumbs=breadcrumbs,
            parent_path=parent_path,
            base_url=request.url_root
        )
    except FileNotFoundError:
        abort(404)
    except ValueError:
        abort(403)
    except Exception as e:
        app.logger.error(f"Error in browse route for path {sub_path}: {e}")
        abort(500)


@app.route('/preview/<path:file_path>')
def preview(file_path):
    try:
        file_path = file_path.strip('/')
        file_info = file_operations.get_file_info(file_path)

        if file_operations.is_text_file(file_path):
            content, is_truncated = file_operations.read_text_file(file_path)
            return render_template(
                'preview.html',
                file_path=file_path,
                file_name=file_info['name'],
                file_size=file_info['size'],
                content=content,
                is_truncated=is_truncated,
                base_url=request.url_root
            )
        elif file_operations.is_image_file(file_path):
            return render_template(
                'image_preview.html',
                file_path=file_path,
                file_name=file_info['name'],
                file_size=file_info['size'],
                base_url=request.url_root
            )
        else:
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
    try:
        file_path = file_path.strip('/')
        absolute_file_path = file_operations._get_absolute_path(file_path)

        if not os.path.isfile(absolute_file_path):
            abort(404)

        return send_from_directory(
            os.path.dirname(absolute_file_path),
            os.path.basename(absolute_file_path),
            as_attachment=True
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
    try:
        image_path = image_path.strip('/')
        absolute_image_path = file_operations._get_absolute_path(image_path)

        if not os.path.isfile(absolute_image_path):
            abort(404)

        return send_from_directory(
            os.path.dirname(absolute_image_path),
            os.path.basename(absolute_image_path),
            as_attachment=False
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
    query = request.args.get('query', '').strip()
    results = []
    if query:
        try:
            results = search_utils.search_files_globally(query)
        except Exception as e:
            app.logger.error(f"Error during global search for query '{query}': {e}")
            results = []

    return render_template('search_results.html', query=query, results=results, base_url=request.url_root)


def run_server(host='0.0.0.0', port=5000):
    """
    启动 AetherServe Flask 应用程序。此函数旨在作为 pipx 或其他脚本的入口点。
    """

    if not os.path.exists(app.config['FILE_SERVER_ROOT_DIR']):
        try:
            os.makedirs(app.config['FILE_SERVER_ROOT_DIR'])
            print(f"Created FILE_SERVER_ROOT_DIR: {app.config['FILE_SERVER_ROOT_DIR']}")
        except OSError as e:
            print(f"Error creating FILE_SERVER_ROOT_DIR {app.config['FILE_SERVER_ROOT_DIR']}: {e}")
            sys.exit(1)

    print(f"Starting AetherServe on {host}:{port}...")
    app.run(debug=True, host=host, port=port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run AetherServe HTTP File Server.')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='要绑定的主机IP地址。默认值为: 0.0.0.0 (所有接口)')
    parser.add_argument('--port', type=int, default=5000,
                        help='监听的端口号，默认是: 5000')
    args = parser.parse_args()

    run_server(host=args.host, port=args.port)
