// server.js — ESM, REST Gemini (text) + TTS thật (WAV) với fallback, phục vụ thư mục web/
// Node 18+ (có fetch() built-in)

import express from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';
import path from 'path';
import crypto from 'crypto';
import fs from 'fs';
import { fileURLToPath } from 'url';

const PORT = 3000;
// ⚠️ Key bạn cung cấp — CHỈ dùng local, đừng commit public
const GEMINI_API_KEY = "AIzaSyArV7g_PhdHhkDDpiNYoDV213YiQS15WGg";

const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);
const ROOT_DIR   = path.join(__dirname, '..');      // .../project
const WEB_DIR    = path.join(ROOT_DIR, 'web');      // .../project/web

const app = express();
app.use(cors());
app.use(bodyParser.json({ limit: '1mb' }));

// Phục vụ static: gốc và thư mục web (để truy cập /assets,...)
app.use(express.static(ROOT_DIR));
app.use(express.static(WEB_DIR));

// Map "/" -> web/index.html (nếu không có thì báo rõ)
app.get('/', (req, res) => {
  const f = path.join(WEB_DIR, 'index.html');
  if (fs.existsSync(f)) return res.sendFile(f);
  res.status(404).send('Không tìm thấy web/index.html');
});

// Map "/app.html" -> web/app.html (để redirect không bị 404)
app.get('/app.html', (req, res) => {
  const f = path.join(WEB_DIR, 'app.html');
  if (fs.existsSync(f)) return res.sendFile(f);
  res.status(404).send('Không tìm thấy web/app.html');
});

// (tuỳ chọn) health check
app.get('/healthz', (req, res) => res.json({ ok: true }));

// ===== Cấu hình model =====
const TEXT_MODEL = 'models/gemini-2.5-flash';      // sinh thuyết minh (text)
// Dùng model TTS hỗ trợ trả audio:
const TTS_MODEL  = 'models/gemini-2.0-flash-tts';

// ===== Cache LRU đơn giản =====
function lru(max = 200) {
  const map = new Map();
  return {
    get(k){ if (!map.has(k)) return; const v=map.get(k); map.delete(k); map.set(k,v); return v; },
    set(k,v){ if (map.has(k)) map.delete(k); map.set(k,v); if (map.size>max){ const first=map.keys().next().value; map.delete(first);} }
  };
}
const narrCache = lru(200);
const ttsCache  = lru(200);
const hash = (obj) => crypto.createHash('sha1').update(JSON.stringify(obj)).digest('hex');

// ===== Gọi REST Gemini =====
async function geminiGenerate(modelName, body) {
  if (!GEMINI_API_KEY) {
    const err = new Error('Missing GEMINI_API_KEY');
    err.status = 500;
    throw err;
  }
  const url = `https://generativelanguage.googleapis.com/v1beta/${modelName}:generateContent`;
  const r = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json; charset=utf-8', 'x-goog-api-key': GEMINI_API_KEY },
    body: JSON.stringify(body)
  });
  if (!r.ok) {
    const txt = await r.text().catch(()=> '');
    const err = new Error(txt || `Gemini HTTP ${r.status}`);
    err.status = r.status;
    try { err.data = JSON.parse(txt); } catch {}
    throw err;
  }
  return r.json();
}

