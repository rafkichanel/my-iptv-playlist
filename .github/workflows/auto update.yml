import requests
import os
import re
from datetime import datetime

MAIN_FILE = "Finalplay.m3u"
SOURCES_FILE = "sources.txt"

# Baca daftar sumber
with open(SOURCES_FILE, "r", encoding="utf-8") as f:
    sources = [line.strip() for line in f if line.strip()]

merged_lines = []
for idx, url in enumerate(sources, start=1):
    try:
        print(f"📡 Mengunduh dari sumber {idx}: {url}")
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        lines = r.text.splitlines()

        # Hilangkan ikon 🔴 di kategori SMA (misal sumber ke-3)
        if idx == 3:
            lines = [line.replace("🔴", "") for line in lines]

        merged_lines.extend(lines)
    except Exception as e:
        print(f"⚠️ Gagal ambil sumber {idx}: {e}")

# Gabung jadi satu string
playlist = "\n".join(merged_lines)

# Ubah kategori "SEDANG LIVE" jadi "LIVE EVENT"
playlist = re.sub(r'group-title="SEDANG LIVE"', 'group-title="LIVE EVENT"', playlist, flags=re.IGNORECASE)

# Pisahkan berdasarkan kategori
lines = playlist.splitlines()
live_event = []
other_channels = []
current_group = None

for line in lines:
    if line.startswith("#EXTINF"):
        match = re.search(r'group-title="([^"]+)"', line)
        if match:
            current_group = match.group(1)
        if current_group and current_group.upper() == "LIVE EVENT":
            live_event.append(line)
        else:
            other_channels.append(line)
    else:
        if current_group and current_group.upper() == "LIVE EVENT":
            live_event.append(line)
        else:
            other_channels.append(line)

# Gabungkan kembali: LIVE EVENT di atas
final_playlist = ["#EXTM3U"] + live_event + other_channels

# Simpan file utama
with open(MAIN_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(final_playlist))

print(f"✅ Playlist diperbarui dan disimpan ke {MAIN_FILE} - {datetime.utcnow().isoformat()} UTC")
