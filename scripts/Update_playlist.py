import requests
import os
import re
import subprocess
from datetime import datetime

# Definisi file sumber dan file output
SOURCE_FILE = "sources.txt"          # daftar sumber m3u
OUTPUT_FILE = "playlist4.m3u"        # disimpan langsung di folder scripts

# URL logo baru
NEW_LOGO_URL = "https://raw.githubusercontent.com/rafkichanel/my-iptv-playlist/refs/heads/master/IMG_20250807_103611.jpg"

def process_playlist(source_file, output_file):
    try:
        with open(source_file, "r", encoding="utf-8") as f:
            sources = [line.strip() for line in f if line.strip()]

        merged_lines = []
        for idx, url in enumerate(sources, start=1):
            try:
                print(f"📡 Mengunduh dari sumber {idx}: {url}")
                r = requests.get(url, timeout=20)
                r.raise_for_status()
                lines = r.text.splitlines()

                # Filter kata kunci & kategori yang tidak diinginkan
                disallowed_words = ["DONASI", "UPDATE", "CADANGAN", "WHATSAPP", "CONTACT", "ADMIN"]
                processed_lines = []
                for line in lines:
                    line_upper = line.upper()
                    if any(word in line_upper for word in disallowed_words):
                        continue
                    if line.startswith("#EXTINF") and 'group-title="00.LIVE EVENT"' in line:
                        continue
                    if 'group-title="SMA"' in line:
                        continue
                    processed_lines.append(line)

                # Ganti logo lama dengan logo baru
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
                print(f"⚠️ Gagal ambil sumber {idx}: {e}")

        # Perbaiki nama grup
        playlist_content = "\n".join(merged_lines)
        playlist_content = re.sub(
            r'group-title="SEDANG LIVE"', 'group-title="LIVE EVENT"', playlist_content, flags=re.IGNORECASE
        )

        # Pisahkan LIVE EVENT ke atas
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

        # Overwrite file lama langsung
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write(f"# Updated: {datetime.utcnow().isoformat()} UTC\n")
            f.write("\n".join(final_playlist[1:]))

        print(f"✅ Playlist disimpan ke {output_file} - {datetime.utcnow().isoformat()} UTC")
        return True

    except Exception as e:
        print(f"🚨 Error: {e}")
        return False


def git_commit_and_push(file_path):
    try:
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
        subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)
        subprocess.run(["git", "add", "-f", file_path], check=True)
        msg = f"Update {file_path} otomatis {datetime.utcnow().isoformat()} UTC"
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print("🚀 Berhasil push ke repo")
    except Exception as e:
        print(f"⚠️ Git error: {e}")


if process_playlist(SOURCE_FILE, OUTPUT_FILE):
    git_commit_and_push(OUTPUT_FILE)
