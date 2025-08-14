import requests
from datetime import datetime
import os

# File output
OUTPUT_FILE = "Finalplay.m3u"

# Sumber playlist (bisa tambah lagi)
SOURCES = [
    "https://iptv-org.github.io/iptv/index.m3u",
    "https://raw.githubusercontent.com/rafkichanel/my-iptv-playlist/master/Playlist.m3u",
    "https://bit.ly/pengembarahitam"
]

def download_and_merge():
    merged_content = "#EXTM3U\n"
    for src in SOURCES:
        try:
            print(f"📥 Mengunduh dari: {src}")
            r = requests.get(src, timeout=15)
            r.raise_for_status()

            # Tambahkan header sumber
            merged_content += f"\n#\n# Sumber: {src}\n#\n"
            merged_content += r.text.strip() + "\n"
        except Exception as e:
            print(f"❌ Gagal mengambil {src}: {e}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(merged_content)
    print(f"✅ Playlist berhasil dibuat: {OUTPUT_FILE}")

if __name__ == "__main__":
    download_and_merge()

    # Commit otomatis jika di GitHub Actions
    if os.environ.get("GITHUB_ACTIONS") == "true":
        os.system("git config --global user.name 'GitHub Actions'")
        os.system("git config --global user.email 'actions@github.com'")
        os.system(f"git add {OUTPUT_FILE}")
        os.system(f"git commit -m 'Update Finalplay.m3u - {datetime.utcnow().isoformat()} UTC' || echo 'Tidak ada perubahan'")
        os.system("git push")
