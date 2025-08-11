import requests
from datetime import datetime

# URL playlist sumber
url = "https://iptv-org.github.io/iptv/index.m3u"

print("Mengambil playlist...")
playlist = requests.get(url).text

# Simpan playlist ke file
with open("Finalplay.m3u", "w", encoding="utf-8") as f:
    f.write(playlist)

# Catat waktu update terakhir
with open("LAST_UPDATE.txt", "w", encoding="utf-8") as f:
    f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

print("Playlist berhasil diperbarui dan waktu update dicatat.")
