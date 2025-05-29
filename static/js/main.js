document.addEventListener('DOMContentLoaded', function() {
    // 通用的复制到剪贴板函数
    function copyToClipboard(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed'; // 防止滚动
        textarea.style.top = '0';
        textarea.style.left = '0';
        textarea.style.width = '2em';
        textarea.style.height = '2em';
        textarea.style.padding = '0';
        textarea.style.border = 'none';
        textarea.style.outline = 'none';
        textarea.style.boxShadow = 'none';
        textarea.style.background = 'transparent';
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        try {
            document.execCommand('copy');
            showToast('已复制到剪贴板！');
        } catch (err) {
            console.error('无法复制文本: ', err);
            // 可以在这里显示一个错误提示
        }
        document.body.removeChild(textarea);
    }

    // 显示 Toast 提示
    function showToast(message) {
        const toastEl = document.getElementById('copy-success-toast');
        if (toastEl) {
            const toastBody = toastEl.querySelector('.toast-body');
            toastBody.textContent = message;
            const toast = new bootstrap.Toast(toastEl);
            toast.show();
        }
    }

    // 绑定所有“复制链接”按钮的点击事件
    // 注意：类名从 copy-path-btn 更改为 copy-link-btn
    document.querySelectorAll('.copy-link-btn').forEach(button => {
        button.addEventListener('click', function() {
            const fullUrlToCopy = this.getAttribute('data-copy-url');
            copyToClipboard(fullUrlToCopy);
        });
    });

    // 实时搜索当前目录功能
    const fileSearchInput = document.getElementById('fileSearchInput');
    if (fileSearchInput) {
        fileSearchInput.addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            const table = document.getElementById('fileTable');
            const tr = table.getElementsByTagName('tr');

            for (let i = 1; i < tr.length; i++) { // 从第二行开始（跳过表头）
                const td = tr[i].getElementsByTagName('td')[0]; // 获取名称列
                if (td) {
                    const textValue = td.textContent || td.innerText;
                    if (textValue.toLowerCase().indexOf(filter) > -1) {
                        tr[i].style.display = "";
                    } else {
                        tr[i].style.display = "none";
                    }
                }
            }
        });
    }

    // 如果在预览页面，确保 Prism.js 高亮代码
    if (document.querySelector('pre code')) {
        Prism.highlightAll();
    }

    // 预览页面复制内容按钮事件 (如果存在)
    const copyContentBtn = document.getElementById('copyContentBtn');
    if (copyContentBtn) {
        copyContentBtn.addEventListener('click', function() {
            // 获取 data-content 属性的值
            const contentToCopy = this.getAttribute('data-content');
            copyToClipboard(contentToCopy);
        });
    }
});
