import asyncio
import aiohttp
import os
from datetime import datetime

MAIN_FILE = "Finalplay.m3u"

# Baca daftar sumber dari sources.txt
with open("sources.txt", "r") as f:
    sources = [line.strip() for line in f if line.strip()]

async def is_channel_alive(session, url):
    """Cek channel aktif (HTTP 200) secara async."""
    try:
        async with session.head(url, timeout=5, allow_redirects=True) as resp:
            return resp.status == 200
    except:
        return False

async def process_source(session, source_url):
    """Download playlist & filter channel aktif."""
    result_lines = []
    try:
        print(f"Download dari {source_url}...")
        async with session.get(source_url, timeout=15) as r:
            text = await r.text()
        
        lines = text.splitlines()
        tasks = []
        channel_map = {}

        # Persiapkan list channel untuk dicek
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or "WHATSAPP" in line.upper():
                continue
            if not line.startswith("#"):
                url = line
                extinf = lines[i-1] if i > 0 and lines[i-1].startswith("#EXTINF:") else ""
                tasks.append((url, extinf))
        
        # Cek semua channel async
        coros = [check_channel(session, url, extinf) for url, extinf in tasks]
        results = await asyncio.gather(*coros)
        for r in results:
            if r:
                result_lines.extend(r)
        print(f"Selesai proses {source_url}, channel aktif: {len(result_lines)//2}")
    except Exception as e:
        print(f"Gagal download dari {source_url}: {e}")
    return result_lines

async def check_channel(session, url, extinf):
    alive = await is_channel_alive(session, url)
    if alive:
        return [extinf, url] if extinf else [url]
    return []

async def main():
    final_content = ["#EXTM3U"]
    async with aiohttp.ClientSession() as session:
        for src in sources:
            lines = await process_source(session, src)
            final_content.extend(lines)

    # Simpan ke file
    with open(MAIN_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_content))
    print(f"✅ Playlist tersimpan: {MAIN_FILE}")

    # Setup Git & push
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

if __name__ == "__main__":
    asyncio.run(main())
