import os
import json
import hashlib
import time
import threading
import webbrowser
import subprocess
from functools import lru_cache
from urllib.parse import urlparse

from flask import Flask, request, send_from_directory, jsonify, make_response
from flask_cors import CORS
import requests
from dotenv import load_dotenv

# ===== Load env =====
load_dotenv()
PORT = int(os.getenv("PORT", "5000"))
HOST = os.getenv("HOST", "127.0.0.1")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
WEB_DIR = os.path.join(ROOT_DIR, "web")

# ===== Flask app =====
app = Flask(__name__, static_folder="web", static_url_path="")
CORS(app)

# ===== Static routes =====
@app.get("/")
def index():
    f = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(f):
        return send_from_directory(WEB_DIR, "index.html")
    return ("Không tìm thấy web/index.html", 404)

@app.get("/app.html")
def app_html():
    f = os.path.join(WEB_DIR, "app.html")
    if os.path.exists(f):
        return send_from_directory(WEB_DIR, "app.html")
    return ("Không tìm thấy web/app.html", 404)

# Health & version
@app.get("/healthz")
def healthz():
    return jsonify({"ok": True, "uptime": time.time()})

@app.get("/version")
def version():
    return jsonify({"name": "dbp-web", "version": "1.0.0-python"})

# ===== Gemini config =====
TEXT_MODEL = "models/gemini-2.5-flash"         # giống server.js
TTS_MODEL  = "models/gemini-2.5-flash-tts"     # hiện chưa dùng, trả 501 để client fallback

def _sha1(obj) -> str:
    if isinstance(obj, (dict, list, tuple)):
        data = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    else:
        data = str(obj)
    return hashlib.sha1(data.encode("utf-8")).hexdigest()

# LRU cache giản đơn (dict + kích thước)
class LRU:
    def __init__(self, maxsize=200):
        self.max = maxsize
        self.map = {}

    def get(self, k):
        v = self.map.pop(k, None)
        if v is not None:
            # move to end
            self.map[k] = v
        return v

    def set(self, k, v):
        if k in self.map:
            self.map.pop(k, None)
        self.map[k] = v
        if len(self.map) > self.max:
            # pop first key
            old_k = next(iter(self.map.keys()))
            self.map.pop(old_k, None)

narr_cache = LRU(200)
tts_cache  = LRU(200)

# ===== Call Gemini REST =====
def gemini_generate(model_name: str, body: dict) -> dict:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set")
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "x-goog-api-key": GEMINI_API_KEY,
    }
    r = requests.post(url, headers=headers, json=body, timeout=30)
    if not r.ok:
        # cố gắng parse lỗi
        try:
            data = r.json()
        except Exception:
            data = {"raw": r.text}
        e = RuntimeError(f"Gemini HTTP {r.status_code}")
        e.status = r.status_code
        e.data = data
        raise e
    return r.json()

# ====== API: Narration text ======
@app.post("/api/narrate")
def api_narrate():
    try:
        data = request.get_json(force=True, silent=True) or {}
        event_id = data.get("eventId")
        event_title = data.get("eventTitle", "")
        event_desc = data.get("eventDesc", "")
        lang = data.get("lang", "vi")
        compact = bool(data.get("compact", True))
        if not event_id:
            return jsonify({"error": "Missing eventId"}), 400

        key = _sha1({"event_id": event_id, "lang": lang, "compact": compact})
        cached = narr_cache.get(key)
        if cached:
            return jsonify({"text": cached, "cached": True})

        prompt = "\n".join([
            f"Ngôn ngữ: {lang}.",
            "Viết đoạn thuyết minh ngắn gọn (2-3 câu), giọng thuyết minh lịch sử, dễ nghe." if compact
            else "Viết đoạn thuyết minh chi tiết (4-6 câu), truyền cảm mà rõ ràng.",
            f"Tiêu đề: {event_title}",
            f"Mô tả: {event_desc}",
            "Tránh liệt kê khô khan, nhấn mạnh ngày tháng & địa danh."
        ])

        out = gemini_generate(TEXT_MODEL, {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}]
        })
        parts = out.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        text = ""
        for p in parts:
            if "text" in p:
                text = p["text"]
                break
        if not text:
            return jsonify({"error": "Narration empty from model"}), 502

        narr_cache.set(key, text)
        return jsonify({"text": text})
    except Exception as e:
        code = getattr(e, "status", 500)
        msg = getattr(e, "data", {}).get("error", {}).get("message") if hasattr(e, "data") else str(e)
        print("[NARRATE ERROR]", code, msg)
        return jsonify({"error": msg}), code

# ====== API: TTS (trả 501 để client fallback Web Speech) ======
@app.post("/api/tts")
def api_tts():
    try:
        data = request.get_json(force=True, silent=True) or {}
        text = (data.get("text") or "").strip()
        lang = data.get("lang", "vi")
        voice_name = data.get("voiceName", "Kore")
        event_id = data.get("eventId", "ev")
        if not text:
            return make_response("Missing \"text\" for TTS", 400)

        key = _sha1({"event_id": event_id, "lang": lang, "voice": voice_name, "text": text})
        cached = tts_cache.get(key)
        if cached:
            resp = make_response(cached, 200)
            resp.headers["Content-Type"] = "audio/wav"
            return resp

        # Trả 501 như server.js để client (web/app.html) fallback sang Web Speech API
        return make_response("GEMINI_TTS_NOT_SUPPORTED_FOR_KEY", 501)

        # Nếu sau này có provider TTS thật:
        # - gọi API tạo audio, đặt mime (audio/wav hoặc audio/mpeg)
        # - tts_cache.set(key, audio_bytes); return audio bytes
    except Exception as e:
        code = getattr(e, "status", 500)
        print("[TTS ERROR]", code, e)
        return make_response(str(e), code)

# ===== Server start =====
def start_server():
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    start_server()
