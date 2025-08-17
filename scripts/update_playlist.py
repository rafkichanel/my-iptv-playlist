import requests
import os
import re
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

MAIN_FILE = "Finalplay.m3u"
SOURCES_FILE = "sources.txt"
TIMEOUT = 10 # Timeout dalam detik untuk setiap permintaan

# Fungsi untuk memeriksa status channel
def check_channel(url, attempts=3):
    """
    Memeriksa apakah URL channel hidup dengan beberapa percobaan.
    """
    for attempt in range(attempts):
        try:
            r = requests.head(url, timeout=TIMEOUT)
            r.raise_for_status()
            return True
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError):
            continue
    return False

# --- Bagian Download dan Parsing ---
try:
    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        sources = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print(f"⚠️ Error: File '{SOURCES_FILE}' tidak ditemukan.")
    exit(1)

all_channels_to_check = []
for idx, url in enumerate(sources, start=1):
    try:
        print(f"📡 Mengunduh dari sumber {idx}: {url}")
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        lines = r.text.splitlines()

        # Filter: hapus baris yang mengandung 'WHATSAPP'
        lines = [line for line in lines if "WHATSAPP" not in line.upper()]

        # Filter: hilangkan ikon 🔴 dari sumber ke-3
        if idx == 3:
            lines = [line.replace("🔴", "") for line in lines]

        extinf_line = None
        for line in lines:
            line = line.strip()
            if line.startswith("#EXTINF"):
                extinf_line = line
            elif line and not line.startswith("#"):
                if extinf_line:
                    all_channels_to_check.append({
                        'extinf': extinf_line,
                        'url': line
                    })
                    extinf_line = None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Gagal ambil sumber {idx}: {e}")

# --- Bagian Filter Channel Mati ---
alive_channels = []
dead_count = 0
checked_count = 0

print("\n🔍 Memeriksa status setiap channel...")

with ThreadPoolExecutor(max_workers=50) as executor:
    future_to_channel = {executor.submit(check_channel, ch['url']): ch for ch in all_channels_to_check}
    
    for future in as_completed(future_to_channel):
        channel = future_to_channel[future]
        is_alive = future.result()
        checked_count += 1
        
        if is_alive:
            print(f"✅ Channel hidup: {channel['url']}")
            alive_channels.append(channel)
        else:
            print(f"⚠️ Channel mati: {channel['url']}")
            dead_count += 1

print("\n==========================")
print("📊 Statistik:")
print(f"🔢 Total channel: {checked_count}")
print(f"✅ Channel hidup: {len(alive_channels)}")
print(f"⚠️ Channel mati: {dead_count}")
print("==========================")

# --- Bagian Pengelompokan dan Penyusunan Ulang ---
live_event_channels = []
other_channels = []

for ch in alive_channels:
    if 'group-title="LIVE EVENT"' in ch['extinf'].upper() or 'group-title="SEDANG LIVE"' in ch['extinf'].upper():
        live_event_channels.append(ch)
    else:
        other_channels.append(ch)

# Ubah kategori "SEDANG LIVE" jadi "LIVE EVENT"
for ch in live_event_channels:
    ch['extinf'] = re.sub(r'group-title="SEDANG LIVE"', 'group-title="LIVE EVENT"', ch['extinf'], flags=re.IGNORECASE)

# Gabungkan kembali: LIVE EVENT di atas
final_playlist_content = ["#EXTM3U"]
for ch in live_event_channels:
    final_playlist_content.append(ch['extinf'])
    final_playlist_content.append(ch['url'])
for ch in other_channels:
    final_playlist_content.append(ch['extinf'])
    final_playlist_content.append(ch['url'])

# --- Bagian Penulisan File dan Git ---
try:
    with open(MAIN_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_playlist_content))
    print(f"✅ Playlist diperbarui dan disimpan ke {MAIN_FILE} - {datetime.utcnow().isoformat()} UTC")
except Exception as e:
    print(f"⚠️ Gagal menulis file: {e}")
    exit(1)

# Persiapan Git
os.system('git config --global user.email "actions@github.com"')
os.system('git config --global user.name "GitHub Actions"')

# Tambahkan file
subprocess.run(['git', 'add', MAIN_FILE], check=True)

# Cek apakah ada perubahan untuk di-commit
result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
if result.stdout:
    # Ada perubahan, lakukan commit dan push
    commit_msg = f"Update Finalplay.m3u - {datetime.utcnow().isoformat()} UTC"
    subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
    subprocess.run(['git', 'push'], check=True)
    print("✅ Commit & push berhasil")
else:
    print("⚠️ Tidak ada perubahan baru pada playlist, skip push.")

# Cetak link commit terbaru
try:
    repo = os.getenv("GITHUB_REPOSITORY", "rafkichanel/my-iptv-playlist")
    commit_hash = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    print(f"🔗 Lihat commit terbaru: https://github.com/{repo}/commit/{commit_hash}")
except subprocess.CalledProcessError:
    print("Gagal mengambil hash commit. Pastikan skrip berjalan di dalam repositori Git.")
              
