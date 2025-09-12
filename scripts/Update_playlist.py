import requests
import re
from datetime import datetime

# File sumber dan output
SOURCE_FILE = "sources.txt"
OUTPUT_FILE = "playlist4.m3u"
GROUP_LOGO_URL = "https://raw.githubusercontent.com/rafkichanel/my-iptv-playlist/refs/heads/master/IMG_20250807_103611.jpg"

def process_playlist(source_file, output_file):
    try:
        with open(source_file, "r", encoding="utf-8") as f:
            sources = [line.strip() for line in f if line.strip()]

        merged_lines = []

        for idx, url in enumerate(sources, start=1):
            try:
                print(f"ðŸ”„ Mengunduh dari sumber {idx}: {url}")
                r = requests.get(url, timeout=15)
                r.raise_for_status()
                lines = r.text.splitlines()

                # Kata kunci yang ingin dihapus
                disallowed_words = ["DONASI", "UPDATE", "CADANGAN", "WHATSAPP", "CONTACT", "ADMIN"]

                processed_lines = []
                for line in lines:
                    line_upper = line.upper()
                    if any(word in line_upper for word in disallowed_words):
                        continue
                    if 'group-title="SMA"' in line:
                        continue
                    if 'group-title="LIVE EVENT"' in line:
                        continue
                    processed_lines.append(line)

                final_lines = []
                for line in processed_lines:
                    if line.startswith("#EXTINF"):
                        # Tambahkan group-logo Rafki tanpa menghapus logo channel
                        if 'group-logo="' not in line:
                            # Tambahkan group-logo sebelum tanda koma terakhir
                            parts = line.split(',', 1)
                            if len(parts) > 1:
                                new_line = parts[0] + f' group-logo="{GROUP_LOGO_URL}",' + parts[1]
                                line = new_line
                    final_lines.append(line)

                merged_lines.extend(final_lines)

            except Exception as e:
                print(f"âš ï¸ Gagal ambil sumber {idx}: {e}")

        final_playlist = ["#EXTM3U"] + [line for line in merged_lines if line.strip()]

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(final_playlist))

        print(f"âœ… Playlist berhasil disimpan di {output_file} - {datetime.utcnow().isoformat()} UTC")
        return True

    except FileNotFoundError:
        print(f"âš ï¸ File sumber tidak ditemukan: {source_file}")
        return False
    except Exception as e:
        print(f"âš ï¸ Terjadi kesalahan: {e}")
        return False

# --- Jalankan proses ---
process_playlist(SOURCE_FILE, OUTPUT_FILE)
        
