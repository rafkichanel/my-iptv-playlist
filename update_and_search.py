def cari_channel(keyword, file_m3u="merged.m3u"):
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
        print(f"Ditemukan {len(hasil)} channel dengan kata kunci '{keyword}':\n")
        for nama_channel, url in hasil:
            print(f"Channel: {nama_channel}\nURL: {url}\n")
    else:
        print(f"Tidak ditemukan channel dengan kata kunci '{keyword}'.")

if __name__ == "__main__":
    keyword = input("Masukkan kata kunci pencarian channel: ")
    cari_channel(keyword)
