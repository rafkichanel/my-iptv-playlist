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

for idx, url in enumerate(sources, start=1):
    try:
        print(f"Download dari {url}...")
        r = requests.get(url, timeout=15)
        r.raise_for_status()

        # Filter hapus WHATSAPP
        lines = [line for line in r.text.splitlines() if "WHATSAPP" not in line.upper()]

        if idx == 3:
            non_sma_lines = []
            sma_blocks = []
            current_block = []
            block_is_sma = False

            for line in lines:
                if line.startswith("#EXTINF"):
                    block_is_sma = "SMA" in line.upper()
                    if block_is_sma:
                        mod_line = re.sub(r"SMA", "SMX", line, flags=re.IGNORECASE)
                        mod_line = re.sub(r"[•●★◆]", "", mod_line)
                        mod_line = re.sub(r"(,.*\|)([123])(\|)",
                                          lambda m: m.group(1) + str(random.randint(1, 3)) + m.group(3),
                                          mod_line)
                        mod_line = re.sub(r"(?i)sedang\s*live", "LIVE EVENT", mod_line)
                        current_block = [mod_line]
                    else:
                        current_block = [re.sub(r"(?i)sedang\s*live", "LIVE EVENT", line)]

                elif line.startswith("http"):
                    current_block.append(line)
                    if block_is_sma:
                        sma_blocks.append("\n".join(current_block))
                        sma_moved_count += 1
                    else:
                        non_sma_lines.extend(current_block)

                else:
                    non_sma_lines.append(re.sub(r"(?i)sedang\s*live", "LIVE EVENT", line))

            random.shuffle(sma_blocks)
            final_content_list[1] += "\n".join(sma_blocks) + "\n"
            channel_count[1] += len(sma_blocks)

            lines = non_sma_lines
            print(f"📦 {len(sma_blocks)} channel kategori SMA dimodifikasi & dipindahkan ke sumber no 2")

        lines = [re.sub(r"(?i)sedang\s*live", "LIVE EVENT", l) for l in lines]
        channel_count[idx-1] += sum(1 for l in lines if l.startswith("http"))
        final_content_list[idx-1] += "\n".join(lines) + "\n"

        print(f"Sukses dari {url}")

    except Exception as e:
        print(f"Gagal download dari {url}: {e}")

final_content = "".join(final_content_list)
final_content = re.sub(r"(?i)sedang\s*live", "LIVE EVENT", final_content)

# === Pindahkan semua LIVE EVENT ke paling atas ===
lines = final_content.strip().split("\n")
live_event_blocks = []
other_blocks = []
current_block = []

for line in lines:
    current_block.append(line)
    if line.startswith("http"):
        block_text = "\n".join(current_block)
        if re.search(r"(?i)LIVE\s*EVENT", block_text):
            live_event_blocks.append(block_text)
        else:
            other_blocks.append(block_text)
        current_block = []

# Gabung ulang: LIVE EVENT di atas, lainnya di bawah
final_content = "\n".join(live_event_blocks + other_blocks)

with open(MAIN_FILE, "w", encoding="utf-8") as f:
    f.write(final_content.strip())

print(f"✅ Playlist tersimpan: {MAIN_FILE}")

print("\n📊 Statistik Channel:")
for i, count in enumerate(channel_count, start=1):
    print(f"  Sumber {i}: {count} channel")
print(f"  ➡ Total SMA yang dipindahkan: {sma_moved_count} channel")

os.system('git config --global user.email "actions@github.com"')
os.system('git config --global user.name "GitHub Actions"')
os.system(f'git add {MAIN_FILE}')

commit_msg = f"Update Finalplay.m3u otomatis - {datetime.utcnow().isoformat()} UTC"
ret = os.system(f'git commit -m "{commit_msg}" || echo "Tidak ada perubahan"')
if ret == 0:
    os.system('git push')
    print("✅ Commit & push berhasil")
else:
    print("⚠️ Tidak ada perubahan baru, skip push")

repo = os.getenv("GITHUB_REPOSITORY", "rafkichanel/my-iptv-playlist")
commit_hash = os.popen("git rev-parse HEAD").read().strip()
print(f"🔗 Lihat commit terbaru: https://github.com/{repo}/commit/{commit_hash}")
