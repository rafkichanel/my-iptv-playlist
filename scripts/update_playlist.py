import requests
import sys
from datetime import datetime, timedelta

# Konfigurasi
SOURCE_PRIVATE = "https://raw.githubusercontent.com/tyo878787/my-iptv-playlist/refs/heads/tyo878787/RfK01.m3u"
SOURCE_PUBLIC = "https://iptv-org.github.io/iptv/index.m3u"
OUTPUT_FILE = "RfK01.m3u"
REFRESH_HOURS = 6
SHORT_URL = "https://rebrand.ly/RFK02"

def fetch_playlist(url):
    try:
        print(f"🔍 Fetching playlist: {url}")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        # Validasi dasar konten
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

def convert_to_valid_m3u(content, source_name):
    """Konversi playlist ke format valid"""
    if not content:
        return ""
        
    lines = content.splitlines()
    valid_lines = []
    
    # Tambahkan header jika tidak ada
    if not any(line.strip().startswith("#EXTM3U") for line in lines):
        valid_lines.append("#EXTM3U")
    
    i = 0
    channel_count = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        # Handle komentar dan metadata
        if line.startswith("#"):
            valid_lines.append(line)
        
        # Jika line adalah URL streaming
        elif line.startswith(("http://", "https://", "rtmp://", "rtsp://")):
            channel_count += 1
            channel_name = f"Channel {channel_count} ({source_name})"
            valid_lines.append(f'#EXTINF:-1,{channel_name}')
            valid_lines.append(line)
        
        # Skip line yang tidak perlu
        i += 1
        
    return "\n".join(valid_lines)

def main():
    print("\n" + "="*60)
    print("🚀 STARTING BREE IPTV PLAYLIST UPDATE")
    print("="*60)
    
    # Ambil playlist
    print("\n📥 Fetching playlists...")
    private_content = fetch_playlist(SOURCE_PRIVATE)
    public_content = fetch_playlist(SOURCE_PUBLIC)
    
    # Konversi ke format valid
    print("\n🛠 Converting playlists to valid format...")
    private_playlist = convert_to_valid_m3u(private_content, "Private") if private_content else ""
    public_playlist = convert_to_valid_m3u(public_content, "Public") if public_content else ""
    
    # Gabungkan playlist
    print("\n🧩 Combining playlists...")
    combined = ""
    if private_playlist:
        combined += private_playlist.strip() + "\n\n"
    if public_playlist:
        combined += public_playlist.strip() + "\n\n"
    
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
## - Private: {SOURCE_PRIVATE}
## - Public: {SOURCE_PUBLIC}
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
    
    # Hitung statistik
    extinf_count = full_playlist.count("#EXTINF")
    http_count = full_playlist.count("http")
    
    print("\n" + "="*60)
    print("✅ UPDATE SUCCESSFUL")
    print("="*60)
    print(f"📁 Output file: {OUTPUT_FILE}")
    print(f"📺 Channel count: {extinf_count}")
    print(f"🔗 Stream URLs: {http_count}")
    print(f"🕒 Next update: {next_update.strftime('%Y-%m-%d %H:%M UTC')}")
    
    # Tampilkan sample
    sample_lines = []
    lines = full_playlist.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("#EXTINF"):
            sample_lines.append(line)
            if i+1 < len(lines) and lines[i+1].startswith("http"):
                sample_lines.append(lines[i+1])
            if len(sample_lines) >= 4:
                break
    
    print("\n🔍 Sample channels:")
    print("\n".join(sample_lines))
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n🔥 UNHANDLED ERROR: {str(e)}")
        sys.exit(1)
