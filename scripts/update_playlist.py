import requests
import os
import re
from datetime import datetime

MAIN_FILE = "Finalplay.m3u"

# Baca daftar sumber dari sources.txt
with open("sources.txt", "r", encoding="utf-8") as f:
    sources = [line.strip() for line in f if line.strip()]

final_content = ""
for url in sources:
    try:
        print(f"Download dari {url}...")
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        lines = r.text.splitlines()

        # Ganti SEDANG LIVE jadi LIVE EVENT
        lines = [line.replace("SEDANG LIVE", "LIVE EVENT") for line in lines]

        # Filter hapus WHATSAPP
        lines = [line for line in lines if "WHATSAPP" not in line.upper()]

        final_content += "\n".join(lines) + "\n"
        print(f"Sukses dari {url}")
    except Exception as e:
        print(f"Gagal download dari {url}: {e}")

# Pisahkan kategori LIVE EVENT dan lainnya
live_event_block = []
other_block = []
lines = final_content.strip().splitlines()

current_block = []
is_live_event = False

for line in lines:
    if line.startswith("#EXTINF"):
        if "LIVE EVENT" in line.upper():
            is_live_event = True
        else:
            is_live_event = False
    if is_live_event:
        live_event_block.append(line)
    else:
        other_block.append(line)

# Gabungkan pasangan EXTINF + URL untuk LIVE EVENT
paired_events = []
for i in range(0, len(live_event_block), 2):
    try:
        extinf = live_event_block[i]
        url = live_event_block[i + 1]
    except IndexError:
        continue
    paired_events.append((extinf, url))

# Fungsi untuk ekstrak waktu dari nama channel
def extract_time(text):
    # Format jam HH:MM
    match_time = re.search(r"(\d{1,2}):(\d{2})", text)
    if match_time:
        try:
            now = datetime.now()
            hour, minute = int(match_time.group(1)), int(match_time.group(2))
            return datetime(now.year, now.month, now.day, hour, minute)
        except:
            return None
    # Format tanggal DD/MM/YYYY HH:MM
    match_datetime = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})[^\d]+(\d{1,2}):(\d{2})", text)
    if match_datetime:
        try:
            day, month, year, hour, minute = map(int, match_datetime.groups())
            return datetime(year, month, day, hour, minute)
        except:
            return None
    return None

# Urutkan LIVE EVENT berdasarkan waktu
paired_events.sort(key=lambda x: (extract_time(x[0]) or datetime.max))

# Susun ulang
sorted_live_event = []
for extinf, url in paired_events:
    sorted_live_event.append(extinf)
    sorted_live_event.append(url)

# Gabungkan final content (LIVE EVENT dulu, lalu lainnya)
final_result = "\n".join(sorted_live_event) + "\n" + "\n".join(other_block)

# Simpan ke file
with open(MAIN_FILE, "w", encoding="utf-8") as f:
    f.write(final_result.strip())

print(f"✅ Playlist tersimpan: {MAIN_FILE}")

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
