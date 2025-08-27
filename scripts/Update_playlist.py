import requests
import os
import re
from datetime import datetime

# Definisi file sumber dan file output
SOURCE_FILE_1 = "sources.txt"
OUTPUT_FILE_1 = "Finalplay.m3u"

SOURCE_FILE_2 = "sources2.txt"
OUTPUT_FILE_2 = "Finalplay2.m3u"

def process_playlist(source_file, output_file):
    """
    Mengunduh, memproses, dan menyimpan playlist dari file sumber.
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
                    # Filter untuk sumber pertama
                    lines = [line for line in lines if "WHATSAPP" not in line.upper()]
                    if idx == 3:
                        lines = [line.replace("🔴", "") for line in lines]
                    lines = [line for line in lines if 'group-title="SMA"' not in line]

                elif source_file == SOURCE_FILE_2:
                    # Filter untuk sumber kedua
                    lines = [line for line in lines if not re.search(r'group-title="00\.LIVE EVENT"', line, re.IGNORECASE)]
                    lines = [line for line in lines if not re.search(r'group-title="01\.CADANGAN LIVE EVENT"', line, re.IGNORECASE)]
                    lines = [line for line in lines if not re.search(r'group-title="Contact Admin"', line, re.IGNORECASE)]
                    # Menghapus semua baris yang berkaitan dengan Donasi
                    lines = [line for line in lines if 'DONASI UPDATE' not in line]

                # --- Logika penghapusan logo UNIVERSAL ---
                cleaned_lines = []
                for line in lines:
                    if line.startswith("#EXTINF"):
                        line = re.sub(r'tvg-logo="[^"]*"', '', line)
                        line = re.sub(r'group-logo="[^"]*"', '', line)
                        cleaned_lines.append(line)
                    else:
                        cleaned_lines.append(line)
                lines = cleaned_lines
                
                merged_lines.extend(lines)
            except Exception as e:
                print(f"⚠️ Gagal ambil sumber {idx} dari {source_file}: {e}")

        playlist_content = "\n".join(merged_lines)
        playlist_content = re.sub(r'group-title="SEDANG LIVE"', 'group-title="LIVE EVENT"', playlist_content, flags=re.IGNORECASE)

        lines = playlist_content.splitlines()
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
        
        final_playlist = ["#EXTM3U"]
        if source_file == SOURCE_FILE_2:
            WELCOME_MESSAGE = [
                "#EXTINF:-1 tvg-logo=\"https://raw.githubusercontent.com/tyo878787/my-iptv-playlist/refs/heads/tyo878787/IMG_20250807_103611.jpg\" group-title=\"00_Welcome RAFKI\", ðŸŽ‰ Selamat Datang di Playlist RAFKI ðŸŽ¶ | Nikmati hiburan terbaik & jangan lupa subscribe YouTube kami! ðŸ“º",
                "https://youtu.be/Lt5ubg_h53c?si=aPHoxL6wkKYnhQqr"
            ]
            final_playlist += WELCOME_MESSAGE
            
        final_playlist += live_event + other_channels

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(final_playlist))
        
        print(f"✅ Playlist diperbarui dan disimpan ke {output_file} - {datetime.utcnow().isoformat()} UTC")
        return True
    
    except FileNotFoundError:
        print(f"❗ File sumber tidak ditemukan: {source_file}")
        return False
    except Exception as e:
        print(f"❌ Terjadi kesalahan saat memproses {source_file}: {e}")
        return False

# --- Jalankan proses untuk kedua file ---
process_playlist(SOURCE_FILE_1, OUTPUT_FILE_1)
print("-" * 50)
process_playlist(SOURCE_FILE_2, OUTPUT_FILE_2)
print("-" * 50)

# --- Setup Git ---
os.system('git config --global user.email "actions@github.com"')
os.system('git config --global user.name "GitHub Actions"')
os.system(f'git add {OUTPUT_FILE_1} {OUTPUT_FILE_2}')

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
                
