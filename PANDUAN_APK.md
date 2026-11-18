# Cara mendapatkan APK tanpa terminal

APK dibangun otomatis di server GitHub (gratis), lalu kamu unduh dan pasang di HP. Semuanya lewat browser.
Paling mudah dilakukan dari **laptop/PC**. Dari HP, aktifkan "Situs desktop" di browser.

## A. Bangun APK (sekali saja, sekitar 20-40 menit)
1. Buat akun di github.com, lalu **New repository** > beri nama `capcut-coach` > **Public** > Create.
2. Ekstrak `capcut_coach.zip` di komputer. Di halaman repo: **Add file > Upload files**, lalu seret **isi** folder
   (bukan folder induknya): `main.py`, `llm.py`, `media_probe.py`, `advisor.py`, `knowledge.py`, `buildozer.spec`,
   `README.md`, folder `service`, dan folder `tests`. Klik **Commit changes**.
3. Folder `.github` sering tersembunyi sehingga tidak ikut terunggah. Buat manual:
   **Add file > Create new file**, ketik nama `.github/workflows/build-apk.yml`, tempel isi file
   dengan nama sama dari zip (atau isi di bawah), lalu **Commit changes**.
4. Buka tab **Actions**. Build berjalan otomatis; bila tidak, pilih **Build APK > Run workflow**.
5. Tunggu tanda centang hijau. Buka run tersebut, bagian **Artifacts** di bawah, unduh **CapCutCoach-APK**
   (berupa zip; ekstrak untuk mendapatkan file `.apk`).

```yaml
name: Build APK
on:
  workflow_dispatch:
  push:
    branches: [main, master]
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 90
    steps:
      - uses: actions/checkout@v4
      - name: Build APK dengan Buildozer
        id: buildozer
        uses: ArtemSBulgakov/buildozer-action@v1
        with:
          command: buildozer android debug
          buildozer_version: stable
      - name: Simpan APK
        uses: actions/upload-artifact@v4
        with:
          name: CapCutCoach-APK
          path: ${{ steps.buildozer.outputs.filename }}
```

## B. Pasang di HP
1. Pindahkan file `.apk` ke HP (Google Drive, kabel USB, atau unduh langsung di HP).
2. Ketuk file APK. Jika diminta, izinkan **Pasang dari sumber ini** untuk aplikasi yang kamu pakai membukanya.
3. Jika Play Protect memperingatkan (APK ini ditandatangani kunci debug, bukan dari Play Store), pilih **Install anyway**.
4. Buka **CapCut Coach AI**, izinkan akses media dan notifikasi.

## C. Pakai
Setelan > isi API key Anthropic > tekan **Bubble** > beri izin "Tampil di atas aplikasi lain" > tekan **Bubble** lagi > buka CapCut.

## Jika build gagal
Buka run yang merah di tab Actions, salin baris error terakhir, lalu kirim ke saya agar saya perbaiki.
Build pertama memang paling rawan gagal karena banyak komponen Android yang diunduh.
