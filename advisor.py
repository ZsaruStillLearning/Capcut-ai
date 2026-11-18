"""Evaluasi berbasis aturan: ubah hasil probe menjadi saran yang menyebut menu CapCut."""
import knowledge

PLATFORMS = {"short": "video pendek vertikal (TikTok/Reels/Shorts)",
             "long": "video panjang horizontal (YouTube)"}


def review(info, platform="short"):
    """Kembalikan list (level, judul, detail). level: OK / SARAN / PERBAIKI."""
    if info.get("error"):
        return [("PERBAIKI", "File tidak terbaca", info["error"])]
    out = []

    def add(level, title, detail):
        out.append((level, title, detail))

    w, h = info.get("width"), info.get("height")
    fps, dur, br = info.get("fps"), info.get("duration"), info.get("bitrate_kbps")

    if info.get("kind") == "video":
        if w and h:
            ratio = w / float(h)
            if platform == "short":
                if abs(ratio - 9 / 16.0) < 0.03:
                    add("OK", "Rasio 9:16", "Cocok untuk layar penuh di ponsel.")
                elif ratio > 1:
                    add("PERBAIKI", "Video landscape untuk platform vertikal (%dx%d)" % (w, h),
                        "Di CapCut: Format/Ratio > 9:16, lalu cubit klip sampai memenuhi layar, atau "
                        "Canvas > Background > Blur agar tidak ada bar hitam.")
                else:
                    add("SARAN", "Rasio %.2f bukan 9:16" % ratio, "Pertimbangkan Format/Ratio > 9:16.")
            elif ratio < 1:
                add("SARAN", "Video vertikal untuk platform horizontal", "Pertimbangkan Format/Ratio > 16:9 dan Canvas > Blur.")
            short = min(w, h)
            if short < 720:
                add("PERBAIKI", "Resolusi rendah (%dx%d)" % (w, h),
                    "Gunakan footage asli dari galeri, bukan hasil kiriman WhatsApp/unduhan; ekspor minimal 1080p.")
            elif short < 1080:
                add("SARAN", "Resolusi %dp" % short, "Cukup, tetapi 1080p memberi hasil lebih tajam setelah di-zoom/crop.")
            else:
                add("OK", "Resolusi %dp" % short, "Sudah bagus; zoom/crop masih punya ruang kualitas.")
        if fps:
            if fps < 24:
                add("PERBAIKI", "FPS rendah (%g)" % fps, "Gerakan akan patah-patah; cari sumber 24-30 fps atau lebih.")
            else:
                add("OK", "FPS %g" % fps, "Ekspor di Export > Frame rate yang sama dengan sumber; menaikkan FPS tidak menambah kehalusan. "
                    "Untuk slow-motion halus, rekam 60 fps.")
        if dur:
            if platform == "short" and dur > 60:
                add("SARAN", "Durasi %d detik" % dur, "Untuk video pendek, durasi 15-60 detik biasanya lebih kuat. Pangkas jeda dan pengulangan dengan Split/Trim.")
            elif dur < 3:
                add("SARAN", "Klip sangat pendek (%.1f dtk)" % dur, "Cocok sebagai potongan b-roll, bukan video utuh.")
        br_min = 3000 * (w * h) / (1920.0 * 1080) if (w and h) else 0
        if br and br_min and br < br_min:
            add("SARAN", "Bitrate rendah (~%.1f Mbps)" % (br / 1000.0),
                "Kemungkinan file sudah terkompresi berat. Ambil file asli untuk bahan editing, karena kompresi ulang di CapCut akan menurunkan kualitas lagi.")
        if not info.get("has_audio"):
            add("SARAN", "Tidak ada jalur audio", "Tambahkan musik/voice-over lewat Audio > Sounds; video bisu mudah di-skip.")
    if info.get("has_audio"):
        sr = info.get("sample_rate")
        if sr and sr < 44100:
            add("SARAN", "Sample rate audio %d Hz" % sr, "Di bawah 44,1 kHz; suara bisa terdengar 'tipis'. Pakai sumber audio lebih baik bila ada.")
        if info.get("kind") == "audio":
            if info.get("ext") == ".mp3" and br and br < 128:
                add("SARAN", "Bitrate MP3 %d kbps" % br, "Cukup rendah; cari versi 192-320 kbps agar tidak terdengar pecah.")
            add("OK", "Tips pakai audio ini di CapCut",
                "Audio > Beats untuk menandai beat, lalu potong klip tepat di tanda tersebut. Fade in/out di akhir agar tidak terpotong kasar.")
    if not out:
        add("SARAN", "Tidak ada temuan otomatis", "Kirim screenshot timeline untuk evaluasi lebih dalam.")
    return out


def format_review(info, platform="short"):
    lines = ["Evaluasi untuk %s:" % PLATFORMS.get(platform, platform)]
    for level, title, detail in review(info, platform):
        lines.append("[%s] %s: %s" % (level, title, detail))
    lines.append("")
    lines.append("Catatan: dari file saja saya tidak bisa menilai hook, ritme potongan, atau teks. "
                 "Kirim screenshot timeline atau ceritakan isi videonya.")
    return "\n".join(lines)
