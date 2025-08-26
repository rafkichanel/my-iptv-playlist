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
    # Kamus (dictionary) untuk pemfilteran sources2.txt
    # Gunakan kamus ini untuk memetakan URL ke kategori yang diizinkan.
    # Kategori akan dicocokkan tanpa memperhatikan huruf besar/kecil.
    source2_filters = {
        "bit.ly/MBois2025": ["Korean channels"],
        "bit.ly/45OH1zr": ["LIGA ARAB", "LIGA INGGRIS", "LIGA PRANCIS", "LIGA SPANYOL", "SERIE A ITALIA"],
        "s.id/andi7153": ["LIVE FORMULA 1", "LIVE | LALIGA", "LIVE | MotoGP", "LIVE | PROLIGA", "LIVE | TIMNAS", "LIVE | UCL", "LIVE VOLLY VNL"]
    }
    
    # Daftar kategori yang akan dihapus secara default untuk sources2.txt
    # Kategori akan dicocokkan tanpa memperhatikan huruf besar/kecil.
    source2_categories_to_remove = [
        "00.LIVE EVENT",
        "01.CADANGAN LIVE EVENT",
        "Contact Admin",
        "WELCOME RAFKI" # Tambahkan filter ini untuk memastikan tidak ada duplikasi
    ]
    
    # URL data SVG untuk logo play
    PLAY_LOGO_SVG = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZD0iTTggNXYxNGwxMS03eiIgZmlsbD0iI2ZmZmZmZiIvPjwvc3ZnPg=="

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
                    # Filter untuk sources.txt: hanya menghapus channel "WHATSAPP" dan emoji 🔴
                    lines = [line for line in lines if "WHATSAPP" not in line.upper()]
                    if idx == 3:
                        lines = [line.replace("🔴", "") for line in lines]

                elif source_file == SOURCE_FILE_2:
                    # Ambil daftar kategori yang diizinkan dari kamus
                    allowed_categories = source2_filters.get(url, [])
                    if allowed_categories:
                        print(f"✅ Filter aktif untuk URL ini. Kategori yang diizinkan: {allowed_categories}")
                        new_lines = []
                        next_line_is_channel = False
                        allowed_categories_lower = [cat.lower() for cat in allowed_categories]
                        for line in lines:
                            if line.startswith("#EXTINF"):
                                match = re.search(r'group-title="([^"]+)"', line, re.IGNORECASE)
                                if match and match.group(1).strip().lower() in allowed_categories_lower:
                                    # Mengganti logo "SMA" dan "MBOIS" dengan logo play hanya jika kategori cocok
                                    line = re.sub(r'tvg-logo="[^"]*(sma|s.m.a|mbois)[^"]*"', f'tvg-logo="{PLAY_LOGO_SVG}"', line, flags=re.IGNORECASE)
                                    new_lines.append(line)
                                    next_line_is_channel = True
                                else:
                                    next_line_is_channel = False
                            elif next_line_is_channel and line.startswith("http"):
                                new_lines.append(line)
                                next_line_is_channel = False
                        lines = new_lines
                    else:
                        print("❗ URL tidak terdaftar di filter. Menggunakan filter standar.")
                        
                        # Buat regex untuk kategori yang akan dihapus
                        remove_pattern = '|'.join([re.escape(cat) for cat in source2_categories_to_remove])
                        
                        new_lines = []
                        next_line_is_channel = False
                        for line in lines:
                            if line.startswith("#EXTINF"):
                                match = re.search(r'group-title="([^"]+)"', line, re.IGNORECASE)
                                if match and re.search(remove_pattern, match.group(1), re.IGNORECASE):
                                    next_line_is_channel = False
                                else:
                                    new_lines.append(line)
                                    next_line_is_channel = True
                            elif next_line_is_channel and line.startswith("http"):
                                new_lines.append(line)
                                next_line_is_channel = False
                        lines = new_lines

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