// ===== API Narration (text) =====
app.post('/api/narrate', async (req, res) => {
  try {
    const { eventId, eventTitle, eventDesc, lang='vi', compact=true } = req.body || {};
    if (!eventId) return res.status(400).json({ error: 'Missing eventId' });

    const key = hash({ eventId, lang, compact });
    const cached = narrCache.get(key);
    if (cached) return res.json({ text: cached, cached: true });

    const prompt = [
      `Ngôn ngữ: ${lang}.`,
      compact
        ? 'Viết đoạn thuyết minh ngắn gọn (2-3 câu), giọng thuyết minh lịch sử, dễ nghe.'
        : 'Viết đoạn thuyết minh chi tiết (4-6 câu), truyền cảm mà rõ ràng.',
      `Tiêu đề: ${eventTitle || ''}`,
      `Mô tả: ${eventDesc || ''}`,
      'Tránh liệt kê khô khan, nhấn mạnh ngày tháng & địa danh.'
    ].join('\n');

    const out = await geminiGenerate(TEXT_MODEL, {
      contents: [{ role:'user', parts:[{ text: prompt }]}]
    });

    const text = out?.candidates?.[0]?.content?.parts?.find(p => p.text)?.text || '';
    if (!text) return res.status(502).json({ error: 'Narration empty' });

    narrCache.set(key, text);
    res.json({ text });
  } catch (err) {
    const code = err?.status || 500;
    const msg  = err?.data?.error?.message || err?.message || 'Unknown narrate error';
    console.error('[NARRATE ERROR]', code, msg);
    res.status(code).json({ error: msg });
  }
});

// ===== API TTS (trả WAV). Nếu lỗi/không có quyền -> fallback 501 để client dùng Web Speech =====
app.post('/api/tts', async (req, res) => {
  try {
    const { text, lang='vi', voiceName='Kore', eventId='ev' } = req.body || {};
    if (!text || !text.trim()) return res.status(400).type('text/plain').send('Missing "text" for TTS');

    const key = hash({ eventId, lang, voiceName, text });
    const cached = ttsCache.get(key);
    if (cached) { res.set('Content-Type','audio/wav'); return res.send(cached); }

    // Thử gọi Gemini TTS thật (WAV)
    const body = {
      contents: [{ role: 'user', parts: [{ text }] }],
      generationConfig: { response_mime_type: 'audio/wav' }
      // Nếu muốn map voiceName -> voice params, hiện REST v1beta không nhận trực tiếp "voice" như một số SDK,
      // nên để model chọn giọng mặc định theo ngôn ngữ. (lang=vi sẽ ra tiếng Việt)
    };

    let out;
    try {
      out = await geminiGenerate(TTS_MODEL, body);
    } catch (e) {
      // Nếu lỗi do quyền/không hỗ trợ audio -> fallback 501 để client dùng Web Speech
      const m = (e?.data?.error?.message || e?.message || '').toLowerCase();
      const status = e?.status || 500;
      const notSupported =
        status === 400 || status === 403 || status === 501 ||
        /invalid_argument|not implemented|unsupported|response_mime_type/i.test(m);

      if (notSupported) {
        return res.status(501).type('text/plain').send('GEMINI_TTS_NOT_SUPPORTED_FOR_KEY');
      }
      throw e; // lỗi khác: trả về cho client biết
    }

    const part = out?.candidates?.[0]?.content?.parts?.find(p => p.inlineData?.data);
    const audioBase64 = part?.inlineData?.data;
    if (!audioBase64) {
      // Model trả về không có audio -> fallback Web Speech
      return res.status(501).type('text/plain').send('GEMINI_TTS_NOT_SUPPORTED_FOR_KEY');
    }

    const audioBuffer = Buffer.from(audioBase64, 'base64');
    ttsCache.set(key, audioBuffer);
    res.set('Content-Type', 'audio/wav');
    res.send(audioBuffer);

  } catch (err) {
    const code = err?.status || 500;
    const data = err?.data;
    const msg  = data?.error?.message || err?.message || 'Unknown TTS error';

    // Nếu có RetryInfo (429) -> set Retry-After
    const details = data?.error?.details;
    if (Array.isArray(details)) {
      const retry = details?.find(d => d['@type']?.includes('RetryInfo'));
      if (retry?.retryDelay) {
        const seconds = parseInt(String(retry.retryDelay).replace(/[^\d]/g,''), 10) || 10;
        res.set('Retry-After', String(seconds));
      }
    }
    console.error('[TTS ERROR]', code, data || msg);
    res.status(code).type('text/plain').send(msg);
  }
});

app.listen(PORT, () => {
  console.log(`✅ Server chạy tại: http://localhost:${PORT}`);
  console.log(`📁 Static root: ${ROOT_DIR}`);
  console.log(`📁 Web dir    : ${WEB_DIR}`);
});
