import requests
import re
from datetime import datetime

SOURCE_FILE = "sources.txt"
OUTPUT_FILE = "Playlist4.m3u"
CATEGORY_LOGO = "https://raw.githubusercontent.com/rafkichanel/my-iptv-playlist/refs/heads/master/IMG_20250807_103611.jpg"
LOGO_BASE_URL = "https://raw.githubusercontent.com/rafkichanel/my-iptv-playlist/master/logos/"

def sanitize_channel_name(name):
    # Hapus karakter khusus untuk membuat URL
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name.strip())

def logo_exists(url):
    # Cek apakah file logo ada (status_code 200)
    try:
        r = requests.head(url, timeout=5)
        return r.status_code == 200
    except:
        return False

def process_playlist(source_file, output_file):
    try:
        with open(source_file, "r", encoding="utf-8") as f:
            sources = [line.strip() for line in f if line.strip()]

        merged_lines = []

        for idx, url in enumerate(sources, start=1):
            try:
                print(f"📡 Mengunduh dari sumber {idx}: {url}")
                r = requests.get(url, timeout=15)
                r.raise_for_status()
                lines = r.text.splitlines()

                disallowed_words = ["DONASI", "UPDATE", "CADANGAN", "WHATSAPP", "CONTACT", "ADMIN"]

                processed_lines = []
                current_group = None

                for line in lines:
                    line_upper = line.upper()
                    if any(word in line_upper for word in disallowed_words):
                        continue
                    if line.startswith("#EXTINF") and 'group-title="00.LIVE EVENT"' in line:
                        continue
                    if 'group-title="SMA"' in line:
                        continue

                    if line.startswith("#EXTINF"):
                        # Deteksi group-title
                        match_group = re.search(r'group-title="([^"]+)"', line)
                        if match_group:
                            current_group = match_group.group(1)
                            # Tambahkan logo kategori
                            line = re.sub(r'group-logo="[^"]*"', '', line)
                            line = re.sub(r'tvg-logo="[^"]*"', '', line)
                            group_logo_tags = f' group-logo="{CATEGORY_LOGO}"'
                            line_parts = line.split(',', 1)
                            if len(line_parts) > 1:
                                attributes = re.search(r'#EXTINF:(-1.*)', line_parts[0]).group(1).strip()
                                line = f'#EXTINF:{attributes}{group_logo_tags},{line_parts[1].strip()}'

                        # Tambahkan logo channel jika ada
                        line_parts = line.split(',', 1)
                        if len(line_parts) > 1:
                            channel_name = line_parts[1].strip()
                            sanitized_name = sanitize_channel_name(channel_name)
                            channel_logo_url = f"{LOGO_BASE_URL}{sanitized_name}.jpg"
                            if logo_exists(channel_logo_url):
                                # Hapus tvg-logo lama
                                line = re.sub(r'tvg-logo="[^"]*"', '', line)
                                line = line.replace(',', f' tvg-logo="{channel_logo_url}",', 1)
                            else:
                                # Hapus jika tidak ada logo
                                line = re.sub(r'tvg-logo="[^"]*"', '', line)

                    processed_lines.append(line)

                merged_lines.extend(processed_lines)

            except Exception as e:
                print(f"⚠ Gagal ambil sumber {idx}: {e}")

        # Normalisasi nama grup
        playlist_content = "\n".join(merged_lines)
        playlist_content = re.sub(
            r'group-title="SEDANG LIVE"', 'group-title="LIVE EVENT"', playlist_content, flags=re.IGNORECASE
        )

        # Pisahkan LIVE EVENT biar di atas
        lines = playlist_content.splitlines()
        live_event, other_channels, current_group = [], [], None

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
        final_playlist = [line for line in final_playlist if line.strip()]

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(final_playlist))

        print(f"✅ Playlist disimpan ke {output_file} - {datetime.utcnow().isoformat()} UTC")
        return True

    except FileNotFoundError:
        print(f"❌ File sumber tidak ditemukan: {source_file}")
        return False
    except Exception as e:
        print(f"❌ Terjadi kesalahan: {e}")
        return False

process_playlist(SOURCE_FILE, OUTPUT_FILE)
