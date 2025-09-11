import requests
import re
from datetime import datetime

SOURCE_FILE = "sources.txt"      # daftar link m3u
OUTPUT_FILE = "Playlist_final.m3u" # hasil akhir
CATEGORIES_FILE = "categories.txt" # daftar kategori

NEW_LOGO_URL = "https://raw.githubusercontent.com/rafkichanel/my-iptv-playlist/refs/heads/master/IMG_20250807_103611.jpg"

def load_categories(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip().upper() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def process_playlist(source_file, output_file, categories):
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

                    # buang spam
                    if any(word in line_upper for word in disallowed_words):
                        continue

                    if line.startswith("#EXTINF"):
                        keep_channel = False
                        current_group = ""
                        current_channel_name = ""

                        # ambil group-title
                        match = re.search(r'group-title="([^"]+)"', line, flags=re.IGNORECASE)
                        if match:
                            current_group = match.group(1).upper()

                        # ambil nama channel
                        if "," in line:
                            current_channel_name = line.split(",", 1)[1].strip().upper()

                        # --- LOGIKA FILTER ---
                        if not categories:  # kalau categories.txt kosong → semua channel masuk
                            keep_channel = True
                        else:
                            for cat in categories:
                                if cat in current_group or cat in current_channel_name:
                                    keep_channel = True
                                    break

                        if keep_channel:
                            # hapus logo lama
                            line = re.sub(r'tvg-logo="[^"]*"', '', line)
                            line = re.sub(r'group-logo="[^"]*"', '', line)

                            # tambah logo baru
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

# --- Jalankan ---
categories = load_categories(CATEGORIES_FILE)
process_playlist(SOURCE_FILE, OUTPUT_FILE, categories)
