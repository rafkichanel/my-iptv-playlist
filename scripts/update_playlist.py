import requests
import os
import re
from datetime import datetime

MAIN_FILE = "Finalplay.m3u"
SOURCES_FILE = "sources.txt"
ALT_SOURCES_FILE = "alt_sources.txt"

# Fungsi cek URL hybrid
def check_url(url):
    try:
        r = requests.head(url, timeout=3)
        if r.status_code < 400:
            return True
    except:
        pass
    try:
        r = requests.head(url, timeout=10)
        if r.status_code < 400:
            return True
    except:
        pass
    return False

# Ambil daftar sumber
def load_sources(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

sources = load_sources(SOURCES_FILE)
alt_sources = load_sources(ALT_SOURCES_FILE)

merged_lines = []
for idx, url in enumerate(sources, start=1):
    try:
        print(f"📡 Mengunduh dari sumber {idx}: {url}")
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        lines = r.text.splitlines()

        # Filter WHATSAPP
        lines = [line for line in lines if "WHATSAPP" not in line.upper()]

        # Hilangkan ikon 🔴 di sumber ke-3
        if idx == 3:
            lines = [line.replace("🔴", "") for line in lines]

        merged_lines.extend(lines)
    except Exception as e:
        print(f"⚠️ Gagal ambil sumber {idx}: {e}")
        if alt_sources:
            print("🔄 Coba alternatif...")
            for alt_url in alt_sources:
                try:
                    r = requests.get(alt_url, timeout=15)
                    r.raise_for_status()
                    merged_lines.extend(r.text.splitlines())
                    break
                except:
                    continue

# Filter channel mati pakai hybrid check
print("🔍 Mengecek channel mati...")
filtered_lines = []
last_extinf = None
for line in merged_lines:
    if line.startswith("#EXTINF"):
        last_extinf = line
    elif line.startswith("http"):
        if check_url(line):
            if last_extinf:
                filtered_lines.append(last_extinf)
            filtered_lines.append(line)
        last_extinf = None
    else:
        filtered_lines.append(line)

playlist = "\n".join(filtered_lines)

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

with open(MAIN_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(final_playlist))

print(f"✅ Playlist diperbarui dan disimpan ke {MAIN_FILE} - {datetime.utcnow().isoformat()} UTC")

# Setup Git
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

repo = os.getenv("GITHUB_REPOSITORY", "rafkichanel/my-iptv-playlist")
commit_hash = os.popen("git rev-parse HEAD").read().strip()
print(f"🔗 Lihat commit terbaru: https://github.com/{repo}/commit/{commit_hash}")
