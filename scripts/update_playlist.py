import os
import re
import asyncio
import aiohttp
from datetime import datetime

MAIN_FILE = "Finalplay.m3u"
DEAD_FILE = "DeadChannels.m3u"
SOURCES_FILE = "sources.txt"

FAST_TIMEOUT = 3
SLOW_TIMEOUT = 10

async def download_source(session, idx, url):
    try:
        print(f"📡 Mengunduh dari sumber {idx}: {url}")
        async with session.get(url, timeout=15) as resp:
            text = await resp.text()
            lines = text.splitlines()
            lines = [line for line in lines if "WHATSAPP" not in line.upper()]
            if idx == 3:
                lines = [line.replace("🔴", "") for line in lines]
            return lines
    except Exception as e:
        print(f"⚠️ Gagal ambil sumber {idx}: {e}")
        return []

async def check_channel(session, url):
    try:
        async with session.get(url, timeout=FAST_TIMEOUT) as resp:
            if resp.status == 200:
                return True
    except asyncio.TimeoutError:
        try:
            async with session.get(url, timeout=SLOW_TIMEOUT) as resp:
                if resp.status == 200:
                    return True
        except:
            return False
    except:
        return False
    return False

async def filter_channels(lines):
    alive_lines, dead_lines = [], []
    tasks, urls, chunks = [], [], []

    async with aiohttp.ClientSession() as session:
        for i in range(len(lines)):
            if lines[i].startswith("#EXTINF"):
                temp_chunk = [lines[i]]
            elif lines[i].startswith("http"):
                temp_chunk.append(lines[i])
                chunks.append(temp_chunk.copy())
                urls.append(lines[i])
                tasks.append(check_channel(session, lines[i]))

        total = len(tasks)
        results = []
        for i in range(0, total, 100):
            batch_tasks = tasks[i:i+100]
            batch_results = await asyncio.gather(*batch_tasks)
            results.extend(batch_results)
            print(f"⏳ Progress cek: {min(i+100, total)}/{total} channel selesai...")

        for idx, alive in enumerate(results):
            if alive:
                alive_lines.extend(chunks[idx])
            else:
                dead_lines.extend(chunks[idx])

    return alive_lines, dead_lines

async def main():
    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        sources = [line.strip() for line in f if line.strip()]

    async with aiohttp.ClientSession() as session:
        download_tasks = [download_source(session, idx+1, url) for idx, url in enumerate(sources)]
        sources_data = await asyncio.gather(*download_tasks)

    merged_lines = []
    for lines in sources_data:
        merged_lines.extend(lines)

    playlist = "\n".join(merged_lines)
    playlist = re.sub(r'group-title="SEDANG LIVE"', 'group-title="LIVE EVENT"', playlist, flags=re.IGNORECASE)
    lines = playlist.splitlines()

    print(f"🔍 Mengecek channel aktif dari total {len(lines)//2} channel approx...")
    alive_lines, dead_lines = await filter_channels(lines)

    print(f"✅ Channel aktif: {len(alive_lines)//2}")
    print(f"💀 Channel mati: {len(dead_lines)//2}")

    # Susun playlist aktif
    live_event, other_channels = [], []
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
    dead_playlist = ["#EXTM3U"] + dead_lines

    with open(MAIN_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_playlist))
    with open(DEAD_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(dead_playlist))

    print(f"📂 File aktif tersimpan: {MAIN_FILE}")
    print(f"📂 File mati tersimpan: {DEAD_FILE}")

    # Git push
    os.system('git config --global user.email "actions@github.com"')
    os.system('git config --global user.name "GitHub Actions"')
    os.system(f'git add {MAIN_FILE} {DEAD_FILE}')
    commit_msg = f"Update Finalplay.m3u & DeadChannels.m3u - {datetime.utcnow().isoformat()} UTC"
    os.system(f'git commit -m "{commit_msg}" || echo "Tidak ada perubahan"')
    os.system('git push')

if __name__ == "__main__":
    asyncio.run(main())
