import requests
import re
from datetime import datetime

# Definisi file sumber dan file output
SOURCE_FILE = "sources.txt"
OUTPUT_FILE = "playlist4.m3u"  # output baru
NEW_LOGO_URL = "https://raw.githubusercontent.com/rafkichanel/my-iptv-playlist/refs/heads/master/IMG_20250807_103611.jpg"

# Kategori yang ingin diberi logo Rafki
CATEGORIES_WITH_RAFKI_LOGO = ["00.LIVE EVENT"]  # bisa tambah kategori lain

def process_playlist(source_file, output_file):
    try:
        # Baca daftar sumber M3U
        with open(source_file, "r", encoding="utf-8") as f:
            sources = [line.strip() for line in f if line.strip()]

        merged_lines = []

        for idx, url in enumerate(sources, start=1):
            try:
                print(f"🔄 Mengunduh dari sumber {idx}: {url}")
                r = requests.get(url, timeout=15)
                r.raise_for_status()
                lines = r.text.splitlines()

                # Kata kunci yang tidak diinginkan
                disallowed_words = ["DONASI", "UPDATE", "CADANGAN", "WHATSAPP", "CONTACT", "ADMIN"]

                # Filter kata kunci dan kategori SMA / LIVE EVENT
                processed_lines = []
                for line in lines:
                    line_upper = line.upper()
                    if any(word in line_upper for word in disallowed_words):
                        continue
                    if 'group-title="SMA"' in line:
                        continue
                    processed_lines.append(line)

                # Tambahkan logo Rafki hanya untuk kategori tertentu
                final_lines = []
                for line in processed_lines:
                    if line.startswith("#EXTINF"):
                        match_group = re.search(r'group-title="([^"]+)"', line)
                        group_title = match_group.group(1) if match_group else ""

                        if group_title.upper() in CATEGORIES_WITH_RAFKI_LOGO:
                            # hapus logo lama
                            line = re.sub(r'tvg-logo="[^"]*"', '', line)
                            line = re.sub(r'group-logo="[^"]*"', '', line)
                            # tambahkan logo Rafki
                            new_tags = f' group-logo="{NEW_LOGO_URL}" tvg-logo="{NEW_LOGO_URL}"'
                            parts = line.split(',', 1)
                            if len(parts) > 1:
                                match = re.search(r'#EXTINF:(-1.*)', parts[0])
                                if match:
                                    attrs = match.group(1).strip()
                                    line = f'#EXTINF:{attrs}{new_tags},{parts[1].strip()}'
                    final_lines.append(line)

                merged_lines.extend(final_lines)

            except Exception as e:
                print(f"⚠️ Gagal ambil sumber {idx}: {e}")

        # Perbaiki nama grup LIVE EVENT
        playlist_content = "\n".join(merged_lines)
        playlist_content = re.sub(r'group-title="SEDANG LIVE"', 'group-title="LIVE EVENT"', playlist_content, flags=re.IGNORECASE)

        # Pisahkan LIVE EVENT biar tampil duluan
        lines = playlist_content.splitlines()
        live_event, other_channels, current_group = [], [], None
        for line in lines:
            if line.startswith("#EXTINF"):
                match = re.search(r'group-title="([^"]+)"', line)
                current_group = match.group(1) if match else None
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
        final_playlist = [line for line in final_playlist if line.strip()]  # hapus baris kosong

        # Simpan file
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

# --- Jalankan proses ---
process_playlist(SOURCE_FILE, OUTPUT_FILE)
