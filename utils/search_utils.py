import os

from flask import current_app


def search_files_globally(keyword):
    """
    在 FILE_SERVER_ROOT_DIR 下全局搜索文件和文件夹。
    返回一个包含匹配项信息的列表。
    """
    root_dir = current_app.config['FILE_SERVER_ROOT_DIR']
    results = []
    keyword_lower = keyword.lower()

    # 遍历根目录下的所有文件和子目录
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 计算当前目录相对于根目录的相对路径
        relative_dirpath = os.path.relpath(dirpath, root_dir)
        # 如果相对路径是 '.'，表示根目录本身，将其设置为空字符串以便拼接 URL
        if relative_dirpath == '.':
            relative_dirpath = ''

        # 搜索文件夹名称
        for dirname in dirnames:
            if keyword_lower in dirname.lower():
                full_relative_path = os.path.join(relative_dirpath, dirname).replace('\\', '/') # 统一路径分隔符
                results.append({
                    'name': dirname,
                    'path': full_relative_path,
                    'is_dir': True
                })

        # 搜索文件名称
        for filename in filenames:
            if keyword_lower in filename.lower():
                full_relative_path = os.path.join(relative_dirpath, filename).replace('\\', '/') # 统一路径分隔符
                results.append({
                    'name': filename,
                    'path': full_relative_path,
                    'is_dir': False
                })
    return results
