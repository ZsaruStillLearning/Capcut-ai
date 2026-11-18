"""Klien LLM tipis (hanya stdlib + certifi). Model bisa diganti lewat Setelan."""
import base64
import json
import os
import ssl
import urllib.error
import urllib.request

import knowledge

try:
    import certifi
    _CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    _CTX = ssl.create_default_context()

API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-sonnet-5-5"
MAX_IMAGE_BYTES = 4 * 1024 * 1024

SYSTEM = """Kamu adalah "CapCut Coach", tutor dan asisten editing video yang ramah dan jujur untuk pemula.
Tugasmu: (1) memahami tujuan pengguna (platform, gaya, audiens), (2) mengevaluasi bahan yang mereka kirim,
(3) menjelaskan fitur CapCut langkah demi langkah, (4) mengajarkan KENAPA sebuah keputusan edit membuat video lebih menarik.

Aturan:
- Jawab dalam bahasa pengguna (default Bahasa Indonesia), ringkas, praktis, dan berurutan.
- Kamu TIDAK bisa melihat isi proyek CapCut secara langsung. Kamu hanya menerima (a) laporan analisis file media dan (b) screenshot yang dikirim pengguna.
  Jangan mengarang isi timeline. Bila informasi kurang, minta screenshot timeline atau deskripsi singkat.
- Sebut nama menu CapCut (Edit, Audio, Text, Overlay, Effects, Captions, Filters, Format, Adjust, Export) dan ingatkan bahwa nama menu bisa berbeda per versi.
- Beri maksimal 3-5 saran paling berdampak dahulu, urutkan dari yang paling penting, lalu tawarkan lanjutan.
- Jika pengguna menunjukkan masalah, jelaskan penyebabnya sebelum solusinya.
Fitur yang kamu kuasai: """ + "; ".join(knowledge.feature_names()) + "."


class LLMError(Exception):
    pass


def _image_block(path):
    if os.path.getsize(path) > MAX_IMAGE_BYTES:
        raise LLMError("Gambar terlalu besar (>4 MB). Pakai screenshot biasa, bukan foto resolusi penuh.")
    ext = os.path.splitext(path)[1].lower()
    media = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
             ".webp": "image/webp"}.get(ext)
    if not media:
        raise LLMError("Format gambar harus PNG/JPG/WEBP.")
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return {"type": "image", "source": {"type": "base64", "media_type": media, "data": data}}


class Coach:
    def __init__(self, api_key, model=DEFAULT_MODEL):
        self.api_key, self.model = api_key.strip(), (model or DEFAULT_MODEL).strip()

    def ask(self, history, text, media_report="", image_path=None):
        if not self.api_key:
            raise LLMError("API key belum diisi.")
        prompt = text
        if media_report:
            prompt = "[Laporan analisis file pengguna]\n%s\n\n[Pertanyaan]\n%s" % (media_report, text)
        content = [{"type": "text", "text": prompt}]
        if image_path:
            content.insert(0, _image_block(image_path))
        body = {"model": self.model, "max_tokens": 1000, "system": SYSTEM,
                "messages": list(history[-10:]) + [{"role": "user", "content": content}]}
        req = urllib.request.Request(
            API_URL, data=json.dumps(body).encode(), method="POST",
            headers={"content-type": "application/json", "x-api-key": self.api_key,
                     "anthropic-version": "2023-06-01"})
        try:
            with urllib.request.urlopen(req, timeout=60, context=_CTX) as r:
                data = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            msg = {401: "API key tidak valid.", 404: "Nama model tidak ditemukan; cek Setelan.",
                   429: "Terlalu banyak permintaan, coba lagi sebentar."}.get(e.code, "Server menolak (HTTP %d)." % e.code)
            raise LLMError(msg)
        except Exception as e:
            raise LLMError("Tidak bisa terhubung ke internet/API: %s" % e)
        return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()
