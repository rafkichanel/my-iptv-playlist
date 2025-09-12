Import requests
import os
import re
from datetime import datetime

# Definisi file sumber dan file output
SOURCE_FILE = "sources.txt"
OUTPUT_FILE = "playlist4.m3u"

# URL logo baru
NEW_LOGO_URL = "https://raw.githubusercontent.com/rafkichanel/my-iptv-playlist/refs/heads/master/IMG_20250807_103611.jpg"

def process_playlist(source_file, output_file):
    """
    Mengunduh, memproses, dan menyimpan playlist dari file sumber.
    """
    try:
        if not os.path.exists(source_file):
            print(f"ðŸš« File sumber tidak ditemukan: {source_file}")
            return False

        with open(source_file, "r", encoding="utf-8") as f:
            sources = [line.strip() for line in f if line.strip()]

        merged_lines = []
        for idx, url in enumerate(sources, start=1):
            try:
                print(f"ðŸ”„ Mengunduh dari sumber {idx}: {url}")
                r = requests.get(url, timeout=15)
                r.raise_for_status()
                lines = r.text.splitlines()

                # Daftar kata kunci yang tidak diinginkan
                disallowed_words = ["DONASI", "UPDATE", "CADANGAN", "WHATSAPP", "CONTACT", "ADMIN", "CHANNEL | JAPAN",]
                
                processed_lines = []
                for line in lines:
                    line_upper = line.upper()
                    
                    # Menghapus baris yang mengandung kata kunci yang tidak diinginkan
                    if any(word in line_upper for word in disallowed_words):
                        continue
                    
                    # Menghapus kategori LIVE EVENT dan SMA
                    if line.startswith("#EXTINF") and ('group-title="00.LIVE EVENT"' in line or 'group-title="SMA"' in line):
                        continue
                    
                    processed_lines.append(line)

                # Menghapus logo lama dan menambahkan logo baru
                final_processed_lines = []
                for line in processed_lines:
                    if line.startswith("#EXTINF"):
                        # Cari logo asli konten (tvg-logo)
                        tvg_logo_match = re.search(r'tvg-logo="([^"]*)"', line)
                        original_tvg_logo = tvg_logo_match.group(1) if tvg_logo_match else ""

                        # Hapus semua tag logo yang ada di baris
                        line = re.sub(r'\s+tvg-logo="[^"]*"', '', line)
                        line = re.sub(r'\s+group-logo="[^"]*"', '', line)

                        # Tambahkan logo Rafki untuk group dan logo asli untuk tvg
                        new_logo_tags = f' tvg-logo="{original_tvg_logo}" group-logo="{NEW_LOGO_URL}"'
                        
                        line_parts = line.split(',', 1)
                        if len(line_parts) > 1:
                            attributes_and_title = line_parts[0].strip()
                            channel_name = line_parts[1].strip()
                            
                            # Rekonstruksi baris dengan logo baru
                            new_line = f'{attributes_and_title}{new_logo_tags},{channel_name}'
                            final_processed_lines.append(new_line)
                        else:
                            final_processed_lines.append(line)
                    else:
                        final_processed_lines.append(line)
                
                merged_lines.extend(final_processed_lines)
            except Exception as e:
                print(f"ðŸš« Gagal ambil sumber {idx}: {e}")

        # Perbaikan nama grup (misal: "SEDANG LIVE" menjadi "LIVE EVENT")
        playlist_content = "\n".join(merged_lines)
        playlist_content = re.sub(
            r'group-title="SEDANG LIVE"', 'group-title="LIVE EVENT"', playlist_content, flags=re.IGNORECASE
        )

        # Pisahkan LIVE EVENT agar tampil duluan
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

        # Simpan file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(final_playlist))

        print(f"ðŸ¤© Playlist berhasil disimpan di {output_file} - {datetime.utcnow().isoformat()} UTC")
        return True

    except Exception as e:
        print(f"ðŸš« Terjadi kesalahan: {e}")
        return False

# --- Jalankan proses ---
process_playlist(SOURCE_FILE, OUTPUT_FILE)


