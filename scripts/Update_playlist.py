import requests
import re
from datetime import datetime

# Definisi file sumber dan file output
SOURCE_FILE = "sources.txt"          # daftar sumber m3u
OUTPUT_FILE = "Playlist4.m3u"        # hasil akhir

# URL logo baru
NEW_LOGO_URL = "https://raw.githubusercontent.com/rafkichanel/my-iptv-playlist/refs/heads/master/IMG_20250807_103611.jpg"

# Kategori yang diperbolehkan
ALLOWED_CATEGORIES = ["SPORT", "INDONESIA"]

# Channel spesial yang selalu masuk
ALWAYS_INCLUDE = ["INDOSIAR"]

def process_playlist(source_file, output_file):
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

                disallowed_words = ["DONASI", "UPDATE", "CADANGAN", "WHATSAPP", "CONTACT", "ADMIN"]

                processed_lines = []
                current_group = None
                keep_channel = False
                current_channel_name = ""

                for line in lines:
                    line_upper = line.upper()

                    if any(word in line_upper for word in disallowed_words):
                        continue

                    if line.startswith("#EXTINF"):
                        match = re.search(r'group-title="([^"]+)"', line, flags=re.IGNORECASE)
                        current_group = match.group(1) if match else ""

                        current_channel_name = ""
                        if "," in line:
                            current_channel_name = line.split(",", 1)[1].strip().upper()

                        # ✅ aturan filter:
                        # 1. Masuk kalau kategori SPORT atau INDONESIA
                        # 2. Masuk kalau nama channel ada di ALWAYS_INCLUDE
                        if (any(cat in current_group.upper() for cat in ALLOWED_CATEGORIES)) or any(
                            inc in current_channel_name for inc in ALWAYS_INCLUDE
                        ):
                            keep_channel = True
                        else:
                            keep_channel = False

                        if keep_channel:
                            # hapus logo lama
                            line = re.sub(r'tvg-logo="[^"]*"', '', line)
                            line = re.sub(r'group-logo="[^"]*"', '', line)

                            # tambahkan logo baru
                            new_line_logo_tags = f' group-logo="{NEW_LOGO_URL}" tvg-logo="{NEW_LOGO_URL}"'
                            line_parts = line.split(',', 1)
                            if len(line_parts) > 1:
                                match2 = re.search(r'#EXTINF:(-1.*)', line_parts[0])
                                if match2:
                                    attributes = match2.group(1).strip()
                                    new_line = f'#EXTINF:{attributes}{new_line_logo_tags},{line_parts[1].strip()}'
                                    processed_lines.append(new_line)
                                else:
                                    processed_lines.append(line)
                            else:
                                processed_lines.append(line)
                    else:
                        if keep_channel:
                            processed_lines.append(line)

                merged_lines.extend(processed_lines)

            except Exception as e:
                print(f"⚠️ Gagal ambil sumber {idx} dari {source_file}: {e}")

        final_playlist = ["#EXTM3U"] + merged_lines
        final_playlist = [line for line in final_playlist if line.strip()]

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(final_playlist))

        print(f"✅ Playlist (INDONESIA + SPORT + Indosiar) disimpan ke {output_file} - {datetime.utcnow().isoformat()} UTC")
        return True

    except FileNotFoundError:
        print(f"❌ File sumber tidak ditemukan: {source_file}")
        return False
    except Exception as e:
        print(f"❌ Terjadi kesalahan saat memproses {source_file}: {e}")
        return False


# --- Jalankan proses ---
process_playlist(SOURCE_FILE, OUTPUT_FILE)
