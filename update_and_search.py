import requests

def fetch_playlist(url):
    print("Mengambil playlist utama dari URL...")
    r = requests.get(url)
    r.raise_for_status()
    return r.text

def read_new_channels(file_path):
    print("Membaca channel baru dari file...")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    channels = [ch.strip() for ch in content.split("\n\n") if ch.strip()]
    return channels

def parse_channels(playlist_text):
    lines = playlist_text.splitlines()
    channels = []
    temp = []
    for line in lines:
        if line.startswith("#EXTINF:") and temp:
            channels.append("\n".join(temp))
            temp = [line]
        else:
            temp.append(line)
    if temp:
        channels.append("\n".join(temp))
    return channels

def merge_channels(main_channels, new_channels):
    existing_ids = set()
    for ch in main_channels:
        first_line = ch.splitlines()[0]
        if 'tvg-id="' in first_line:
            start = first_line.find('tvg-id="') + 8
            end = first_line.find('"', start)
            existing_ids.add(first_line[start:end])
        else:
            existing_ids.add(first_line)

    merged = main_channels.copy()
    added = 0
    for ch in new_channels:
        first_line = ch.splitlines()[0]
        if 'tvg-id="' in first_line:
            start = first_line.find('tvg-id="') + 8
            end = first_line.find('"', start)
            ch_id = first_line[start:end]
        else:
            ch_id = first_line

        if ch_id not in existing_ids:
            merged.append(ch)
            existing_ids.add(ch_id)
            added += 1

    print(f"Channel baru ditambahkan: {added}")
    return merged

def save_playlist(channels, filename):
    print(f"Menyimpan playlist gabungan ke {filename} ...")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in channels:
            f.write(ch + "\n")

def cari_channel(file_m3u, keyword):
    print(f"Mencari channel dengan kata kunci '{keyword}'...")
    with open(file_m3u, "r", encoding="utf-8") as f:
        lines = f.readlines()

    hasil = []
    for i, line in enumerate(lines):
        if keyword.lower() in line.lower() and line.startswith("#EXTINF"):
            nama_channel = line.strip()
            url = lines[i+1].strip() if i+1 < len(lines) else ""
            hasil.append((nama_channel, url))

    if hasil:
        for ch, link in hasil:
            print(f"{ch}\

cat > new_channels.txt << EOF
#EXTINF:-1 tvg-id="NewCh1" group-title="NewCategory",New Channel 1
http://example.com/stream1

#EXTINF:-1 tvg-id="NewCh2" group-title="NewCategory",New Channel 2
http://example.com/stream2
