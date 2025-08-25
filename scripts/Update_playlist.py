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
                    # Filter untuk Finalplay.m3u
                    lines = [line for line in lines if "WHATSAPP" not in line.upper()]
                    if idx == 3:
                        lines = [line.replace("🔴", "") for line in lines]
                elif source_file == SOURCE_FILE_2:
                    # Filter khusus untuk Finalplay2.m3u
                    filtered_lines = []
                    skip_next_line = False
                    for line in lines:
                        if "group-title=\"00.LIVE EVENT\"" in line or \
                           "group-title=\"01.CADANGAN LIVE EVENT\"" in line or \
                           "group-title=\"Contact Admin\"" in line:
                            skip_next_line = True
                            continue
                        if skip_next_line and line.startswith("http"):
                            skip_next_line = False
                            continue
                        if not skip_next_line:
                            filtered_lines.append(line)
                    lines = filtered_lines
                
                merged_lines.extend(lines)
            except Exception as e:
                print(f"⚠️ Gagal ambil sumber {idx} dari {source_file}: {e}")

        # Gabung jadi satu string
        playlist_content = "\n".join(merged_lines)
        playlist_content = re.sub(r'group-title="SEDANG LIVE"', 'group-title="LIVE EVENT"', playlist_content, flags=re.IGNORECASE)

        # Pisahkan berdasarkan kategori untuk menempatkan 'LIVE EVENT' di atas
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
        
        final_playlist = ["#EXTM3U"] + live_event + other_channels

        # Simpan file
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
