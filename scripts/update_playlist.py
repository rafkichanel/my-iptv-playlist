import requests

SOURCE1 = "https://raw.githubusercontent.com/tyo878787/my-iptv-playlist/refs/heads/tyo878787/RfK01.m3u"
SOURCE2 = "https://iptv-org.github.io/iptv/index.m3u"
OUTPUT = "RfK01.m3u"

def main():
    # Ambil playlist pertama
    try:
        r1 = requests.get(SOURCE1, timeout=10)
        r1.raise_for_status()
        content1 = r1.text
    except:
        content1 = ""
    
    # Ambil playlist kedua
    try:
        r2 = requests.get(SOURCE2, timeout=15)
        r2.raise_for_status()
        content2 = r2.text
    except:
        content2 = ""
    
    # Gabungkan
    combined = ""
    if content1:
        combined += content1.strip() + "\n\n"
    if content2:
        combined += content2.strip() + "\n\n"
    
    # Pastikan ada header
    if not combined.startswith("#EXTM3U"):
        combined = "#EXTM3U\n" + combined
    
    # Simpan
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(combined.strip())
    
    print(f"✅ Playlist berhasil digabung: {OUTPUT}")

if __name__ == "__main__":
    main()
