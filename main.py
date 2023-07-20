from docx_generator import docx_generator_main
from pywebio import start_server

if __name__ == '__main__':
    start_server(
        applications=[docx_generator_main,],
        debug=True,
        # 最大并发数
        # max_payload_size=1024 * 1024 * 1024,？
        # auto_open_webbrowser=True,
        remote_access=True,
        port=8080
    )