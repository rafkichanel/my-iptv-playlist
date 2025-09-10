import requests
import re
from datetime import datetime

# Definisi file sumber dan file output
SOURCE_FILE = "sources.txt"          # daftar sumber m3u
OUTPUT_FILE = "Playlist4.m3u"        # output baru

# URL logo baru
NEW_LOGO_URL = "https://raw.githubusercontent.com/rafkichanel/my-iptv-playlist/refs/heads/master/IMG_20250807_103611.jpg"

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
                for line in lines:
                    line_upper = line.upper()
                    if any(word in line_upper for word in disallowed_words):
                        continue
                    if line.startswith("#EXTINF") and 'group-title="00.LIVE EVENT"' in line:
                        continue
                    processed_lines.append(line)

                # Tambahkan logo baru
                final_processed_lines = []
                for line in processed_lines:
                    if line.startswith("#EXTINF"):
                        line = re.sub(r'tvg-logo="[^"]*"', '', line)
                        line = re.sub(r'group-logo="[^"]*"', '', line)
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

        lines = "\n".join(merged_lines).splitlines()

        # --- FILTER --- #
        keep_keywords_group = ["INDONESIA", "ID", "NASIONAL", "VISION", "VISION+", "VISION PLUS", "SMA", "SPORT", "SPORTS", "OLAH RAGA"]
        keep_keywords_channel = [
            "RCTI", "SCTV", "INDOSIAR", "TRANSTV", "TRANS7", "TVONE", 
            "ANTV", "METRO", "MNCTV", "GTV", "INEWS", "NET", "KOMPAS", 
            "RTV", "TVRI"
        ]

        filtered_final = []
        sport_section = []
        sma_taken = False
        keep_next = False
        temp_line = None
        seen_channels = set()  # untuk hapus duplikat

        for line in lines:
            if line.startswith("#EXTINF"):
                group_match = re.search(r'group-title="([^"]+)"', line, re.IGNORECASE)
                channel_name_match = line.split(",", 1)
                channel_name = channel_name_match[1].strip().upper() if len(channel_name_match) > 1 else ""

                ok = False
                group_name = ""

                if group_match:
                    group_name = group_match.group(1).upper()
                    if any(k in group_name for k in keep_keywords_group):
                        ok = True

                if any(k in channel_name for k in keep_keywords_channel):
                    ok = True

                if ok and channel_name not in seen_channels:
                    # handle sport → simpan di sport_section
                    if "SPORT" in group_name:
                        temp_line = re.sub(r'group-title="[^"]+"', 'group-title="SPORT ALL"', line)
                        keep_next = "SPORT"
                        seen_channels.add(channel_name)
                    # handle SMA → ambil hanya satu channel
                    elif "SMA" in group_name:
                        if not sma_taken:
                            temp_line = line
                            keep_next = "SMA"
                            sma_taken = True
                            seen_channels.add(channel_name)
                        else:
                            keep_next = False
                    else:
                        filtered_final.append(line)
                        keep_next = True
                        seen_channels.add(channel_name)
                else:
                    keep_next = False
            else:
                if keep_next == "SPORT":
                    sport_section.append(temp_line)
                    sport_section.append(line)
                    keep_next = False
                elif keep_next == "SMA":
                    filtered_final.append(temp_line)
                    filtered_final.append(line)
                    keep_next = False
                elif keep_next:
                    filtered_final.append(line)

        # Playlist final
        final_playlist = ["#EXTM3U"] + filtered_final + sport_section
        final_playlist = [line for line in final_playlist if line.strip()]

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(final_playlist))

        print(f"✅ Playlist disimpan ke {output_file} - {datetime.utcnow().isoformat()} UTC")
        return True

    except FileNotFoundError:
        print(f"❌ File sumber tidak ditemukan: {source_file}")
        return False
    except Exception as e:
        print(f"⛔ Terjadi kesalahan saat memproses {source_file}: {e}")
        return False


# --- Jalankan proses ---
process_playlist(SOURCE_FILE, OUTPUT_FILE)
