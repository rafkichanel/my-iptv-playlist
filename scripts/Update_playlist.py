import requests
import os
import re
from datetime import datetime

# Definisi file sumber dan file output
SOURCE_FILE_1 = "sources.txt"
SOURCE_FILE_2 = "sources2.txt"
COMBINED_OUTPUT_FILE = "Finalplay.m3u"

def process_source_to_lines(source_file):
    """
    Mengunduh dan memproses playlist dari file sumber, mengembalikan daftar baris.
    """
    try:
        with open(source_file, "r", encoding="utf-8") as f:
            sources = [line.strip() for line in f if line.strip()]

        merged_lines = []
        for idx, url in enumerate(sources, start=1):
            try:
                print(f"📡 Mengunduh dari sumber {idx} ({source_file}): {url}")
                r = requests.get(url, timeout=15)
                r.raise_for_status()
                lines = r.text.splitlines()

                # --- Logika Pemfilteran ---
                if source_file == SOURCE_FILE_1:
                    lines = [line for line in lines if "WHATSAPP" not in line.upper()]
                    if idx == 3:
                        lines = [line.replace("🔴", "") for line in lines]
                    lines = [line for line in lines if 'group-title="SMA"' not in line]

                elif source_file == SOURCE_FILE_2:
                    lines = [line for line in lines if not re.search(r'group-title="00\.LIVE EVENT"', line, re.IGNORECASE)]
                    lines = [line for line in lines if not re.search(r'group-title="01\.CADANGAN LIVE EVENT"', line, re.IGNORECASE)]
                    lines = [line for line in lines if not re.search(r'group-title="Contact Admin"', line, re.IGNORECASE)]
                    lines = [line for line in lines if not re.search(r'\$\$\$\$\$\$ DONASI UPDATE \$\$\$\$\$\$', line, re.IGNORECASE)]

                merged_lines.extend(lines)
            except Exception as e:
                print(f"⚠️ Gagal ambil sumber {idx} dari {source_file}: {e}")
        
        return merged_lines
    
    except FileNotFoundError:
        print(f"❗ File sumber tidak ditemukan: {source_file}")
        return []
    except Exception as e:
        print(f"❌ Terjadi kesalahan saat memproses {source_file}: {e}")
        return []

# --- Jalankan proses untuk kedua file dan gabungkan ---
print("🚀 Memulai proses penggabungan playlist...")
lines_playlist1 = process_source_to_lines(SOURCE_FILE_1)
print("-" * 50)
lines_playlist2 = process_source_to_lines(SOURCE_FILE_2)

# Gabungkan konten
final_playlist = ["#EXTM3U"]

# Tambahkan konten dari playlist pertama
final_playlist.append("") # Baris kosong untuk pemisah
final_playlist.append("# Playlist Sumber Pertama")
final_playlist.extend(lines_playlist1)

# Tambahkan konten dari playlist kedua
final_playlist.append("") # Baris kosong untuk pemisah
# Pesan selamat datang
final_playlist.append("#EXTINF:-1 tvg-logo=\"https://raw.githubusercontent.com/tyo878787/my-iptv-playlist/refs/heads/tyo878787/IMG_20250807_103611.jpg\" group-title=\"00_Welcome RAFKI\", ðŸŽ‰ Selamat Datang di Playlist RAFKI ðŸŽ¶ | Nikmati hiburan terbaik & jangan lupa subscribe YouTube kami! ðŸ“º")
final_playlist.append("https://youtu.be/Lt5ubg_h53c?si=aPHoxL6wkKYnhQqr")
final_playlist.append("# Playlist Sumber Kedua")
final_playlist.extend(lines_playlist2)

# Simpan ke satu file
with open(COMBINED_OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(final_playlist))
    
print(f"✅ Playlist gabungan berhasil dibuat dan disimpan ke {COMBINED_OUTPUT_FILE} - {datetime.utcnow().isoformat()} UTC")

# --- Setup Git ---
os.system('git config --global user.email "actions@github.com"')
os.system('git config --global user.name "GitHub Actions"')
os.system(f'git add {COMBINED_OUTPUT_FILE}')

# Commit dengan safe exit code
commit_msg = f"Update playlists otomatis - {datetime.utcnow().isoformat()} UTC"
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
