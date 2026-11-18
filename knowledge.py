"""Basis pengetahuan CapCut + playbook editing (bekerja offline).

Nama menu CapCut bisa berbeda antar versi/bahasa; selalu cek tombol di toolbar bawah.
"""

FEATURES = [
    {"name": "Split & Trim (Pisah/Potong)",
     "keys": ["split", "pisah", "potong", "trim", "cut", "gunting"],
     "what": "Memotong klip di posisi playhead, atau memangkas awal/akhir klip dengan menggeser tepinya.",
     "how": "Pilih klip, geser garis putih (playhead) ke titik potong, tekan Split. Untuk trim, tarik ujung klip.",
     "tip": "Buang jeda napas dan kata 'eee' agar ritme terasa rapat (jump cut)."},
    {"name": "Speed (Kecepatan) & Curve",
     "keys": ["speed", "kecepatan", "slow", "cepat", "curve", "ramp", "slowmo"],
     "what": "Mempercepat/memperlambat klip. Mode Curve mengatur kecepatan berubah di tengah klip (speed ramp).",
     "how": "Pilih klip > Speed > Normal untuk nilai tetap, atau Curve untuk preset/kustom dengan titik.",
     "tip": "Pakai slow-motion pada momen puncak (lompatan, reaksi), lalu kembali normal agar punya dinamika."},
    {"name": "Keyframe",
     "keys": ["keyframe", "key frame", "zoom", "gerak", "animasi manual", "pan"],
     "what": "Menyimpan nilai (posisi, skala, rotasi, opacity) pada titik waktu berbeda sehingga CapCut menganimasikan di antaranya.",
     "how": "Pilih klip, geser playhead, tekan ikon berlian untuk menambah keyframe; ubah posisi/skala, geser playhead, ubah lagi.",
     "tip": "Zoom pelan 100% ke 110% selama klip statis supaya tidak terasa membosankan."},
    {"name": "Mask (Masker)",
     "keys": ["mask", "masker", "reveal", "transisi mask"],
     "what": "Menampilkan sebagian area klip saja (bentuk linear, lingkaran, persegi, dsb.).",
     "how": "Pilih klip (biasanya di layer Overlay) > Mask > pilih bentuk, atur feather dan posisi.",
     "tip": "Kombinasikan mask + keyframe untuk efek 'wipe' atau teks yang muncul dari balik objek."},
    {"name": "Overlay & Picture-in-Picture",
     "keys": ["overlay", "pip", "picture in picture", "lapisan", "layer", "b-roll", "broll"],
     "what": "Menumpuk klip/gambar di atas video utama (b-roll, reaksi, logo, stiker).",
     "how": "Overlay > Add overlay > pilih media; atur ukuran dan posisi di preview.",
     "tip": "Tutup cut kasar dengan b-roll agar tidak terlihat patah."},
    {"name": "Chroma Key & Remove Background",
     "keys": ["chroma", "green screen", "greenscreen", "remove background", "hapus latar", "cutout", "bg"],
     "what": "Menghapus warna tertentu (green screen) atau memotong subjek dari latar secara otomatis.",
     "how": "Pilih klip overlay > Cutout (Chroma key / Auto cutout). Pada chroma key, pilih warna dengan color picker lalu atur Intensity/Shadow.",
     "tip": "Cahaya rata pada green screen jauh lebih menentukan hasil daripada slider apa pun."},
    {"name": "Auto Captions (Teks Otomatis)",
     "keys": ["caption", "subtitle", "teks otomatis", "auto caption", "terjemah", "takarir"],
     "what": "Mengenali suara lalu membuat teks sinkron di timeline.",
     "how": "Captions > Auto captions > pilih bahasa suara > Generate. Rapikan salah ketik, lalu atur gaya semua teks sekaligus.",
     "tip": "Maksimal 1-2 baris, font tebal, kontras tinggi, dan jauhkan dari area tombol platform di bawah/kanan layar."},
    {"name": "Text & Animasi Teks",
     "keys": ["text", "teks", "judul", "font", "tulisan", "title"],
     "what": "Menambah teks dengan font, warna, outline, bayangan, dan animasi masuk/keluar/loop.",
     "how": "Text > Add text. Atur Style, lalu tab Animations untuk In/Out/Loop.",
     "tip": "Tulis hook pada 1-3 detik pertama sebagai teks besar agar penonton paham topik tanpa suara."},
    {"name": "Transisi",
     "keys": ["transisi", "transition"],
     "what": "Efek perpindahan antar dua klip yang berdampingan.",
     "how": "Tekan ikon kotak kecil di antara dua klip > pilih transisi > atur durasi.",
     "tip": "Pakai satu jenis transisi konsisten; cut biasa sering lebih baik daripada transisi mencolok."},
    {"name": "Effects & Filter",
     "keys": ["effect", "efek", "filter", "glitch", "blur"],
     "what": "Effects menambah efek visual (video/body) sebagai layer; Filter mengubah warna secara cepat.",
     "how": "Effects > Video effects/Body effects > pilih, lalu atur durasi di timeline. Filters > pilih dan atur intensitas.",
     "tip": "Turunkan intensitas filter ke sekitar 50-70% supaya warna kulit tetap natural."},
    {"name": "Adjust (Color Grading)",
     "keys": ["adjust", "sesuaikan", "warna", "brightness", "kontras", "saturasi", "color grading", "hdr", "exposure"],
     "what": "Mengatur brightness, contrast, saturation, highlight, shadow, temperature, dll.",
     "how": "Pilih klip > Adjust, atau tambah layer Adjust dari toolbar agar berlaku pada beberapa klip sekaligus.",
     "tip": "Samakan eksposur dan white balance antar klip lebih dulu, baru beri 'look' dengan filter."},
    {"name": "Audio: Musik, Volume, Fade, Beats, Noise Reduction",
     "keys": ["audio", "musik", "music", "suara", "volume", "fade", "beat", "noise", "bising", "ekstrak", "extract", "voice"],
     "what": "Menambah musik/efek suara, mengatur volume, fade in/out, penanda beat, dan mengurangi noise.",
     "how": "Audio > Sounds/Extracted. Pilih klip audio > Volume, Fade, Beats (tandai beat), dan opsi Reduce noise bila tersedia.",
     "tip": "Suara bicara harus dominan; musik latar cukup sekitar 10-25% volume di bawah narasi."},
    {"name": "Freeze, Reverse, Stabilize",
     "keys": ["freeze", "bekukan", "reverse", "mundur", "stabilize", "stabil", "goyang", "shaky"],
     "what": "Freeze menahan satu frame; Reverse memutar mundur; Stabilize mengurangi guncangan.",
     "how": "Pilih klip > Freeze / Reverse / Stabilize di toolbar Edit.",
     "tip": "Freeze + teks/stiker di momen lucu adalah cara cepat menambah penekanan."},
    {"name": "Format, Canvas & Background",
     "keys": ["format", "rasio", "ratio", "canvas", "9:16", "16:9", "1:1", "background", "latar"],
     "what": "Mengatur rasio proyek dan latar (warna/blur) di balik video yang tidak memenuhi layar.",
     "how": "Format/Ratio > pilih 9:16, 1:1, 16:9, dll. Canvas > Background > Blur untuk mengisi sisi kosong.",
     "tip": "Pilih rasio dulu di awal proyek, bukan di akhir, supaya penataan teks tidak berantakan."},
    {"name": "Template",
     "keys": ["template", "templat"],
     "what": "Proyek siap pakai; kamu cukup mengganti media dengan klipmu.",
     "how": "Tab Template > pilih > Use template > pilih klip.",
     "tip": "Gunakan untuk belajar ritme potongan, lalu ubah supaya identitasmu tetap terlihat."},
    {"name": "Export (Resolusi, FPS, Kualitas)",
     "keys": ["export", "ekspor", "resolusi", "fps", "frame rate", "kualitas", "bitrate", "simpan", "render"],
     "what": "Mengatur resolusi, frame rate, dan (pada versi tertentu) bitrate/kodek hasil akhir.",
     "how": "Tombol Export di kanan atas > atur Resolution dan Frame rate > Export.",
     "tip": "Ekspor 1080p dengan FPS yang sama dengan footage aslinya; menaikkan FPS tidak menambah kehalusan."},
]

