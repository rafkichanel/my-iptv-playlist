import requests
import os
import re
from datetime import datetime

# Definisi file sumber dan file output
SOURCE_PATH_1 = "sources.txt"
OUTPUT_PATH_1 = "Finalplay.m3u"

SOURCE_PATH_2 = "sources2.txt"
OUTPUT_PATH_2 = "Finalplay2.m3u"

def process_playlist(source_path, output_path):
    """
    Mengunduh, memproses, dan menyimpan playlist dari file sumber.
    """
    try:
        if not os.path.exists(source_path):
            print(f"❗ File sumber tidak ditemukan: {source_path}")
            return False

        with open(source_path, "r", encoding="utf-8") as f:
            sources = [line.strip() for line in f if line.strip()]

        if not sources:
            print(f"❗ File sumber {source_path} kosong. Tidak ada URL untuk diproses.")
            return False

        merged_lines = []
        for idx, url in enumerate(sources, start=1):
            try:
                print(f"📡 Mengunduh dari sumber {idx} ({source_path}): {url}")
                r = requests.get(url, timeout=15)
                r.raise_for_status()
                lines = r.text.splitlines()
                print(f"   -> Berhasil mengunduh {len(lines)} baris.")

                # --- Logika Pemfilteran ---
                initial_line_count = len(lines)
                if source_path == SOURCE_PATH_1:
                    lines = [line for line in lines if "WHATSAPP" not in line.upper()]
                    if idx == 3:
                        lines = [line.replace("🔴", "") for line in lines]
                    lines = [line for line in lines if 'group-title="SMA"' not in line]

                elif source_path == SOURCE_PATH_2:
                    lines = [line for line in lines if not re.search(r'group-title="00\.LIVE EVENT"', line, re.IGNORECASE)]
                    lines = [line for line in lines if not re.search(r'group-title="01\.CADANGAN LIVE EVENT"', line, re.IGNORECASE)]
                    lines = [line for line in lines if not re.search(r'group-title="Contact Admin"', line, re.IGNORECASE)]
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
                
                print(f"   -> Setelah filter, tersisa {len(lines)} baris.")
                merged_lines.extend(lines)

            except requests.exceptions.RequestException as e:
                print(f"⚠️ Gagal mengunduh URL {idx} dari {source_path}: {e}")
            except Exception as e:
                print(f"❌ Terjadi kesalahan saat memproses data dari {url}: {e}")
        
        # Cek jika playlist kosong sebelum melanjutkan
        if not merged_lines:
            print(f"❗ Tidak ada konten yang berhasil diunduh untuk {source_path}. Abort.")
            return False

        playlist_content = "\n".join(merged_lines)
        playlist_content = re.sub(r'group-title="SEDANG LIVE"', 'group-title="LIVE EVENT"', playlist_content, flags=re.IGNORECASE)

        lines = playlist_content.splitlines()
        live_event = []
        other_channels = []
        current_group = None

        for line in lines:
            if line.startswith("#EXTINF"):
                match = re.search(r'group-title="([^"]+)"', line)
                current_group = match.group(1).upper() if match else None
                
            if current_group == "LIVE EVENT":
                live_event.append(line)
            else:
                other_channels.append(line)
        
        final_playlist = ["#EXTM3U"]
        if source_path == SOURCE_PATH_2:
            WELCOME_MESSAGE = [
                "#EXTINF:-1 tvg-logo=\"https://raw.githubusercontent.com/tyo878787/my-iptv-playlist/refs/heads/tyo878787/IMG_20250807_103611.jpg\" group-title=\"00_Welcome RAFKI\", ðŸŽ‰ Selamat Datang di Playlist RAFKI ðŸŽ¶ | Nikmati hiburan terbaik & jangan lupa subscribe YouTube kami! ðŸ“º",
                "https://youtu.be/Lt5ubg_h53c?si=aPHoxL6wkKYnhQqr"
            ]
            final_playlist += WELCOME_MESSAGE
            
        final_playlist += live_event + other_channels

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(final_playlist))
        
        print(f"✅ Playlist diperbarui dan disimpan ke {output_path} - {datetime.utcnow().isoformat()} UTC")
        return True
    
    except FileNotFoundError:
        print(f"❗ File sumber tidak ditemukan: {source_path}")
        return False
    except Exception as e:
        print(f"❌ Terjadi kesalahan saat memproses {source_path}: {e}")
        return False

# --- Jalankan proses untuk kedua file ---
success1 = process_playlist(SOURCE_PATH_1, OUTPUT_PATH_1)
print("-" * 50)
success2 = process_playlist(SOURCE_PATH_2, OUTPUT_PATH_2)
print("-" * 50)

# --- Setup Git hanya jika ada perubahan ---
if success1 or success2:
    print("Mempersiapkan Git untuk commit...")
    os.system('git config --global user.email "actions@github.com"')
    os.system('git config --global user.name "GitHub Actions"')
    os.system(f'git add {OUTPUT_PATH_1} {OUTPUT_PATH_2}')

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

