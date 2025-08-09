import requests

SOURCE1 = "https://raw.githubusercontent.com/tyo878787/my-iptv-playlist/refs/heads/tyo878787/RfK01.m3u"
SOURCE2 = "https://iptv-org.github.io/iptv/index.m3u"
OUTPUT = "RfK01.m3u"

def main():
    p1 = requests.get(SOURCE1).text
    p2 = requests.get(SOURCE2).text

    combined = p1 + "\n" + p2

    if not combined.lstrip().startswith("#EXTM3U"):
        combined = "#EXTM3U\n" + combined

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(combined)

    print(f"✅ Playlist berhasil dibuat di {OUTPUT}")

if __name__ == "__main__":
    main()
