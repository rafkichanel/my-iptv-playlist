import requests
from datetime import datetime

# URL sumber playlist
url = "https://iptv-org.github.io/iptv/index.m3u"

print("Mengambil playlist...")
playlist = requests.get(url).text

lines = playlist.splitlines()
new_lines = []
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

for line in lines:
    if line.startswith("#EXTINF:"):
        # Tambah baris timestamp sebelum channel
        new_lines.append(f"#TIME: {current_time}")
    new_lines.append(line)

with open("Finalplay.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(new_lines))

# Catat waktu update terakhir
with open("LAST_UPDATE.txt", "w", encoding="utf-8") as f:
    f.write(current_time)

print("Playlist berhasil diperbarui dengan timestamp channel dan waktu update dicatat.")
