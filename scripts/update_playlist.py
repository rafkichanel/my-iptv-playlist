
import requests
import base64

# Sumber playlist
url1 = "https://raw.githubusercontent.com/tyo878787/my-iptv-playlist/refs/heads/tyo878787/RfK01.m3u"
url2 = "https://iptv-org.github.io/iptv/index.m3u"

# Ambil playlist pertama
p1 = requests.get(url1).text.strip()

# Ambil playlist kedua
p2 = requests.get(url2).text.strip()

# Gabungkan
gabungan = p1 + "\n" + p2

# Encode Base64
encoded = base64.b64encode(gabungan.encode()).decode()

# Buat file hasil gabungan
with open("Rafki.m3u", "w", encoding="utf-8") as f:
    f.write(encoded)

print("✅ Playlist gabungan berhasil dibuat: Rafki.m3u")
