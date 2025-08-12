import requests

# Playlist utama lokal yang ingin diupdate
main_playlist_file = "Finalplay.m3u"

# Daftar URL playlist backup dari berbagai sumber GitHub, urutan prioritas sumber pertama adalah milik kamu
backup_playlist_urls = [
    "https://raw.githubusercontent.com/rafkichanel/my-iptv-playlist/refs/heads/master/playlist1.m3u",  # Playlist milik kamu, update sendiri
    "https://raw.githubusercontent.com/Free-TV/IPTV/main/playlist.m3u",                             # Playlist global, channel lengkap dari Free-TV
    "https://raw.githubusercontent.com/iptv-restream/IPTV/main/iptv.m3u",                           # Playlist kategori beragam dari iptv-restream
    "https://raw.githubusercontent.com/matjava/xtream-playlist/main/xtream-playlist.m3u",           # Playlist M3U8 koleksi matjava
    "https://raw.githubusercontent.com/sacuar/MyIPTV/main/MyIPTV.m3u",                              # Playlist aktif dari sacuar
    "https://raw.githubusercontent.com/HerbertHe/iptv-sources/main/iptv-sources.m3u",               # Playlist otomatis update dari HerbertHe
]

def parse_m3u(playlist_text):
    """
    Parsing playlist M3U dan membuat dict channel_name: stream_url
    """
    channels = {}
    lines = playlist_text.splitlines()
    name = None
    for line in lines:
        if line.startswith("#EXTINF:"):
            name = line.split(",", 1)[1].strip()
        elif line.startswith("http") and name:
            channels[name] = line.strip()
            name = None
    return channels

def check_url(url):
    """
    Cek apakah URL streaming bisa diakses (status code 200)
    """
    try:
        resp = requests.head(url, timeout=5)
        return resp.status_code == 200
    except:
        return False

def find_replacement(channel_name, backup_channels_list):
    """
    Cari link pengganti dari daftar playlist backup berdasarkan nama channel dan cek url-nya valid
    """
    for backup_channels in backup_channels_list:
        if channel_name in backup_channels:
            url = backup_channels[channel_name]
            if check_url(url):
                return url
    return None

def update_playlist_auto(main_file, backup_urls, output_file):
    print("Mengambil playlist backup dari semua sumber...")
    backup_channels_list = []
    for url in backup_urls:
        try:
            print(f"Download playlist dari: {url}")
            text = requests.get(url, timeout=10).text
            backup_channels_list.append(parse_m3u(text))
        except Exception as e:
            print(f"Gagal ambil playlist dari {url}: {e}")

    with open(main_file, "r", encoding="utf-8") as f:
        main_lines = f.readlines()

    new_lines = []
    current_channel = None

    for line in main_lines:
        if line.startswith("#EXTINF:"):
            current_channel = line.split(",", 1)[1].strip()
            new_lines.append(line)
        elif line.strip().startswith("http") and current_channel:
            url = line.strip()
            if not check_url(url):
                print(f"Link channel '{current_channel}' mati, mencari pengganti...")
                new_url = find_replacement(current_channel, backup_channels_list)
                if new_url:
                    print(f"Ketemu link pengganti untuk '{current_channel}': {new_url}")
                    new_lines.append(new_url + "\n")
                else:
                    print(f"Tidak ada link pengganti untuk '{current_channel}', pakai link lama.")
                    new_lines.append(line)
            else:
                new_lines.append(line)
            current_channel = None
        else:
            new_lines.append(line)

    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"Playlist berhasil diperbarui dan disimpan ke '{output_file}'.")

if __name__ == "__main__":
    update_playlist_auto(main_playlist_file, backup_playlist_urls, "Finalplay_updated.m3u")