PLAYBOOK = [
    "Hook: 3 detik pertama harus menjawab 'kenapa aku harus lanjut nonton?' (hasil akhir, pertanyaan, atau momen paling menarik).",
    "Struktur ringkas: Hook, isi/nilai, lalu ajakan (CTA) atau ending yang memancing replay.",
    "Ritme: untuk video pendek, ganti visual (potong, zoom, b-roll) kira-kira tiap 2-4 detik.",
    "Buang jeda mati dan pengulangan; durasi yang lebih pendek hampir selalu lebih baik.",
    "Caption besar dan kontras di area aman, dan jangan menutup wajah atau tombol platform.",
    "Audio itu setengah video: suara jernih dulu, baru musik. Turunkan musik saat ada narasi.",
    "Sinkronkan potongan dengan beat musik (fitur Beats) supaya terasa 'nge-flow'.",
    "Konsisten: satu gaya font, satu palet warna, satu jenis transisi.",
    "Jangan menumpuk efek. Satu efek yang punya alasan lebih kuat daripada sepuluh efek dekoratif.",
    "Cek hasil di layar ponsel, tanpa suara dan dengan suara, sebelum upload.",
]


def find_features(query, limit=3):
    q = query.lower()
    scored = []
    for f in FEATURES:
        score = sum(1 for k in f["keys"] if k in q)
        if score:
            scored.append((score, f))
    scored.sort(key=lambda x: -x[0])
    return [f for _, f in scored[:limit]]


def explain(f):
    return ("%s\nFungsi: %s\nCara: %s\nTips: %s" % (f["name"], f["what"], f["how"], f["tip"]))


def feature_names():
    return [f["name"] for f in FEATURES]


def tip(i):
    return PLAYBOOK[i % len(PLAYBOOK)]


def answer_offline(query):
    found = find_features(query)
    if found:
        return "\n\n".join(explain(f) for f in found)
    return ("Mode offline: saya belum menemukan fitur yang cocok dengan pertanyaanmu.\n"
            "Coba sebut nama fitur (mis. keyframe, caption, speed, audio, export), atau isi API key di Setelan "
            "untuk jawaban AI penuh.\n\nTips umum: " + PLAYBOOK[0])
