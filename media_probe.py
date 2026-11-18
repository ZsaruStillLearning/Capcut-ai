"""Membaca metadata file media tanpa ffmpeg (aman untuk Android).

MP4/MOV/M4A: parser box ISO-BMFF sendiri. WAV: modul `wave`. MP3: `mutagen` bila ada.
"""
import os
import struct
import wave

VIDEO_EXT = {".mp4", ".mov", ".m4v", ".3gp"}
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".aac"}


def _boxes(f, start, end):
    pos = start
    while pos + 8 <= end:
        f.seek(pos)
        hdr = f.read(8)
        if len(hdr) < 8:
            return
        size, typ = struct.unpack(">I4s", hdr)
        hlen = 8
        if size == 1:
            size = struct.unpack(">Q", f.read(8))[0]
            hlen = 16
        elif size == 0:
            size = end - pos
        if size < hlen:
            return
        yield typ.decode("latin1"), pos + hlen, min(pos + size, end)
        pos += size


def _find(f, start, end, name):
    for t, s, e in _boxes(f, start, end):
        if t == name:
            return s, e
    return None


def _parse_track(f, s, e, info):
    tkhd = _find(f, s, e, "tkhd")
    mdia = _find(f, s, e, "mdia")
    if not mdia:
        return
    hdlr = _find(f, *mdia, "hdlr")
    if not hdlr:
        return
    f.seek(hdlr[0] + 8)
    kind = f.read(4).decode("latin1")
    mdhd = _find(f, *mdia, "mdhd")
    timescale = duration = 0
    if mdhd:
        f.seek(mdhd[0])
        ver = f.read(1)[0]
        f.seek(mdhd[0] + (20 if ver == 1 else 12))
        if ver == 1:
            timescale, duration = struct.unpack(">IQ", f.read(12))
        else:
            timescale, duration = struct.unpack(">II", f.read(8))
    minf = _find(f, *mdia, "minf")
    stbl = _find(f, *minf, "stbl") if minf else None
    stsd = _find(f, *stbl, "stsd") if stbl else None
    fourcc = ""
    if stsd:
        f.seek(stsd[0] + 12)
        fourcc = f.read(4).decode("latin1")

    if kind == "vide":
        info["vcodec"] = fourcc
        if tkhd:
            f.seek(tkhd[0])
            ver = f.read(1)[0]
            moff = 52 if ver == 1 else 40
            f.seek(tkhd[0] + moff)
            a, b = struct.unpack(">ii", f.read(8))
            f.seek(tkhd[0] + moff + 36)
            w, h = struct.unpack(">II", f.read(8))
            w, h = w >> 16, h >> 16
            if a == 0 and abs(b) == 0x10000:  # rotasi 90/270
                w, h = h, w
            info["width"], info["height"] = w, h
        if stbl and timescale:
            stts = _find(f, *stbl, "stts")
            if stts:
                f.seek(stts[0] + 4)
                n = struct.unpack(">I", f.read(4))[0]
                frames = ticks = 0
                for _ in range(min(n, 5000)):
                    c, d = struct.unpack(">II", f.read(8))
                    frames += c
                    ticks += c * d
                if ticks:
                    info["fps"] = round(frames * timescale / ticks, 2)
        if timescale and duration:
            info["duration"] = max(info.get("duration", 0), duration / timescale)
    elif kind == "soun":
        info["has_audio"] = True
        info["acodec"] = fourcc
        if stsd:
            f.seek(stsd[0] + 32)
            ch = struct.unpack(">H", f.read(2))[0]
            f.seek(stsd[0] + 40)
            sr = struct.unpack(">I", f.read(4))[0] >> 16
            info["channels"], info["sample_rate"] = ch, sr
        if timescale and duration and "duration" not in info:
            info["duration"] = duration / timescale


def _probe_mp4(path, info):
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        moov = _find(f, 0, size, "moov")
        if not moov:
            info["error"] = "Struktur MP4 tidak dikenali (atom 'moov' tidak ada/ file rusak)."
            return
        mvhd = _find(f, *moov, "mvhd")
        if mvhd:
            f.seek(mvhd[0])
            ver = f.read(1)[0]
            f.seek(mvhd[0] + (20 if ver == 1 else 12))
            ts, dur = struct.unpack(">IQ", f.read(12)) if ver == 1 else struct.unpack(">II", f.read(8))
            if ts:
                info["duration"] = dur / ts
        for t, s, e in _boxes(f, *moov):
            if t == "trak":
                _parse_track(f, s, e, info)
    info.setdefault("has_audio", False)


def _probe_wav(path, info):
    with wave.open(path, "rb") as w:
        info["sample_rate"], info["channels"] = w.getframerate(), w.getnchannels()
        info["duration"] = w.getnframes() / float(w.getframerate())
        info["has_audio"] = True


def _probe_mp3(path, info):
    try:
        from mutagen.mp3 import MP3
        m = MP3(path)
        info["duration"] = m.info.length
        info["sample_rate"] = m.info.sample_rate
        info["channels"] = m.info.channels
        info["bitrate_kbps"] = round(m.info.bitrate / 1000)
        info["has_audio"] = True
    except Exception as exc:  # mutagen tidak ada / file aneh
        info["note"] = "Detail MP3 tidak terbaca (%s)." % exc


def probe(path):
    ext = os.path.splitext(path)[1].lower()
    info = {"path": path, "name": os.path.basename(path), "ext": ext}
    if not os.path.isfile(path):
        info["error"] = "File tidak bisa dibuka. Coba pilih dari folder Download/DCIM."
        return info
    info["size_mb"] = round(os.path.getsize(path) / 1048576, 2)
    try:
        if ext in VIDEO_EXT or ext in {".m4a", ".aac"}:
            _probe_mp4(path, info)
            info["kind"] = "video" if "vcodec" in info else "audio"
        elif ext == ".wav":
            _probe_wav(path, info)
            info["kind"] = "audio"
        elif ext == ".mp3":
            _probe_mp3(path, info)
            info["kind"] = "audio"
        else:
            info["error"] = "Format %s belum didukung untuk analisis." % (ext or "?")
    except Exception as exc:
        info["error"] = "Gagal membaca file: %s" % exc
    d = info.get("duration")
    if d and "bitrate_kbps" not in info:
        info["bitrate_kbps"] = round(os.path.getsize(path) * 8 / 1000 / d)  # total, termasuk audio
    return info


def summary(info):
    if info.get("error"):
        return info["error"]
    p = ["%s (%s MB)" % (info["name"], info.get("size_mb", "?"))]
    d = info.get("duration")
    if d:
        p.append("durasi %d:%02d" % (d // 60, d % 60))
    if info.get("width"):
        p.append("%dx%d" % (info["width"], info["height"]))
    if info.get("fps"):
        p.append("%g fps" % info["fps"])
    if info.get("vcodec"):
        p.append("kodek video %s" % info["vcodec"])
    if info.get("bitrate_kbps"):
        p.append("~%.1f Mbps" % (info["bitrate_kbps"] / 1000))
    if info.get("has_audio"):
        p.append("audio %s %s Hz %s ch" % (info.get("acodec", ""), info.get("sample_rate", "?"), info.get("channels", "?")))
    elif info.get("kind") == "video":
        p.append("tanpa jalur audio")
    return ", ".join(p)
