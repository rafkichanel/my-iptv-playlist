import requests
import os
from datetime import datetime

MAIN_FILE = "Finalplay.m3u"

# Baca daftar sumber
with open("sources.txt", "r") as f:
    sources = [line.strip() for line in f if line.strip()]

# Download & gabungkan playlist
final_content = ""
for url in sources:
    try:
        print(f"Download dari {url}...")
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        lines = [line for line in r.text.splitlines() if "WHATSAPP" not in line.upper()]
        final_content += "\n".join(lines) + "\n"
        print(f"Sukses dari {url}")
    except Exception as e:
        print(f"Gagal download dari {url}: {e}")

# Simpan ke file lokal
with open(MAIN_FILE, "w", encoding="utf-8") as f:
    f.write(final_content.strip())
print(f"✅ Playlist tersimpan: {MAIN_FILE}")

# Commit & push ke GitHub
os.system('git config --global user.email "actions@github.com"')
os.system('git config --global user.name "GitHub Actions"')
os.system(f'git add {MAIN_FILE}')
commit_msg = f"Update Finalplay.m3u otomatis - {datetime.utcnow().isoformat()} UTC"
os.system(f'git commit -m "{commit_msg}" || echo "Tidak ada perubahan"')
os.system('git push')

# Cetak link commit terbaru
repo = os.getenv("GITHUB_REPOSITORY", "rafkichanel/my-iptv-playlist")
commit_hash = os.popen("git rev-parse HEAD").read().strip()
print(f"✅ Lihat commit: https://github.com/{repo}/commit/{commit_hash}")
