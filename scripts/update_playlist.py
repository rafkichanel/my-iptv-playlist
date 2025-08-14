import requests
import os
from datetime import datetime
import re

MAIN_FILE = "Finalplay.m3u"

# Baca daftar sumber dari sources.txt
if not os.path.exists("sources.txt"):
    print("❌ File sources.txt tidak ditemukan!")
    exit()

with open("sources.txt", "r", encoding="utf-8") as f:
    sources = [line.strip() for line in f if line.strip()]

if not sources:
    print("❌ Tidak ada URL sumber di sources.txt!")
    exit()

final_playlist = "#EXTM3U\n"

for url in sources:
    try:
        print(f"⬇️ Mengunduh dari {url}")
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        final_playlist += resp.text + "\n"
    except Exception as e:
        print(f"⚠️ Gagal ambil {url}: {e}")

# Ganti SEDANG LIVE → LIVE EVENT
final_playlist = final_playlist.replace("SEDANG LIVE", "LIVE EVENT")

# Hapus simbol 🔴
final_playlist = re.sub(r"🔴", "", final_playlist)

# Simpan file utama
with open(MAIN_FILE, "w", encoding="utf-8") as f:
    f.write(final_playlist)

# Simpan backup dengan timestamp
backup_file = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.m3u"
with open(backup_file, "w", encoding="utf-8") as f:
    f.write(final_playlist)

print(f"✅ Playlist berhasil disimpan ke {MAIN_FILE}")
print(f"📦 Backup disimpan ke {backup_file}")
