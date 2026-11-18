"""Jalankan: python tests/test_core.py  (butuh ffmpeg hanya untuk membuat file contoh)."""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import advisor, knowledge, media_probe  # noqa: E402

tmp = tempfile.mkdtemp()


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


land = os.path.join(tmp, "land.mp4")
vert = os.path.join(tmp, "vert.mp4")
mute = os.path.join(tmp, "mute.mp4")
song = os.path.join(tmp, "song.mp3")
ff("-f", "lavfi", "-i", "testsrc=s=1280x720:r=30:d=3", "-f", "lavfi", "-i", "sine=f=440:d=3:r=48000",
   "-c:v", "libx264", "-c:a", "aac", "-shortest", land)
ff("-f", "lavfi", "-i", "testsrc=s=1080x1920:r=25:d=2", "-f", "lavfi", "-i", "sine=f=440:d=2",
   "-c:v", "libx264", "-c:a", "aac", "-shortest", vert)
ff("-f", "lavfi", "-i", "testsrc=s=640x360:r=15:d=2", "-c:v", "libx264", mute)
ff("-f", "lavfi", "-i", "sine=f=440:d=4", "-b:a", "96k", song)

i = media_probe.probe(land)
assert (i["width"], i["height"], i["fps"], i["has_audio"]) == (1280, 720, 30.0, True), i
assert abs(i["duration"] - 3) < 0.2 and i["vcodec"] == "avc1" and i["sample_rate"] == 48000, i
j = media_probe.probe(vert)
assert (j["width"], j["height"], j["fps"]) == (1080, 1920, 25.0), j
k = media_probe.probe(mute)
assert k["has_audio"] is False and k["fps"] == 15.0, k
m = media_probe.probe(song)
assert m["kind"] == "audio" and abs(m["duration"] - 4) < 0.3, m
assert "error" in media_probe.probe(os.path.join(tmp, "nope.mp4"))

titles = lambda inf: [t for _, t, _ in advisor.review(inf)]
assert any("landscape" in t for t in titles(i)), titles(i)
assert any("Rasio 9:16" in t for t in titles(j)), titles(j)
assert any("Resolusi rendah" in t for t in titles(k)) and any("FPS rendah" in t for t in titles(k))
assert any("Tidak ada jalur audio" in t for t in titles(k))
assert knowledge.find_features("cara pakai keyframe zoom")[0]["name"].startswith("Keyframe")
assert "keyframe" in knowledge.answer_offline("apa itu keyframe?").lower()

print(media_probe.summary(i))
print(advisor.format_review(k))
print("SEMUA TES LULUS")
