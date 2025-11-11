# launcher.py — chạy Flask rồi mở trình duyệt ở chế độ fullscreen/kiosk
import os
import sys
import time
import subprocess
import threading
import webbrowser
from dotenv import load_dotenv

load_dotenv()
PORT = int(os.getenv("PORT", "5000"))
HOST = os.getenv("HOST", "127.0.0.1")
URL  = f"http://{HOST}:{PORT}/"

def run_flask():
    # chạy app.py trong cùng env
    return subprocess.Popen([sys.executable, "app.py"])

def open_kiosk(url):
    """
    Cố gắng mở trình duyệt ở chế độ kiosk/app.
    Ưu tiên Chrome/Edge; fallback: mở mặc định + nhắc nhấn F11.
    """
    try_variants = []

    if os.name == "nt":
        # Windows
        try_variants = [
            ["cmd", "/c", "start", "chrome", "--kiosk", url],
            ["cmd", "/c", "start", "msedge", "--kiosk", url],
        ]
    elif sys.platform == "darwin":
        # macOS
        try_variants = [
            ["open", "-a", "Google Chrome", "--args", "--kiosk", "--start-fullscreen", url],
            ["open", "-a", "Microsoft Edge", "--args", "--kiosk", url],
        ]
    else:
        # Linux
        try_variants = [
            ["bash", "-lc", f"google-chrome --kiosk '{url}' || chromium --kiosk '{url}' || brave-browser --kiosk '{url}'"],
        ]

    for cmd in try_variants:
        try:
            subprocess.Popen(cmd)
            return True
        except Exception:
            continue

    # Fallback: trình duyệt mặc định
    try:
        webbrowser.open(url, new=1, autoraise=True)
        print("⚠️ Không tìm thấy Chrome/Edge kiosk. Đã mở trình duyệt mặc định. Nhấn F11 để fullscreen.")
        return True
    except Exception:
        return False

if __name__ == "__main__":
    p = run_flask()
    # đợi server nổ cổng
    time.sleep(1.2)
    ok = open_kiosk(URL)
    if not ok:
        print(f"❌ Không mở được trình duyệt. Hãy tự truy cập: {URL}")
    # Giữ tiến trình chính cho đến khi Flask dừng
    try:
        p.wait()
    except KeyboardInterrupt:
        p.terminate()
