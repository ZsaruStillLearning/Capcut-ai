"""CapCut Coach AI - aplikasi utama (Kivy). Jalan di desktop untuk uji, dan di Android via Buildozer."""
import json
import os
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.utils import escape_markup, platform

import advisor
import knowledge
import llm
import media_probe

KV = """
BoxLayout:
    orientation: 'vertical'
    padding: dp(8)
    spacing: dp(6)
    BoxLayout:
        size_hint_y: None
        height: dp(44)
        spacing: dp(6)
        Button:
            text: 'Video/Audio'
            on_release: app.pick('media')
        Button:
            text: 'Screenshot'
            on_release: app.pick('shot')
        Button:
            text: 'Bubble'
            on_release: app.toggle_bubble()
        Button:
            text: 'Setelan'
            on_release: app.open_settings()
    ScrollView:
        id: scroll
        GridLayout:
            id: chat
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(6)
            padding: dp(4)
    BoxLayout:
        size_hint_y: None
        height: dp(48)
        spacing: dp(6)
        TextInput:
            id: inp
            multiline: False
            hint_text: 'Tanya soal editing CapCut...'
            on_text_validate: app.send()
        Button:
            text: 'Kirim'
            size_hint_x: None
            width: dp(80)
            on_release: app.send()
"""

PERMS = ["android.permission.READ_EXTERNAL_STORAGE", "android.permission.READ_MEDIA_VIDEO",
         "android.permission.READ_MEDIA_AUDIO", "android.permission.READ_MEDIA_IMAGES",
         "android.permission.POST_NOTIFICATIONS"]


class Msg(Label):
    def __init__(self, text, **kw):
        super().__init__(text=text, markup=True, size_hint_y=None, halign="left", valign="top", **kw)
        self.bind(width=lambda *_: setattr(self, "text_size", (self.width - dp(12), None)))
        self.bind(texture_size=lambda *_: setattr(self, "height", self.texture_size[1] + dp(12)))


class CoachApp(App):
    title = "CapCut Coach AI"

    def build(self):
        self.history, self.media_report, self.image_path = [], "", None
        self.platform_goal, self.bubble_on = "short", False
        self.cfg = self._load_cfg()
        if platform == "android":
            from android.permissions import request_permissions
            request_permissions(PERMS)
        self.root_w = Builder.load_string(KV)
        self.say("Halo! Saya CapCut Coach. Pilih video/audio yang kamu edit, atau kirim screenshot timeline CapCut, "
                 "lalu tanya apa saja: fitur CapCut, cara bikin video lebih menarik, atau minta evaluasi.", "Coach")
        return self.root_w

    # ---------- util ----------
    def _cfg_path(self):
        return os.path.join(self.user_data_dir, "settings.json")

    def _load_cfg(self):
        try:
            with open(self._cfg_path()) as f:
                return json.load(f)
        except Exception:
            return {"api_key": "", "model": llm.DEFAULT_MODEL}

    def say(self, text, who):
        color = "5b8def" if who == "Kamu" else "2ecc71"
        self.root_w.ids.chat.add_widget(Msg("[b][color=%s]%s:[/color][/b] %s" % (color, who, escape_markup(text))))
        Clock.schedule_once(lambda *_: setattr(self.root_w.ids.scroll, "scroll_y", 0), 0.1)

    def ui(self, fn, *a):
        Clock.schedule_once(lambda *_: fn(*a), 0)

    # ---------- file picking ----------
    def pick(self, kind):
        from plyer import filechooser
        kw = {"on_selection": lambda sel: self.ui(self.on_picked, kind, sel), "multiple": False}
        if platform != "android":
            kw["filters"] = [("Media", "*.mp4", "*.mov", "*.m4a", "*.mp3", "*.wav")] if kind == "media" \
                else [("Gambar", "*.png", "*.jpg", "*.jpeg", "*.webp")]
        filechooser.open_file(**kw)

    def on_picked(self, kind, selection):
        if not selection:
            return
        path = selection[0]
        if kind == "shot":
            self.image_path = path
            self.say("Screenshot dimuat. Tanyakan sesuatu, mis. 'timeline-ku sudah bagus?'", "Coach")
            return
        info = media_probe.probe(path)
        self.media_report = media_probe.summary(info)
        self.say(advisor.format_review(info, self.platform_goal), "Coach")

    # ---------- chat ----------
    def send(self):
        inp = self.root_w.ids.inp
        text = inp.text.strip()
        if not text:
            return
        inp.text = ""
        self.say(text, "Kamu")
        img, self.image_path = self.image_path, None
        threading.Thread(target=self._answer, args=(text, img), daemon=True).start()

    def _answer(self, text, img):
        key = self.cfg.get("api_key", "")
        try:
            if not key:
                raise llm.LLMError("offline")
            reply = llm.Coach(key, self.cfg.get("model")).ask(self.history, text, self.media_report, img)
            self.history += [{"role": "user", "content": text}, {"role": "assistant", "content": reply}]
        except llm.LLMError as e:
            note = "" if str(e) == "offline" else "(%s) Menjawab dari basis pengetahuan offline.\n\n" % e
            reply = note + knowledge.answer_offline(text)
        self.ui(self.say, reply, "Coach")

    # ---------- settings ----------
    def open_settings(self):
        box = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        key = TextInput(text=self.cfg.get("api_key", ""), hint_text="API key Anthropic", password=True, multiline=False)
        model = TextInput(text=self.cfg.get("model", llm.DEFAULT_MODEL), multiline=False)
        save = Button(text="Simpan", size_hint_y=None, height=dp(44))
        for w in (Label(text="API key (kosong = mode offline)"), key, Label(text="Model"), model, save):
            box.add_widget(w)
        pop = Popup(title="Setelan", content=box, size_hint=(0.92, 0.6))

        def do_save(*_):
            self.cfg = {"api_key": key.text.strip(), "model": model.text.strip() or llm.DEFAULT_MODEL}
            os.makedirs(self.user_data_dir, exist_ok=True)
            with open(self._cfg_path(), "w") as f:
                json.dump(self.cfg, f)
            pop.dismiss()
        save.bind(on_release=do_save)
        pop.open()

    # ---------- floating bubble (Android) ----------
    def toggle_bubble(self):
        if platform != "android":
            self.say("Bubble hanya tersedia di Android.", "Coach")
            return
        from jnius import autoclass
        act = autoclass("org.kivy.android.PythonActivity").mActivity
        Settings = autoclass("android.provider.Settings")
        if not Settings.canDrawOverlays(act):
            Intent, Uri = autoclass("android.content.Intent"), autoclass("android.net.Uri")
            act.startActivity(Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                                     Uri.parse("package:" + act.getPackageName())))
            self.say("Aktifkan izin 'Tampil di atas aplikasi lain' untuk CapCut Coach, lalu tekan Bubble lagi.", "Coach")
            return
        svc = autoclass(str(act.getPackageName()) + ".ServiceBubble")
        if self.bubble_on:
            svc.stop(act)
            self.bubble_on = False
            self.say("Bubble dimatikan.", "Coach")
            return
        try:  # p4a baru: start(ctx, icon, judul, teks, argumen)
            svc.start(act, "icon", "CapCut Coach", "Bubble aktif", "")
        except Exception:  # p4a lama: start(ctx, argumen)
            svc.start(act, "")
        self.bubble_on = True
        self.say("Bubble aktif. Buka CapCut; ketuk bubble 'AI' untuk tips cepat.", "Coach")


if __name__ == "__main__":
    CoachApp().run()
