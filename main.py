# PyWebview launcher

import webview
from app import create_app

app = create_app()

if __name__ == "__main__":
    webview.create_window("FSMP Automation Tool", app, width=1200, height=850)
    webview.start()