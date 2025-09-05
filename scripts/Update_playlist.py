import requests
import os
import re
from datetime import datetime

# Definisi file sumber dan file output
SOURCE_FILE = "sources.txt"          # daftar sumber m3u
OUTPUT_FILE = "Finalplay04.m3u"      # disimpan langsung di folder scripts

# URL logo baru
NEW_LOGO_URL = "https://raw.githubusercontent.com/rafkichanel/my-iptv-playlist/refs/heads/master/IMG_20250807_103611.jpg"

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

                # --- Gabungkan semua filter dalam satu baris untuk efisiensi ---
                # Kata "SAM" telah dihapus dari daftar filter
                lines = [line for line in lines if not any(word in line.upper() for word in ["DONASI", "UPDATE", "CADANGAN", "WHATSAPP"])]

                if idx == 3:
                    lines = [line.replace("🔴", "") for line in lines]
                lines = [line for line in lines if 'group-title="SMA"' not in line]

                # --- Hapus logo lama ---
                cleaned_lines = []
                for line in lines:
                    if line.startswith("#EXTINF"):
                        line = re.sub(r'tvg-logo="[^"]*"', '', line)
                        line = re.sub(r'group-logo="[^"]*"', '', line)
                    cleaned_lines.append(line)
                lines = cleaned_lines

                # --- Tambah logo baru ---
                final_processed_lines = []
                for line in lines:
                    if line.startswith("#EXTINF"):
                        new_line_logo_tags = f' group-logo="{NEW_LOGO_URL}" tvg-logo="{NEW_LOGO_URL}"'
                        line_parts = line.split(',', 1)
                        if len(line_parts) > 1:
                            match = re.search(r'#EXTINF:(-1.*)', line_parts[0])
                            if match:
                                attributes = match.group(1).strip()
                                new_line = f'#EXTINF:{attributes}{new_line_logo_tags},{line_parts[1].strip()}'
                                final_processed_lines.append(new_line)
                            else:
                                final_processed_lines.append(line)
                        else:
                            final_processed_lines.append(line)
                    else:
                        final_processed_lines.append(line)
                merged_lines.extend(final_processed_lines)
            except Exception as e:
                print(f"⚠️ Gagal ambil sumber {idx} dari {source_file}: {e}")

        # Perbaikan nama grup
        playlist_content = "\n".join(merged_lines)
        playlist_content = re.sub(
            r'group-title="SEDANG LIVE"', 'group-title="LIVE EVENT"', playlist_content, flags=re.IGNORECASE
        )

        # Pisahkan LIVE EVENT biar tampil duluan
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
        final_playlist = [line for line in final_playlist if line.strip()]  # hapus baris kosong

        # Simpan file (langsung ke folder scripts)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(final_playlist))

        print(f"✅ Playlist disimpan ke {output_file} - {datetime.utcnow().isoformat()} UTC")
        return True

    except FileNotFoundError:
        print(f"❗ File sumber tidak ditemukan: {source_file}")
        return False
    except Exception as e:
        print(f"❌ Terjadi kesalahan saat memproses {source_file}: {e}")
        return False

# --- Jalankan proses ---
process_playlist(SOURCE_FILE, OUTPUT_FILE)

