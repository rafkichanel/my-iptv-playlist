import requests
import re
from datetime import datetime
from requests.adapters import HTTPAdapter, Retry

# Definisi file sumber dan file output
SOURCE_FILE = "sources.txt"
OUTPUT_FILE = "Finalplay04.m3u"

# URL logo baru
NEW_LOGO_URL = "https://raw.githubusercontent.com/rafkichanel/my-iptv-playlist/refs/heads/master/IMG_20250807_103611.jpg"

# Kategori yang diijinkan
ALLOWED_GROUPS = {"INDONESIA", "SPORT", "KIDS"}   # <<< bisa edit sesuai kebutuhan

# Setup session
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount("http://", HTTPAdapter(max_retries=retries))
session.mount("https://", HTTPAdapter(max_retries=retries))

def process_playlist(source_file, output_file):
    try:
        with open(source_file, "r", encoding="utf-8") as f:
            sources = [line.strip() for line in f if line.strip()]

        merged_lines = []
        for idx, url in enumerate(sources, start=1):
            try:
                print(f"🚀 Ambil sumber {idx}: {url}")
                r = session.get(url, timeout=10)
                r.raise_for_status()
                lines = r.text.splitlines()

                disallowed_words = [
                    "DONASI", "UPDATE", "CADANGAN", "WHATSAPP", "CONTACT",
                    "ADMIN", "TEST", "404", "STREAM NOT FOUND"
                ]

                processed_lines, current_group, skip_block = [], None, False

                for line in lines:
                    line_upper = line.upper()
                    if any(word in line_upper for word in disallowed_words):
                        continue
                    if line.startswith("#EXTINF"):
                        match = re.search(r'group-title="([^"]+)"', line, flags=re.IGNORECASE)
                        if match:
                            current_group = match.group(1).upper()
                            # Skip jika bukan kategori allowed
                            if current_group not in ALLOWED_GROUPS:
                                skip_block = True
                                continue
                            else:
                                skip_block = False
                        # Hapus logo lama + ganti baru
                        line = re.sub(r'tvg-logo="[^"]*"', '', line)
                        line = re.sub(r'group-logo="[^"]*"', '', line)
                        new_tags = f' group-logo="{NEW_LOGO_URL}" tvg-logo="{NEW_LOGO_URL}"'
                        parts = line.split(',', 1)
                        if len(parts) > 1:
                            m = re.search(r'#EXTINF:(-1.*)', parts[0])
                            if m:
                                attrs = m.group(1).strip()
                                new_line = f'#EXTINF:{attrs}{new_tags},{parts[1].strip()}'
                                processed_lines.append(new_line)
                            else:
                                processed_lines.append(line)
                        else:
                            processed_lines.append(line)
                    else:
                        if not skip_block:
                            processed_lines.append(line)

                merged_lines.extend(processed_lines)
                print(f"✅ Berhasil ambil sumber {idx}")

            except Exception as e:
                print(f"❌ Gagal ambil sumber {idx}: {e}")

        # Buang semua LIVE EVENT (kalau masih ada sisa)
        playlist_content = "\n".join(merged_lines)
        playlist_content = re.sub(r'#EXTINF[^\n]*group-title="LIVE EVENT"[^\n]*\n?.*', '', playlist_content, flags=re.IGNORECASE)
        playlist_content = re.sub(r'#EXTINF[^\n]*group-title="SEDANG LIVE"[^\n]*\n?.*', '', playlist_content, flags=re.IGNORECASE)
        playlist_content = re.sub(r'#EXTINF[^\n]*group-title="00\.LIVE EVENT"[^\n]*\n?.*', '', playlist_content, flags=re.IGNORECASE)

        # Simpan hasil akhir
        final_playlist = ["#EXTM3U"] + [line for line in playlist_content.splitlines() if line.strip()]
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(final_playlist))

        print(f"🎯 Playlist disimpan ke {output_file} - {datetime.utcnow().isoformat()} UTC")
        return True

    except FileNotFoundError:
        print(f"❌ File sumber tidak ditemukan: {source_file}")
        return False
    except Exception as e:
        print(f"💥 Error saat proses {source_file}: {e}")
        return False

# Jalankan
process_playlist(SOURCE_FILE, OUTPUT_FILE)
