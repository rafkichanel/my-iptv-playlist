import requests
import re
from datetime import datetime

# Definisi file sumber dan file output
SOURCE_FILE = "sources.txt"          # daftar sumber m3u
OUTPUT_FILE = "Playlist4.m3u"        # hasil akhir
CATEGORY_FILE = "categories.txt"     # daftar kategori yang diperbolehkan

# URL logo baru
NEW_LOGO_URL = "https://raw.githubusercontent.com/rafkichanel/my-iptv-playlist/refs/heads/master/IMG_20250807_103611.jpg"

# --- Baca kategori dari file ---
try:
    with open(CATEGORY_FILE, "r", encoding="utf-8") as f:
        ALLOWED_CATEGORIES = [line.strip().upper() for line in f if line.strip()]
except FileNotFoundError:
    print(f"[ERROR] File kategori tidak ditemukan: {CATEGORY_FILE}")
    ALLOWED_CATEGORIES = []

def process_playlist(source_file, output_file):
    try:
        with open(source_file, "r", encoding="utf-8") as f:
            sources = [line.strip() for line in f if line.strip()]

        merged_lines = []
        total_channels = 0

        for idx, url in enumerate(sources, start=1):
            try:
                print(f"[INFO] Mengunduh dari sumber {idx}: {url}")
                r = requests.get(url, timeout=15)
                r.raise_for_status()
                lines = r.text.splitlines()

                disallowed_words = ["DONASI", "UPDATE", "CADANGAN", "WHATSAPP", "CONTACT", "ADMIN"]

                processed_lines = []
                keep_channel = False
                current_group = ""
                current_channel_name = ""

                for line in lines:
                    line_upper = line.upper()

                    # Skip kata terlarang
                    if any(word in line_upper for word in disallowed_words):
                        continue

                    if line.startswith("#EXTINF"):
                        match = re.search(r'group-title="([^"]+)"', line, flags=re.IGNORECASE)
                        current_group = match.group(1).upper() if match else ""
                        
                        current_channel_name = ""
                        if "," in line:
                            current_channel_name = line.split(",", 1)[1].strip().upper()

                        # === Filter fleksibel ===
                        keep_channel = False

                        # 1. Masuk kalau kategori cocok
                        if any(cat in current_group for cat in ALLOWED_CATEGORIES):
                            keep_channel = True

                        # 2. Masuk kalau nama channel mengandung kategori
                        for cat in ALLOWED_CATEGORIES:
                            if cat in current_channel_name:
                                keep_channel = True

                        if keep_channel:
                            # Hapus logo lama
                            line = re.sub(r'tvg-logo="[^"]*"', '', line)
                            line = re.sub(r'group-logo="[^"]*"', '', line)

                            # Tambahkan logo baru
                            line = re.sub(r'(#EXTINF:[^,]+)',
                                          rf'\1 group-logo="{NEW_LOGO_URL}" tvg-logo="{NEW_LOGO_URL}"',
                                          line)
                            processed_lines.append(line)
                            total_channels += 1
                    else:
                        if keep_channel:
                            processed_lines.append(line)

                merged_lines.extend(processed_lines)

            except Exception as e:
                print(f"[WARN] Gagal ambil sumber {idx}: {e}")

        # Buat playlist akhir
        final_playlist = ["#EXTM3U"] + merged_lines
        final_playlist = [line for line in final_playlist if line.strip()]

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(final_playlist))

        print(f"[SUCCESS] Playlist selesai ({total_channels} channel) disimpan ke {output_file} - {datetime.utcnow().isoformat()} UTC")
        return True

    except FileNotFoundError:
        print(f"[ERROR] File sumber tidak ditemukan: {source_file}")
        return False
    except Exception as e:
        print(f"[ERROR] Terjadi kesalahan saat memproses {source_file}: {e}")
        return False

# --- Jalankan proses ---
process_playlist(SOURCE_FILE, OUTPUT_FILE)
