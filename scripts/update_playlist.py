import requests
import re
import base64

SOURCE1 = "https://raw.githubusercontent.com/tyo878787/my-iptv-playlist/refs/heads/tyo878787/RfK01.m3u"
SOURCE2 = "https://iptv-org.github.io/iptv/index.m3u"
OUTPUT = "RfK01.m3u"

DECODER_BASE = "https://your-worker-domain.workers.dev"  # Ganti ini dengan URL Cloudflare Worker-mu

# Regex untuk URL http/https
URL_RE = re.compile(r"^(https?://\S+)$")

def encode_url(url: str) -> str:
    # Encode URL jadi base64 tanpa padding dan URL-safe
    b64 = base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")
    return b64

def process_playlist(text: str) -> str:
    lines = text.splitlines()
    output = []
    for line in lines:
        m = URL_RE.match(line.strip())
        if m:
            url = m.group(1)
            encoded = encode_url(url)
            output.append(f"{DECODER_BASE}/{encoded}")
        else:
            output.append(line)
    return "\n".join(output)

def main():
    # Ambil playlist sumber
    p1 = requests.get(SOURCE1).text
    p2 = requests.get(SOURCE2).text

    combined = p1 + "\n" + p2

    processed = process_playlist(combined)

    # Pastikan ada header #EXTM3U
    if not processed.lstrip().startswith("#EXTM3U"):
        processed = "#EXTM3U\n" + processed

    # Simpan ke file output
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(processed)

    print(f"✅ Playlist berhasil dibuat di {OUTPUT}")

if __name__ == "__main__":
    main()
