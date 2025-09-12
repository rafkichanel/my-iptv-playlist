import requests
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
                disallowed_words = ["DONASI", "UPDATE", "CADANGAN", "WHATSAPP", "CONTACT", "ADMIN"]
                
                processed_lines = []
                # Gunakan flag untuk menandai blok yang harus dihilangkan
                skip_block = False
                for line in lines:
                    line_upper = line.upper()

                    # Cek apakah baris ini adalah awal dari blok yang ingin dihapus
                    if 'group-title="SMA"' in line_upper or 'group-title="LIVE EVENT"' in line_upper or 'group-title="CHANNEL | JAPAN"' in line_upper:
                        skip_block = True
                        continue  # Langsung lewati baris ini

                    # Jika sedang dalam mode "skip", cek apakah blok sudah berakhir
                    if skip_block:
                        if line.startswith("#EXTINF"):
                            skip_block = False
                        else:
                            continue  # Jika belum, lewati baris ini

                    # Jika tidak sedang dalam mode "skip", proses baris seperti biasa
                    if any(word in line_upper for word in disallowed_words):
                        continue
                    
                    final_line_to_add = line
                    if final_line_to_add.startswith("#EXTINF"):
                        # Cari logo asli konten (tvg-logo)
                        tvg_logo_match = re.search(r'tvg-logo="([^"]*)"', final_line_to_add)
                        original_tvg_logo = tvg_logo_match.group(1) if tvg_logo_match else ""

                        # Hapus semua tag logo yang ada di baris
                        final_line_to_add = re.sub(r'\s+tvg-logo="[^"]*"', '', final_line_to_add)
                        final_line_to_add = re.sub(r'\s+group-logo="[^"]*"', '', final_line_to_add)

                        # Tambahkan logo Rafki untuk group dan logo asli untuk tvg
                        new_logo_tags = f' tvg-logo="{original_tvg_logo}" group-logo="{NEW_LOGO_URL}"'
                        
                        line_parts = final_line_to_add.split(',', 1)
                        if len(line_parts) > 1:
                            attributes_and_title = line_parts[0].strip()
                            channel_name = line_parts[1].strip()
                            final_line_to_add = f'{attributes_and_title}{new_logo_tags},{channel_name}'
                                
                    processed_lines.append(final_line_to_add)

                merged_lines.extend(processed_lines)

            except Exception as e:
                print(f"ðŸš« Gagal ambil sumber {idx}: {e}")

        final_playlist = ["#EXTM3U"] + [line for line in merged_lines if line.strip()]

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(final_playlist))

        print(f"ðŸ¤© Playlist berhasil disimpan di {output_file} - {datetime.utcnow().isoformat()} UTC")
        return True

    except FileNotFoundError:
        print(f"ðŸš« File sumber tidak ditemukan: {source_file}")
        return False
    except Exception as e:
        print(f"ðŸš« Terjadi kesalahan: {e}")
        return False

# --- Jalankan proses ---
process_playlist(SOURCE_FILE, OUTPUT_FILE)
            
