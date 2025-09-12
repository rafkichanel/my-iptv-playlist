import requests
import re
from datetime import datetime

# File sumber dan output
SOURCE_FILE = "sources.txt"
OUTPUT_FILE = "playlist4.m3u"
RAF_LOGO_URL = "https://raw.githubusercontent.com/rafkichanel/my-iptv-playlist/refs/heads/master/IMG_20250807_103611.jpg"

# Channel yang ingin dihapus di LIVE EVENT
REMOVE_CHANNELS_LIVE_EVENT = ["Reload Playlist", "Event 11"]

# Kategori yang ingin diganti logonya
CATEGORIES_WITH_RAFKI_LOGO = ["LIVE EVENT", "CHANNEL JAPAN"]

def process_playlist(source_file, output_file):
    try:
        with open(source_file, "r", encoding="utf-8") as f:
            sources = [line.strip() for line in f if line.strip()]

        merged_lines = []

        for idx, url in enumerate(sources, start=1):
            try:
                print(f"🔄 Mengunduh dari sumber {idx}: {url}")
                r = requests.get(url, timeout=15)
                r.raise_for_status()
                lines = r.text.splitlines()

                disallowed_words = ["DONASI", "UPDATE", "CADANGAN", "WHATSAPP", "CONTACT", "ADMIN"]
                processed_lines = []
                current_group = None

                for line in lines:
                    line_upper = line.upper()

                    # Hapus kata kunci yang tidak diinginkan
                    if any(word in line_upper for word in disallowed_words):
                        continue

                    # Deteksi kategori
                    if line.startswith("#EXTINF"):
                        match_group = re.search(r'group-title="([^"]+)"', line)
                        current_group = match_group.group(1).strip() if match_group else None

                        # Hapus channel tertentu hanya di LIVE EVENT
                        if current_group and current_group.upper() == "LIVE EVENT":
                            match_name = re.search(r'#EXTINF:.*?,(.*)', line)
                            channel_name = match_name.group(1).strip() if match_name else ""
                            if channel_name in REMOVE_CHANNELS_LIVE_EVENT:
                                continue

                        # Ganti logo Rafki untuk kategori yang diinginkan
                        if current_group and current_group.upper() in [cat.upper() for cat in CATEGORIES_WITH_RAFKI_LOGO]:
                            # Hapus logo lama di group-logo dan tvg-logo
                            line = re.sub(r'group-logo="[^"]*"', '', line)
                            line = re.sub(r'tvg-logo="[^"]*"', '', line)
                            # Tambahkan logo Rafki
                            parts = line.split(',', 1)
                            if len(parts) > 1:
                                line = parts[0] + f' group-logo="{RAF_LOGO_URL}" tvg-logo="{RAF_LOGO_URL}",' + parts[1]

                        # Hapus kategori SMA seperti sebelumnya
                        if 'group-title="SMA"' in line:
                            continue

                    processed_lines.append(line)

                merged_lines.extend(processed_lines)

            except Exception as e:
                print(f"⚠️ Gagal ambil sumber {idx}: {e}")

        final_playlist = ["#EXTM3U"] + [line for line in merged_lines if line.strip()]

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(final_playlist))

        print(f"✅ Playlist berhasil disimpan di {output_file} - {datetime.utcnow().isoformat()} UTC")
        return True

    except FileNotFoundError:
        print(f"⚠️ File sumber tidak ditemukan: {source_file}")
        return False
    except Exception as e:
        print(f"⚠️ Terjadi kesalahan: {e}")
        return False

# Jalankan proses
process_playlist(SOURCE_FILE, OUTPUT_FILE)
