# CapCut Coach AI

Asisten + tutor editing CapCut berbentuk aplikasi Android (Python/Kivy) dengan bubble mengambang.

## Fitur
- **Chat tutor**: paham tujuan pengguna, menjelaskan fitur CapCut (split, speed/curve, keyframe, mask, overlay, chroma key, caption otomatis, teks, transisi, efek, color grading, audio/beats, freeze/reverse/stabilize, rasio/canvas, template, export) dan *kenapa* sebuah edit membuat video menarik.
- **Evaluasi file** MP4/MOV/M4A/MP3/WAV: durasi, resolusi, rasio, FPS, kodek, bitrate, audio, lalu saran yang menyebut menu CapCut.
- **Evaluasi screenshot timeline** CapCut (dikirim ke model AI dengan kemampuan gambar).
- **Bubble "AI"** yang bisa digeser di atas CapCut: tips cepat offline, tombol buka asisten.
- **Mode offline** (tanpa API key) memakai basis pengetahuan lokal. Dengan API key, jawaban penuh dari model Claude (nama model bisa diganti di Setelan).

## Batasan penting (jujur)
- CapCut **tidak punya API** dan file proyeknya (draft) disimpan di penyimpanan privat aplikasinya, jadi tidak bisa dibaca aplikasi lain tanpa root. Karena itu AI membaca **file media yang kamu pilih** dan **screenshot timeline** yang kamu kirim, bukan isi proyek secara langsung.
- Dari metadata file saja AI tidak bisa menilai hook, ritme, atau isi visual; itu dijawab lewat screenshot/deskripsimu.
- Bagian bubble (`service/bubble.py`) memakai pyjnius dan **belum diuji di perangkat Android** (tidak bisa dibangun di lingkungan pembuatnya). Logika inti (`media_probe`, `advisor`, `knowledge`) sudah diuji otomatis.

## Uji di komputer
```bash
pip install kivy plyer certifi mutagen
python main.py
python tests/test_core.py   # butuh ffmpeg untuk membuat file contoh
```

## Bangun APK (Linux/WSL/Colab)
```bash
pip install buildozer cython
buildozer -v android debug      # hasil: bin/*.apk
```
Pasang APK, lalu: buka **Setelan** > isi API key > tekan **Bubble** > beri izin "Tampil di atas aplikasi lain" > tekan **Bubble** lagi > buka CapCut.

## Struktur
| File | Fungsi |
|---|---|
| `main.py` | UI chat, pemilih file, setelan, tombol bubble |
| `llm.py` | Klien API (system prompt tutor, dukungan gambar) |
| `media_probe.py` | Pembaca metadata MP4/MOV/M4A/WAV/MP3 tanpa ffmpeg |
| `advisor.py` | Aturan evaluasi dan saran |
| `knowledge.py` | Penjelasan fitur CapCut + playbook editing |
| `service/bubble.py` | Bubble mengambang (foreground service) |

## Pengembangan lanjutan
Tangkap layar otomatis lewat MediaProjection saat bubble diketuk, analisis loudness/deteksi pergantian adegan, dan memakai model lain dengan menambah kelas klien di `llm.py`.
# Capcut-ai
# Capcut-ai
