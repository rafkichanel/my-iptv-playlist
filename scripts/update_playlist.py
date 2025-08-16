import requests
import os
import re
import asyncio
import aiohttp
from datetime import datetime

MAIN_FILE = "Finalplay.m3u"
SOURCES_FILE = "sources.txt"

# Timeout hybrid
FAST_TIMEOUT = 3
SLOW_TIMEOUT = 10

async def check_channel(session, url):
    """Cek apakah channel hidup."""
    try:
        # Cek cepat 3 detik
        async with session.get(url, timeout=FAST_TIMEOUT) as resp:
            if resp.status == 200:
                return True
    except asyncio.TimeoutError:
        # Kalau timeout cepat → coba 10 detik
        try:
            async with session.get(url, timeout=SLOW_TIMEOUT) as resp:
                if resp.status == 200:
                    return True
        except:
            return False
    except:
        return False
    return False

async def filter_dead_channels(lines):
    """Hapus channel mati dari playlist."""
    alive_lines = []
    current_chunk = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(len(lines)):
            if lines[i].startswith("#EXTINF"):
                current_chunk = [lines[i]]
            elif lines[i].startswith("http"):
                current_chunk.append(lines[i])
                tasks.append((current_chunk, check_channel(session, lines[i])))

        results = await asyncio.gather(*[t[1] for t in tasks])
        for idx, alive in enumerate(results):
            if alive:
                alive_lines.extend(tasks[idx][0])

    return alive_lines

# === Mulai proses unduh & filter ===
with open(SOURCES_FILE, "r", encoding="utf-8") as f:
    sources = [line.strip() for line in f if line.strip()]

merged_lines = []
for idx, url in enumerate(sources, start=1):
    try:
        print(f"📡 Mengunduh dari sumber {idx}: {url}")
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        lines = r.text.splitlines()

        # Filter tetap
        lines = [line for line in lines if "WHATSAPP" not in line.upper()]
        if idx == 3:
            lines = [line.replace("🔴", "") for line in lines]

        merged_lines.extend(lines)
    except Exception as e:
        print(f"⚠️ Gagal ambil sumber {idx}: {e}")

playlist = "\n".join(merged_lines)
playlist = re.sub(r'group-title="SEDANG LIVE"', 'group-title="LIVE EVENT"', playlist, flags=re.IGNORECASE)

lines = playlist.splitlines()
print(f"🔍 Mengecek channel aktif ({len(lines)//2} total approx)...")

# Cek channel aktif
alive_lines = asyncio.run(filter_dead_channels(lines))
print(f"✅ Channel aktif: {len(alive_lines)//2}")

# Pisahkan kategori LIVE EVENT
live_event = []
other_channels = []
current_group = None

for line in alive_lines:
    if line.startswith("#EXTINF"):
        match = re.search(r'group-title="([^"]+)"', line)
        if match:
            current_group = match.group(1)
        if current_group and current_group.upper() == "LIVE EVENT":
            live_event.append(line)
        else:
            other_channels.append(line)
    else:
        if current_group and current_group.upper() == "LIVE EVENT":
            live_event.append(line)
        else:
            other_channels.append(line)

final_playlist = ["#EXTM3U"] + live_event + other_channels

with open(MAIN_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(final_playlist))

print(f"✅ Playlist diperbarui ({len(alive_lines)//2} channel aktif) - {datetime.utcnow().isoformat()} UTC")

# Commit Git
os.system('git config --global user.email "actions@github.com"')
os.system('git config --global user.name "GitHub Actions"')
os.system(f'git add {MAIN_FILE}')
commit_msg = f"Update Finalplay.m3u otomatis - {datetime.utcnow().isoformat()} UTC"
os.system(f'git commit -m "{commit_msg}" || echo "Tidak ada perubahan"')
os.system('git push')
