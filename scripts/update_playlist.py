import requests
import os
import re
from datetime import datetime

MAIN_FILE = "Finalplay.m3u"
SOURCES_FILE = "sources.txt"
ALT_SOURCES_FILE = "alt_sources.txt"

# Fungsi ambil playlist dari URL
def fetch_playlist(url):
    try:
        print(f"📡 Mengunduh: {url}")
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        lines = r.text.splitlines()

        # Filter: hapus WHATSAPP
        lines = [line for line in lines if "WHATSAPP" not in line.upper()]
        return lines
    except Exception as e:
        print(f"⚠️ Gagal ambil {url}: {e}")
        return []

# Baca daftar sumber utama
with open(SOURCES_FILE, "r", encoding="utf-8") as f:
    sources = [line.strip() for line in f if line.strip()]

# Baca daftar sumber alternatif
if os.path.exists(ALT_SOURCES_FILE):
    with open(ALT_SOURCES_FILE, "r", encoding="utf-8") as f:
        alt_sources = [line.strip() for line in f if line.strip()]
else:
    alt_sources = []

merged_lines = []

# Ambil dari sumber utama
for idx, url in enumerate(sources, start=1):
    lines = fetch_playlist(url)

    # Hapus ikon 🔴 untuk sumber ke-3
    if idx == 3:
        lines = [line.replace("🔴", "") for line in lines]

    if not lines and alt_sources:  # Jika gagal, coba alternatif
        for alt_url in alt_sources:
            alt_lines = fetch_playlist(alt_url)
            if alt_lines:
                print(f"✅ Menggunakan sumber alternatif: {alt_url}")
                lines = alt_lines
                break

    merged_lines.extend(lines)

# Gabungkan jadi satu string
playlist = "\n".join(merged_lines)

# Ubah kategori "SEDANG LIVE" jadi "LIVE EVENT"
playlist = re.sub(r'group-title="SEDANG LIVE"', 'group-title="LIVE EVENT"', playlist, flags=re.IGNORECASE)

# Pisahkan LIVE EVENT di atas
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

final_playlist = ["#EXTM3U"] + live_event + other_channels

# Simpan hasil
with open(MAIN_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(final_playlist))

print(f"✅ Playlist diperbarui dan disimpan ke {MAIN_FILE} - {datetime.utcnow().isoformat()} UTC")

# Git setup & commit
os.system('git config --global user.email "actions@github.com"')
os.system('git config --global user.name "GitHub Actions"')
os.system(f'git add {MAIN_FILE}')

commit_msg = f"Update Finalplay.m3u otomatis - {datetime.utcnow().isoformat()} UTC"
ret = os.system(f'git commit -m "{commit_msg}" || echo "Tidak ada perubahan"')
if ret == 0:
    os.system('git push')
    print("✅ Commit & push berhasil")
else:
    print("⚠️ Tidak ada perubahan baru, skip push")

# Cetak link commit terbaru
repo = os.getenv("GITHUB_REPOSITORY", "rafkichanel/my-iptv-playlist")
commit_hash = os.popen("git rev-parse HEAD").read().strip()
print(f"🔗 Lihat commit terbaru: https://github.com/{repo}/commit/{commit_hash}")
