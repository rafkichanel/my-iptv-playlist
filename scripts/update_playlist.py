import requests
import sys
from datetime import datetime, timedelta

# Konfigurasi
SOURCE_PRIVATE = "https://raw.githubusercontent.com/tyo878787/my-iptv-playlist/refs/heads/tyo878787/RfK01.m3u"
SOURCE_PUBLIC = "https://iptv-org.github.io/iptv/index.m3u"
OUTPUT_FILE = "RfK01.m3u"
REFRESH_HOURS = 6
SHORT_URL = "https://rebrand.ly/RFK02"
MAX_CHANNELS = 500  # Batasi jumlah channel dari sumber publik

def fetch_playlist(url):
    try:
        print(f"🔍 Fetching playlist: {url}")
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        
        if not response.text.strip():
            print(f"⚠️ Warning: Empty content from {url}")
            return ""
            
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {url}: {str(e)}")
        return ""
    except Exception as e:
        print(f"❌ Unexpected error with {url}: {str(e)}")
        return ""

def process_public_playlist(content):
    """Proses playlist publik yang besar"""
    if not content:
        return ""
    
    lines = content.splitlines()
    processed = []
    channel_count = 0
    
    # Header playlist
    if lines and lines[0].strip() == "#EXTM3U":
        processed.append(lines[0])
        lines = lines[1:]
    
    i = 0
    while i < len(lines) and channel_count < MAX_CHANNELS:
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        # Jika ini metadata channel
        if line.startswith("#EXTINF"):
            # Ambil 1 channel lengkap (metadata + URL)
            if i + 1 < len(lines) and lines[i+1].strip().startswith("http"):
                processed.append(line)
                processed.append(lines[i+1].strip())
                channel_count += 1
                i += 1  # Skip URL
        i += 1
    
    print(f"📺 Added {channel_count} public channels")
    return "\n".join(processed)

def process_private_playlist(content):
    """Proses playlist pribadi"""
    if not content:
        return ""
    
    lines = content.splitlines()
    processed = []
    
    # Header playlist
    if lines and lines[0].strip() == "#EXTM3U":
        processed.append(lines[0])
        lines = lines[1:]
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Jika ini metadata channel
        if line.startswith("#EXTINF"):
            if i + 1 < len(lines) and lines[i+1].strip().startswith("http"):
                processed.append(line)
                processed.append(lines[i+1].strip())
    
    print(f"📺 Added {len(processed)//2} private channels")
    return "\n".join(processed)

def main():
    print("\n" + "="*60)
    print("🚀 STARTING BREE IPTV PLAYLIST UPDATE")
    print("="*60)
    
    # Ambil playlist
    print("\n📥 Fetching playlists...")
    private_content = fetch_playlist(SOURCE_PRIVATE)
    public_content = fetch_playlist(SOURCE_PUBLIC)
    
    # Proses playlist
    print("\n🛠 Processing playlists...")
    private_playlist = process_private_playlist(private_content)
    public_playlist = process_public_playlist(public_content)
    
    # Gabungkan playlist
    combined = ""
    if private_playlist:
        combined += private_playlist + "\n\n"
    if public_playlist:
        combined += public_playlist + "\n\n"
    
    if not combined:
        print("\n❌ CRITICAL ERROR: No valid playlist content!")
        sys.exit(1)
    
    # Header auto-update
    now_utc = datetime.utcnow()
    next_update = now_utc + timedelta(hours=REFRESH_HOURS)
    
    header = f"""#EXTM3U
## AUTO-GENERATED PLAYLIST
## Created: {now_utc.strftime("%Y-%m-%d %H:%M:%S UTC")}
## Next Update: {next_update.strftime("%Y-%m-%d %H:%M:%S UTC")}
## Sources:
## - Private: {SOURCE_PRIVATE} (all channels)
## - Public: {SOURCE_PUBLIC} (first {MAX_CHANNELS} channels)
## User Access: {SHORT_URL}
#REFRESH-INTERVAL:{REFRESH_HOURS * 3600:.1f}
#REFRESH-URI:{SHORT_URL}
#REFRESH-DATE:{next_update.strftime("%Y-%m-%dT%H:%M:%SZ")}
#GENERATED-BY:https://github.com/tyo878787/my-iptv-playlist

"""
    
    full_playlist = header + combined.strip()
    
    # Simpan file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(full_playlist)
    
    # Statistik
    extinf_count = full_playlist.count("#EXTINF")
    
    print("\n" + "="*60)
    print("✅ UPDATE SUCCESSFUL")
    print("="*60)
    print(f"📁 Output file: {OUTPUT_FILE}")
    print(f"📺 Total channels: {extinf_count}")
    print(f"🕒 Next update: {next_update.strftime('%Y-%m-%d %H:%M UTC')}")
    
    # Tampilkan sample
    print("\n🔍 Sample channels:")
    lines = full_playlist.splitlines()
    for i in range(min(50, len(lines))):
        print(lines[i])
    print("... [truncated] ...")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n🔥 UNHANDLED ERROR: {str(e)}")
        sys.exit(1)
