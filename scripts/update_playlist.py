import requests
import os
import random
import re
from datetime import datetime

MAIN_FILE = "Finalplay.m3u"

# Baca daftar sumber dari sources.txt
with open("sources.txt", "r") as f:
    sources = [line.strip() for line in f if line.strip()]

# Simpan terpisah konten per sumber
final_content_list = ["", "", ""]
channel_count = [0, 0, 0]  # jumlah channel per sumber
sma_moved_count = 0
live_event_blocks = []  # simpan blok Live Event di sini

for idx, url in enumerate(sources, start=1):
    try:
        print(f"Download dari {url}...")
        r = requests.get(url, timeout=15)
        r.raise_for_status()

        # Filter hapus WHATSAPP
        lines = [line for line in r.text.splitlines() if "WHATSAPP" not in line.upper()]

        if idx == 3:
            # Hilangkan ikon 🔴 di semua baris
            lines = [line.replace("🔴", "") for line in lines]

            non_sma_lines = []
            sma_blocks = []
            current_block = []
            block_is_sma = False

            for line in lines:
                if line.startswith("#EXTINF"):
                    block_is_sma = "SMA" in line.upper()
                    if block_is_sma:
                        # 1️⃣ Ganti "SMA" → "SMX"
                        mod_line = re.sub(r"SMA", "SMX", line, flags=re.IGNORECASE)
                        # 2️⃣ Hilangkan simbol bullet merah / simbol aneh
                        mod_line = re.sub(r"[•●★◆]", "", mod_line)
                        # 3️⃣ Ganti angka kategori 1-3 secara acak
                        mod_line = re.sub(r"(,.*\|)([123])(\|)",
                                          lambda m: m.group(1) + str(random.randint(1, 3)) + m.group(3),
                                          mod_line)
                        # 4️⃣ Ganti "Sedang Live" → "Live Event"
                        mod_line = re.sub(r"Sedang\s*Live", "Live Event", mod_line, flags=re.IGNORECASE)

                        current_block = [mod_line]
                    else:
                        current_block = [line]

                elif line.startswith("http"):
                    current_block.append(line)
                    if block_is_sma:
                        sma_blocks.append("\n".join(current_block))
                        live_event_blocks.append("\n".join(current_block))  # simpan untuk taruh paling atas
                        sma_moved_count += 1
                    else:
                        non_sma_lines.extend(current_block)

                else:
                    # Baris header / #EXTM3U
                    non_sma_lines.append(line)

            # Acak urutan SMA sebelum ditambahkan ke sumber no 2
            random.shuffle(sma_blocks)
            final_content_list[1] += "\n".join(sma_blocks) + "\n"
            channel_count[1] += len(sma_blocks)

            # Sisa non-SMA tetap di sumber ke 3
            lines = non_sma_lines
            print(f"📦 {len(sma_blocks)} channel kategori SMA dimodifikasi & dipindahkan ke sumber no 2")

        # Hitung jumlah channel di sumber saat ini
        channel_count[idx-1] += sum(1 for l in lines if l.startswith("http"))
        final_content_list[idx-1] += "\n".join(lines) + "\n"

        print(f"Sukses dari {url}")

    except Exception as e:
        print(f"Gagal download dari {url}: {e}")

# Gabungkan semua sumber jadi satu file, Live Event paling atas
final_content = "\n".join(live_event_blocks) + "\n" + "".join(final_content_list)

# Simpan ke file lokal
with open(MAIN_FILE, "w", encoding="utf-8") as f:
    f.write(final_content.strip())
print(f"✅ Playlist tersimpan: {MAIN_FILE}")

# Log jumlah channel per sumber
print("\n📊 Statistik Channel:")
for i, count in enumerate(channel_count, start=1):
    print(f"  Sumber {i}: {count} channel")
print(f"  ➡ Total SMA (Live Event) yang dipindahkan: {sma_moved_count} channel")

# Setup Git
os.system('git config --global user.email "actions@github.com"')
os.system('git config --global user.name "GitHub Actions"')
os.system(f'git add {MAIN_FILE}')

# Commit dengan safe exit code
commit_msg = f"Update Finalplay.m3u otomatis - {datetime.utcnow().isoformat()} UTC"
ret = os.system(f'git commit -m "{commit_msg}" || echo "Tidak ada perubahan"')
if ret == 0:
    os.system('git push')
    print("✅ Commit & push berhasil")
else:
    print("⚠️ Tidak ada perubahan baru, skip push")

# Cetak link commit terbaru
repo = os.getenv("GITHUB_REPOSITORY", "rafkichanel/my-iptv-playlist")
commit_hash = os.popen("git rev-parse HEAD").read().strip()
print(f"🔗 Lihat commit terbaru: https://github.com/{repo}/commit/{commit_hash}")
