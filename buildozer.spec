[app]
title = CapCut Coach AI
package.name = capcutcoach
package.domain = id.capcutcoach
source.dir = .
source.include_exts = py,png,jpg,kv,json
source.exclude_dirs = tests,bin,.buildozer
version = 0.1.0
requirements = python3,kivy==2.3.0,pyjnius,android,plyer,certifi,openssl,mutagen
orientation = portrait
fullscreen = 0

# Bubble = layanan foreground (service/bubble.py)
services = Bubble:service/bubble.py:foreground:sticky

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,READ_MEDIA_VIDEO,READ_MEDIA_AUDIO,READ_MEDIA_IMAGES,SYSTEM_ALERT_WINDOW,FOREGROUND_SERVICE,POST_NOTIFICATIONS
# API 33 dipilih agar foreground service tidak memerlukan 'foregroundServiceType' (wajib mulai API 34).
android.api = 33
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
