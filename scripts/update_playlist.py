import requests
import os
from datetime import datetime

MAIN_FILE = "Finalplay.m3u"

# Baca daftar sumber dari sources.txt
with open("sources.txt", "r") as f:
    sources = [line.strip() for line in f if line.strip()]

final_content = ""
for idx, url in enumerate(sources, start=1):
    try:
        print(f"Download dari sumber {idx}: {url}")
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        lines = r.text.splitlines()

        # Filter hapus WHATSAPP
        lines = [line for line in lines if "WHATSAPP" not in line.upper()]

        # Modifikasi sumber ke-3 agar tidak ada SMA
        if idx == 3:
            mod_lines = []
            for line in lines:
                if "#EXTINF" in line and "SMA" in line.upper():
                    line = line.replace("SMA", "SMX")  # Ganti supaya beda
                mod_lines.append(line)
            lines = mod_lines

        # Gabungkan
        final_content += "\n".join(lines) + "\n"
        print(f"✅ Sukses ambil sumber {idx}")

    except Exception as e:
        print(f"❌ Gagal ambil sumber {idx}: {e}")

# Ganti kategori SEDANG LIVE -> LIVE EVENT
final_content = final_content.replace("SEDANG LIVE", "LIVE EVENT")

# Simpan hasil
with open(MAIN_FILE, "w", encoding="utf-8") as f:
    f.write(final_content.strip())

print(f"✅ Playlist tersimpan: {MAIN_FILE}")

# Git config
os.system('git config --global user.email "actions@github.com"')
os.system('git config --global user.name "GitHub Actions"')
os.system(f'git add {MAIN_FILE}')

# Commit & push
commit_msg = f"Update Finalplay.m3u otomatis - {datetime.utcnow().isoformat()} UTC"
ret = os.system(f'git commit -m "{commit_msg}" || echo "Tidak ada perubahan"')
if ret == 0:
    os.system('git push')
    print("✅ Commit & push berhasil")
else:
    print("⚠️ Tidak ada perubahan baru, skip push")

# Link commit terbaru
repo = os.getenv("GITHUB_REPOSITORY", "rafkichanel/my-iptv-playlist")
commit_hash = os.popen("git rev-parse HEAD").read().strip()
print(f"🔗 Lihat commit terbaru: https://github.com/{repo}/commit/{commit_hash}")
