import requests
import base64
import re

SOURCE1 = "https://raw.githubusercontent.com/tyo878787/my-iptv-playlist/refs/heads/tyo878787/RfK01.m3u"
SOURCE2 = "https://iptv-org.github.io/iptv/index.m3u"
OUTPUT_FILE = "RfK01.m3u"

HTTP_URL_RE = re.compile(r'^(https?://\S+)$')

def encode_url(url):
    b = base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")
    return b

def process_playlist(content, decoder_base):
    lines = content.splitlines()
    out_lines = []
    for line in lines:
        m = HTTP_URL_RE.match(line.strip())
        if m:
            encoded = encode_url(m.group(1))
            out_lines.append(f"{decoder_base}/{encoded}")
        else:
            out_lines.append(line)
    return "\n".join(out_lines)

def main():
    DECODER_BASE = "https://your-cloudflare-worker.workers.dev"  # Ganti dengan URL decoder kamu

    # Ambil source playlist
    p1 = requests.get(SOURCE1).text
    p2 = requests.get(SOURCE2).text

    combined = p1 + "\n" + p2

    encoded_playlist = process_playlist(combined, DECODER_BASE)

    # Pastikan header
    if not encoded_playlist.lstrip().startswith("#EXTM3U"):
        encoded_playlist = "#EXTM3U\n" + encoded_playlist

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(encoded_playlist)

    print(f"Berhasil update {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
